# Inline Java In YAML Pipelines

## Goal

Use Java source in YAML when you need strict type/classpath control or Java-only APIs.

## Supported source forms

From `JavaProcessorConfig` docs and engine tests:

- Full class with `public static Object process(Object input)`.
- Full class with instance `public Object process(Object input)` and public no-arg constructor.
- Lambda compatible with `Function<Object, Object>` (for example `input -> input.toString()`).
- Method reference (for example `java.lang.String::toUpperCase`).

## Processor shape

Inline class:

```yaml
processors:
  - java:
      source: |
        public class MyProc {
          public static Object process(Object input) {
            return String.valueOf(input).toUpperCase();
          }
        }
```

Source from URI:

```yaml
processors:
  - java:
      sourceUri: "classpath:/scripts/MyProc.java"
```

## Runtime behavior and troubleshooting
    
- Java source is compiled at startup, then `process(Object)` is invoked per record.
- Compilation/init errors fail startup (`Failed to prepare Java resource function`).
- Invocation failures are surfaced as `Script invocation failure: ...`.
- Returning `null` drops the record downstream.

## Environment requirements

- Runtime must include a JDK (not only JRE), because the plugin uses `ToolProvider.getSystemJavaCompiler()`.
- Any referenced classes must be present on runtime classpath.

## Common pitfalls

- Missing or wrong `process(Object)` signature.
- Non-static process method without an accessible no-arg constructor.
- Method reference pointing to incompatible or missing method.
- Incorrect classpath (e.g., user classes not added to it).
- 