# SONG API - Example Prompts for Testing

Use these prompts to validate the SONG tools end-to-end.

## Transport & Playback

- "Start playback"
- "Stop the song"
- "Continue playing"
- "Jump forward 8 beats"
- "Jump to the next cue point"

## Tempo & Time Signature

- "Set the tempo to 128 BPM"
- "Tap tempo"
- "Set the time signature to 7/8"
- "What is the current song tempo?"
- "What is the time signature?"

## Looping & Position

- "Enable loop from bar 4 for 8 bars"
- "Disable looping"
- "Set loop start to 16 beats and length to 8"
- "What is the current song position?"

## Recording & Overdub

- "Start session recording"
- "Stop session recording"
- "Enable arrangement overdub"
- "Disable arrangement overdub"

## Undo / Redo / Navigation

- "Undo the last action"
- "Redo the last action"
- "Go back to arrangement"

## Track / Scene Management

- "Create a new MIDI track"
- "Create an audio track"
- "Duplicate scene 2"
- "Delete track 3"

## Quantization / Groove / Nudge

- "Set clip trigger quantization to 1 bar"
- "Set MIDI recording quantization to 1/16"
- "Set groove amount to 0.3"
- "Nudge the song down"

## Stop Commands

- "Stop all clips"
- "Trigger session record"

## Multi-step Workflows

- "Set tempo to 120 BPM, enable loop from bar 5 for 4 bars, then start playback"
- "Create a new scene and duplicate it"

## Error Handling / Edge Cases

- "Set tempo" (missing value → should ask for BPM)
- "Jump by" (missing distance → should ask for beats)
- "Create track" (missing track type → should ask)

## Notes

- SONG API controls global session state. Use TRACK/CLIP/SCENE APIs for per-object operations.
