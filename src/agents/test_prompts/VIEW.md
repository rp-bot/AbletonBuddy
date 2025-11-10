# VIEW API - Example Prompts for Testing

Use these prompts to validate the VIEW tools end-to-end. All indices are 0-based.

## Selection Queries

- "What track is currently selected?"
- "Which scene is selected right now?"
- "Show the selected clip's track and scene indices"
- "Which device is selected?"

## Selection Control

- "Select track 2"
- "Set the selected scene to scene 3"
- "Select clip track 1 slot 4"
- "Focus device 0 on track 2"

## Listening to Selection Changes

- "Start listening to selected track changes"
- "Start listening to selected scene"
- "Stop listening to selected track"
- "Stop listening to selected scene"

## Multi-step Workflows

- "Select track 1, then tell me which clip is selected"
- "Select clip track 0 slot 2, then launch it"
- "Focus device 0 on track 2, then increase the selected device's parameter 3" (requires DEVICE API afterwards)
- "Start listening to selected track, then change to track 3"

## Error Handling / Edge Cases

- "Select track" (missing index → should ask for track number)
- "Select clip 3" (ambiguous format → should prompt for track/scene indices)
- "Start listening to selected clip" (unsupported listen target → should respond appropriately)

## Notes

- VIEW handles UI focus only. Use TRACK/CLIP/SCENE/DEVICE APIs for actual edits once selection is set.
- Track, scene, clip, and device indices are 0-based.
- combine VIEW queries with other APIs to perform actions on the selected items.
