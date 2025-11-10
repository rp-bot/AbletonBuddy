# TRACK API - Example Prompts for Testing

Use these prompts to validate the TRACK tools end-to-end. Track indices are 0-based.

## Mix Controls

- "Mute track 1"
- "Solo track 0"
- "Set track 2 volume to 0.75"
- "Pan track 3 hard left"
- "Set send A on track 1 to 0.5"

## Track Properties & State

- "What is the name of track 0?"
- "Rename track 1 to 'Bass'"
- "What color is track 2?"
- "Is track 3 armed?"
- "What is the output meter level of track 0?"

## Routing

- "List available input routing channels for track 1"
- "Set track 0 input routing channel to '1/2'"
- "Set track 2 monitoring state to IN"

## Devices & Clips

- "How many devices are on track 1?"
- "List device names on track 0"
- "List clip names on track 2"
- "List arrangement clip lengths on track 3"

## Clip Control on Track

- "Stop all clips on track 0"

## Track State Queries

- "What is the playing slot index of track 1?"
- "Is track 2 visible?"
- "Can track 3 be armed?"

## Multi-step Workflows

- "Rename track 0 to 'Drums' and set its color to red"
- "List devices on track 1, then set the track volume to 0.8"
- "Get clip names on track 0 and stop all clips"

## Error Handling / Edge Cases

- "Mute track" (missing index → should ask for track number)
- "Set send on track 1" (missing send and value → should prompt)
- "Set track 10 volume to 0.5" (invalid track index → should report)

## Notes

- TRACK API handles per-track operations. Use SONG API for global track management (create/delete/duplicate) and CLIP/DEVICE APIs for specific clip/device operations.
