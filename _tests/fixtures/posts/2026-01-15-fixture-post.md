---
title: "Fixture post for tests"
description: "A post that exists only in the test suite's temporary builds."
tags: [kotlin, testing]
---

This post is test content. It is copied into a temporary build by
`_tests/conftest.py` and never into the real `_posts/`.

## A section

Some text with `inline code`.

```kotlin
// fixture/Example.kt
fun greet(name: String) = "Hello, $name"
```
