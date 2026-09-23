---
published: false # demo only, never publish (see AGENTS.md)
title: "Sharing one Ktor client between Android and iOS"
description: "Set up a single Ktor HttpClient in commonMain, pick the engine per platform, and test it with MockEngine on both targets."
tags: [kmp, kotlin, testing]
---

> **Sample post:** this article shows the blog's look and feel. The code follows Ktor 3 APIs, but it wasn't compiled for this page.
{: .note}

If your Android and iOS apps each have their own networking layer, every timeout, header and JSON quirk gets fixed twice. This post moves the HTTP client into Kotlin Multiplatform (KMP) shared code, so both apps use one client, one set of models and one test suite. It's for teams that already share some code and want networking to be next.

## The problem

A typical setup before KMP looks like this: Retrofit on Android, `URLSession` on iOS, and two copies of every response model. The copies drift. One app gets a retry policy, the other doesn't. A new field breaks parsing on one platform only.

The fix isn't to share *everything*. The HTTP engine should stay native, because each platform's stack handles proxies, certificates and background sessions best. What's worth sharing is everything on top of the engine:

- the client configuration: base URL, timeouts, JSON settings
- the API calls and response models
- the tests

## Setup

**Tested with:** Kotlin 2.2, Ktor 3.3, kotlinx.coroutines 1.10

The version catalog declares the core client, the JSON plugin, one engine per platform and the mock engine for tests:

```toml
# gradle/libs.versions.toml
[versions]
kotlin = "2.2.20"
ktor = "3.3.0"
coroutines = "1.10.2"

[libraries]
ktor-client-core = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
ktor-client-content-negotiation = { module = "io.ktor:ktor-client-content-negotiation", version.ref = "ktor" }
ktor-serialization-kotlinx-json = { module = "io.ktor:ktor-serialization-kotlinx-json", version.ref = "ktor" }
ktor-client-okhttp = { module = "io.ktor:ktor-client-okhttp", version.ref = "ktor" }
ktor-client-darwin = { module = "io.ktor:ktor-client-darwin", version.ref = "ktor" }
ktor-client-mock = { module = "io.ktor:ktor-client-mock", version.ref = "ktor" }
kotlinx-coroutines-test = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-test", version.ref = "coroutines" }

[plugins]
kotlin-multiplatform = { id = "org.jetbrains.kotlin.multiplatform", version.ref = "kotlin" }
kotlin-serialization = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
```

Each source set then gets only what it needs. The engines stay in the platform source sets, so iOS never pulls in OkHttp:

```kotlin
// shared/build.gradle.kts
kotlin {
    androidTarget()
    iosArm64()
    iosSimulatorArm64()

    sourceSets {
        commonMain.dependencies {
            implementation(libs.ktor.client.core)
            implementation(libs.ktor.client.content.negotiation)
            implementation(libs.ktor.serialization.kotlinx.json)
        }
        androidMain.dependencies {
            implementation(libs.ktor.client.okhttp)
        }
        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
        }
        commonTest.dependencies {
            implementation(kotlin("test"))
            implementation(libs.ktor.client.mock)
            implementation(libs.kotlinx.coroutines.test)
        }
    }
}
```

Here's how the pieces fit together:

![Diagram: commonMain holds ItemsApi and createHttpClient; androidMain provides the OkHttp engine and iosMain the Darwin engine](/assets/images/posts/sharing-ktor-client-kmp/source-sets.svg)

## One client in commonMain

The client factory takes an engine as a parameter. That one decision makes the rest of the post work: production code passes the platform engine, and tests pass a fake.

```kotlin
// shared/src/commonMain/kotlin/lt/setkus/api/HttpClientFactory.kt
fun createHttpClient(
    engine: HttpClientEngine = platformEngine(),
): HttpClient = HttpClient(engine) {
    expectSuccess = true
    install(ContentNegotiation) {
        json(Json { ignoreUnknownKeys = true })
    }
    install(HttpTimeout) {
        requestTimeoutMillis = 15_000
    }
    defaultRequest {
        url("https://api.example.com/v1/")
    }
}
```

Three settings do most of the work:

1. `expectSuccess = true` turns 4xx and 5xx responses into exceptions, so a failed call can't silently decode an error page.
2. `ignoreUnknownKeys` keeps old app versions working when the backend adds a field.
3. `defaultRequest` sets the base URL once. Every call after that uses a relative path.

### Picking the engine per platform

The factory's default comes from an `expect` function, which each platform implements with its own engine:

```kotlin
// shared/src/commonMain/kotlin/lt/setkus/api/Engine.kt
expect fun platformEngine(): HttpClientEngine
```

On Android that's OkHttp, and on iOS it's Darwin, which wraps `NSURLSession`:

```kotlin
// shared/src/androidMain/kotlin/lt/setkus/api/Engine.android.kt
actual fun platformEngine(): HttpClientEngine = OkHttp.create()

// shared/src/iosMain/kotlin/lt/setkus/api/Engine.ios.kt
actual fun platformEngine(): HttpClientEngine = Darwin.create()
```

| Platform | Engine | Artifact |
|---|---|---|
| Android | OkHttp | `ktor-client-okhttp` |
| iOS | Darwin (`NSURLSession`) | `ktor-client-darwin` |
| Tests | MockEngine | `ktor-client-mock` |

## The API layer

With the client configured, the API itself is small. The response model is annotated once and used by both apps:

```kotlin
// shared/src/commonMain/kotlin/lt/setkus/api/ItemsApi.kt
@Serializable
data class Item(val id: String, val title: String)

class ItemsApi(private val client: HttpClient) {
    suspend fun items(): List<Item> = client.get("items").body()

    suspend fun item(id: String): Item = client.get("items/$id").body()
}
```

> **Warning:** Write `get("items")`, not `get("/items")`. A leading slash makes the path absolute and drops the `/v1/` from the base URL.
{: .warning}

## Testing with MockEngine

Because the engine is a parameter, a test can hand the client a `MockEngine` and check both the request and the parsing. The test lives in `commonTest`, so it runs on every target:

```kotlin
// shared/src/commonTest/kotlin/lt/setkus/api/ItemsApiTest.kt
class ItemsApiTest {
    private val jsonHeaders =
        headersOf(HttpHeaders.ContentType, "application/json")

    @Test
    fun parsesItemsAndIgnoresUnknownFields() = runTest {
        val engine = MockEngine { request ->
            assertEquals("/v1/items", request.url.encodedPath)
            respond(ITEMS_JSON, HttpStatusCode.OK, jsonHeaders)
        }
        val api = ItemsApi(createHttpClient(engine))

        assertEquals(listOf(Item("1", "First")), api.items())
    }
}

private const val ITEMS_JSON =
    """[{"id": "1", "title": "First", "addedLater": true}]"""
```

Run it on the JVM and on the iOS simulator:

```bash
./gradlew :shared:testDebugUnitTest :shared:iosSimulatorArm64Test
```

## Running it in CI

The iOS tests need macOS, so the workflow runs on a macOS runner. The `concurrency` group cancels outdated runs when you push again:

{% raw %}
```yaml
# .github/workflows/shared-tests.yml
name: Shared tests
on: [push, pull_request]
concurrency:
  group: shared-tests-${{ github.ref }}
  cancel-in-progress: true
jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 21
      - uses: gradle/actions/setup-gradle@v4
      - run: >
          ./gradlew :shared:testDebugUnitTest
          :shared:iosSimulatorArm64Test
```
{% endraw %}

## Moving the Android app over

On Android the switch is mostly deleting code. The app depends on the shared module instead of Retrofit:

```diff
 // androidApp/build.gradle.kts
 dependencies {
-    implementation(libs.retrofit)
-    implementation(libs.retrofit.converter.kotlinx.serialization)
+    implementation(project(":shared"))
 }
```

## Pitfalls

- **One client per app, not per request.** Each `HttpClient` has its own connection pool. Create it once, share it, and call `close()` only when the app no longer needs it.
- **App Transport Security on iOS.** Darwin goes through `NSURLSession`, so plain `http://` URLs fail unless `Info.plist` allows them. That's easy to miss when testing against a local server.
- **Exceptions differ by engine.** Timeouts and connection errors surface as engine-specific exceptions. Catch Ktor's `HttpRequestTimeoutException` and `ResponseException` in shared code, not OkHttp's or Foundation's types.

## Takeaways

- Share the client configuration, API calls and models. Keep the engine native.
- Pass the engine in as a parameter. It's what makes the client testable from `commonTest`.
- Run the shared tests on both targets in CI, because a JVM-only run misses iOS-specific failures.

For more detail, see Ktor's docs on [client engines](https://ktor.io/docs/client-engines.html) and [testing with MockEngine](https://ktor.io/docs/client-testing.html).
