# DEVICE API - Example Prompts for Testing

Use these prompts to validate the DEVICE tools end-to-end. Track and device indices are 0-based.

## Device Discovery & Metadata

- "How many devices are on track 1?"
- "List device names on track 0"
- "What is the class name of device 0 on track 2?"
- "What type is device 1 on track 3?"

## Parameter Queries (Bulk)

- "List parameter names for device 0 on track 1"
- "Show parameter values for device 0 on track 1"
- "Show parameter min values for device 0 on track 1"
- "Which parameters on device 0 track 1 are quantized?"

## Parameter Queries (Individual)

- "What is parameter 3 value for device 0 on track 1?"
- "Show parameter 5 value string for device 0 on track 2"

## Parameter Control

- "Set parameter 2 on device 0 track 1 to 0.7"
- "Set multiple parameters on device 0 track 1 to 0.2,0.5,0.8"

## Multi-step Workflows

- "List device names on track 0, then show parameter names for device 0"
- "Get parameter values for device 0 on track 1, then set parameter 3 to 0.6"

## Error Handling / Edge Cases

- "Set parameter value for device 0" (missing parameter index → should prompt)
- "Set parameters value" (missing value list → should prompt)
- "Query device 3 on track 0" (invalid device index → should warn)

## Notes

- DEVICE API requires knowing track and device indices. Use TRACK API to list devices first if needed.
- Use parameter_value_string for human-readable values when needed (e.g., frequency).
