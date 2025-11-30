# CLIP_SLOT API - Example Prompts for Testing

Use these prompts to validate the CLIP_SLOT tools end-to-end. Track and slot indices are 0-based. A subset of these prompts is also mirrored in `eval_prompts.csv` for automatic, binary success/failure evaluation.

## Discovery / State

- [EVAL] "Does track 0, slot 3 have a clip?"
- [EVAL] "Does track 1, slot 0 have a stop button?"
- "Show if track 2 slot 4 has a clip and stop button"

## Actions

- "Fire slot 0 on track 1"
- "Play/pause track 0 slot 2"

## Create / Delete Clip in Slot

- [EVAL] "Create an empty 4-bar clip in track 1, slot 0"
- "Create a 16-beat clip in track 0 slot 3"
- [EVAL] "Delete the clip in track 2, slot 1"

## Stop Button Control

- "Enable the stop button on track 0, slot 3"
- "Disable the stop button on track 1 slot 0"

## Duplicate Clip Between Slots

- [EVAL] "Duplicate the clip from track 0, slot 1 to track 2, slot 0"
- "Copy clip from track 1 slot 3 to track 1 slot 0"

## Multi-step Workflows

- [EVAL] "Create an 8-beat clip in track 0 slot 1, then fire it"
- "Duplicate clip from track 0 slot 0 to track 1 slot 0, then enable stop button on the target slot"
- "Create a 4-bar clip in track 2 slot 0, then rename the clip to 'Intro'" (expects CLIP API to follow after slot create)

## Error Handling / Edge Cases

- "Create a clip in track 0 slot 1" (missing length → should ask for beats)
- "Duplicate the clip from track 0 slot 1" (missing target → should ask for target track and slot)
- "Fire slot 12 on track 0" (invalid slot index → should report/handle gracefully)

## Notes

- Use CLIP_SLOT for container operations (create/delete/duplicate/fire, stop button, presence checks).
- After creating a clip in a slot, use CLIP API for clip content and properties (name, color, notes, loop, etc.).
