# Rate-Limited Generator Pipeline

## Goal

Generate deterministic synthetic records at controlled TPS and stop automatically after a max count.

## YAML implementation

```yaml
version: 1
name: "generator"

source:
  generate:
    tps: "10"
    eventsPerBatch: 1
    maxEventCount: 10
    generator: |
      function process(input) {
        return "Hello World " + input + "\n";
      }

sink:
  stdout: {}
```

## Notes

- `maxEventCount` lets the pipeline end without manual cancellation.
- `eventsPerBatch` controls batch size independent of TPS.
- Keep output deterministic for predictable tests.
