# SCENE API - Example Prompts for Testing

Use these prompts to validate the SCENE tools end-to-end. Scene indices are 0-based.

## Triggering Scenes

- "Launch scene 0"
- "Fire scene 2"
- "Trigger the currently selected scene"
- "Fire scene 1 and select the next scene"

## Scene Properties

- "What is the name of scene 3?"
- "Rename scene 1 to 'Chorus'"
- "What color is scene 0?"
- "Set scene 2 color to blue"

## Scene Tempo & Time Signature

- "What tempo is scene 1 set to?"
- "Set scene 0 tempo to 120 BPM"
- "Is tempo override enabled for scene 2?"
- "Enable tempo override for scene 2"

- "What time signature is scene 3 using?"
- "Set scene 1 time signature to 5/4"
- "Enable time signature override for scene 1"

## Scene State

- "Is scene 0 empty?"
- "Is scene 2 triggered?"

## Multi-step Workflows

- "Set scene 0 tempo to 128 BPM and launch it"
- "Rename scene 2 to 'Breakdown', set tempo to 110 BPM, then fire it"

## Error Handling / Edge Cases

- "Launch scene" (missing index → should ask)
- "Set scene tempo" (missing scene/tempo → should prompt)
- "Set time signature for scene 10" (invalid index → should warn)

## Notes

- SCENE API acts on existing scenes. Use SONG API for scene creation/deletion/duplication.
