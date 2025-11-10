# APPLICATION API - Example Prompts for Testing

Use these prompts to validate the Application API tools end-to-end.

## Connectivity / Health Checks

- "Run a connection test"
- "Is AbletonOSC responding?"
- "Check the AbletonOSC connection"

## Metadata

- "What Live version is running?"
- "Tell me the Ableton Live major/minor version"

## Log Level Management

- "What log level is AbletonOSC using?"
- "Set the AbletonOSC log level to debug"
- "Change the AbletonOSC log level to warning"

## Server Maintenance / Development

- "Reload the AbletonOSC server"
- "Restart the AbletonOSC API" (maps to reload)

## Multi-step Workflows

- "Run a connection test, then tell me the Live version"
- "Set the log level to info and confirm it changed"
- "Check the current log level, set it to error, then run a connection test"

## Error Handling / Edge Cases

- "Set log level" (missing value → should ask for level)
- "Set log level to verbose" (unsupported level → should warn)

## Notes

- APPLICATION API is for diagnostics and AbletonOSC configuration, not musical operations.
- For transport, track, clip, or device actions, use the corresponding APIs.
