# Syslog Sink

Forward records to remote syslog endpoints using RFC3164 format. Input type is CharSequence.

Compile dependency: volt-stream-plugin-syslog-api

## Java Example

```java
import org.voltdb.stream.plugin.syslog.api.SyslogSinkConfigBuilder;

stream.terminateWithSink(SyslogSinkConfigBuilder.builder()
    .withAddressHost("syslog.example.com")
    .withAddressPort(514)
);
```

## YAML Example

```yaml
sink:
  syslog:
    address: "syslog.example.com:514"
    message:
      facility: USER
      severity: NOTICE
      hostname: "my-host"
      tag: "my-app"
```

## Properties
- HostAndPort address: Syslog server address, default port 514, required.
- SyslogRFC3164Message message: RFC3164 message settings.
  - facility: Syslog facility (e.g. USER, ALERT).
  - severity: Syslog severity (e.g. DEBUG, NOTICE).
  - hostname: Originating hostname.
  - tag: Application tag.
