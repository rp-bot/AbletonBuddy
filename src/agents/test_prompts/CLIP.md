# CLIP API - Example Prompts for Testing

Use these prompts to validate the CLIP tools end-to-end. Track and clip indices are 0-based. A subset of these prompts is also mirrored in `eval_prompts.csv` for automatic, binary success/failure evaluation.

## Playback & Looping

- [EVAL] "Launch clip 0 on track 1"
- "Stop clip 2 on track 0"
- "Duplicate the loop for clip 1 on track 3"
- "Set clip 0 on track 0 loop start to 8 beats"
- [EVAL] "Set clip 0 on track 0 loop length to 4 beats"

## Clip Properties

- "What is the name of clip 0 on track 1?"
- [EVAL] "Rename clip 1 on track 0 to 'Intro'"
- "What is the length of clip 2 on track 3?"
- "Set clip 0 on track 0 gain to 1.2"
- "What is the file path for clip 1 on track 2?"

## Clip State & Type

- "Is clip 0 on track 1 playing?"
- "Is clip 2 on track 3 recording?"
- "Is clip 0 on track 0 an audio clip?"
- "Is clip 1 on track 2 a MIDI clip?"

## Pitch & Markers

- "Set clip 0 on track 1 pitch coarse to +2"
- "Set clip 0 on track 1 pitch fine to -30"
- "Set clip 2 on track 0 start marker to 16 beats"
- "Set clip 2 on track 0 end marker to 24 beats"

## Loops & Warping

- "What is the loop start for clip 1 on track 0?"
- "Set clip 1 on track 0 loop end to 32 beats"
- [EVAL] "Enable warping for clip 0 on track 2"
- "What is the warping state of clip 2 on track 3?"

## MIDI Notes

- "Show all notes in clip 0 on track 1"
- "Show notes in clip 0 on track 1 between C3 and C5"
- [EVAL] "Add note C4 at beat 0 duration 1 to clip 0 on track 1"
- "Remove notes between beats 4 and 8 in clip 0 on track 1"

## Multi-step Workflows

- "Launch clip 0 on track 1 and report its loop settings"
- "Query notes in clip 0 on track 1, then add a chord"
- "Set pitch coarse to +1 and loop end to 16 beats for clip 2 on track 0"

## Error Handling / Edge Cases

- "Launch clip" (missing track/clip indices → should ask)
- "Add note to clip 0" (missing pitch/time/duration → should prompt)
- "Set loop start for clip 5 on track 0" (invalid clip index → should warn)

## Notes

- CLIP API acts on a specific track/clip pair. Use TRACK API to discover clip indices or CLIP_SLOT API to create slots.
