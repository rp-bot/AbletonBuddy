# NATURAL LANGUAGE PROMPTS - Producer Workflows

These are natural, conversational prompts that producers would actually use when working in Ableton Live. They typically involve multiple steps across different APIs and represent real-world workflows.

## Track Setup & Organization

- "Create a new MIDI track for drums, set the volume to 0.8, and arm it for recording"
- "Make a new audio track, name it 'Vocals', and pan it slightly to the right"
- "Set up track 1 for bass - mute it, set the volume to 0.7, and show me what devices are on it"
- "Rename track 0 to 'Kick' and set its color to red"
- "Create a new track, duplicate scene 1, and then launch the new scene"
- "Show me all the tracks and tell me which ones are currently playing clips"

## Recording & Loop Setup

- "Set the tempo to 128 BPM, enable looping from bar 4 for 8 bars, and start recording"
- "Create a 4-bar loop starting at bar 8, then start playback"
- "Set up a loop for 16 bars, arm track 1, and trigger session record"
- "Start recording, then after 8 bars jump forward 4 beats"
- "Set the loop to 4 bars, start playing, and show me the current song position"

## Clip Workflows

- "Create a new 8-beat clip on track 0, launch it, and tell me if it's playing"
- "Take the clip from track 1 slot 0, copy it to track 2 slot 0, then launch it"
- "Find all the clips on the bass track and stop them"
- "Launch clip 0 on track 1, then show me its loop settings"
- "Create a clip in track 0 slot 2, rename it to 'Intro', and set it to loop"
- "Stop all clips on track 3, then show me what clips are available on that track"
- "Launch the clip on track 1, then adjust its gain to 1.2"

## Mixing & Effects

- "Turn down track 2 to 0.6, add some reverb by setting send A to 0.4"
- "Mute track 1, solo track 0, and show me the output levels"
- "Pan the vocals hard left and the guitar hard right"
- "Make the kick louder - set track 0 volume to 0.9 and show me the meter"
- "Turn up send B on track 3 to 0.5, then check the track volume"
- "Mute everything except track 0 and 1, then start playback"

## Scene Management

- "Create a new scene, name it 'Chorus', set the tempo to 130 BPM, and fire it"
- "Launch scene 2, then tell me what tempo it's set to"
- "Duplicate scene 1, rename it to 'Breakdown', and set it to 110 BPM"
- "Fire scene 0, then show me which tracks are playing clips"
- "Set scene 3 tempo to 128, enable tempo override, then launch it"
- "Create a scene, set its color to blue, and trigger it"

## Tempo & Timing

- "Set the tempo to 120, enable the metronome, and start playing"
- "What's the current tempo? Then set it to 128 BPM"
- "Tap in a tempo, then set up a 4-bar loop"
- "Change the time signature to 7/8, then start playback"
- "Set the tempo to 140, jump forward 8 beats, and continue playing"

## MIDI & Clip Editing

- "Create a new MIDI clip on track 1, add a C4 note at beat 0, then launch it"
- "Show me all the notes in clip 0 on track 1, then add a chord"
- "Launch clip 0 on track 2, then show me what MIDI notes are in it"
- "Create an 8-beat MIDI clip, add a kick pattern, then loop it"
- "Remove all notes between beats 4 and 8 in clip 0 on track 1"

## Device Control

- "Show me what devices are on track 1, then set parameter 3 on device 0 to 0.7"
- "List all the parameters for device 0 on track 2, then adjust the first one"
- "Find device 0 on track 1, show its parameter values, then tweak parameter 2"
- "What's the name of device 0 on track 3? Then set one of its parameters"

## Complex Multi-Step Workflows

- "Set up a new track for bass, create a 4-bar clip, set the tempo to 128, and start playing"
- "Mute track 2, create a new scene called 'Verse 2', set it to 120 BPM, and launch it"
- "Stop all clips, set the loop to 8 bars starting at bar 4, then start recording"
- "Create a MIDI track, add a clip, set it to loop, launch it, and show me the notes"
- "Take the kick from track 0, copy it to track 1, then mute the original track"
- "Set up track 1: rename it to 'Lead', set volume to 0.8, pan right, and show me its clips"
- "Create a new scene, duplicate it, rename both scenes, then fire the first one"
- "Arm track 1, set the loop to 4 bars, start recording, then after it loops show me the clip"
- "Mute everything, solo track 0, launch scene 1, then gradually unmute other tracks"
- "Set tempo to 128, create a new scene, set scene tempo to 130 with override, then fire it"
- "Create a clip on track 0, rename it, set its gain, launch it, then adjust the track volume"
- "Stop all clips, jump to bar 8, set up a loop, then start playback"
- "Show me all tracks, find the one with the most devices, then list those devices"
- "Create a new audio track, set input routing, arm it, then start recording"
- "Launch scene 2, wait a moment, then show me which clips are playing on each track"

## Performance & Live Use

- "Start playing, then jump forward 4 beats every 8 bars"
- "Fire scene 1, then immediately fire scene 2"
- "Stop everything, reset to the beginning, then start fresh"
- "Create a loop, start playing, then gradually increase the tempo"
- "Set up a 16-bar loop, start recording, then stop after one pass"

## Discovery & Exploration

- "Show me what's in the project - how many tracks, scenes, and what's currently playing"
- "List all the clips on track 1, then tell me which ones are currently playing"
- "What devices are on track 0? Show me their names and types"
- "Show me all the scenes and their tempos"
- "What's the current state - tempo, loop settings, and which tracks are armed?"

## Notes

- These prompts represent natural language that producers would use in conversation
- They often require the agent to infer multiple steps and combine operations across APIs
- The agent should handle ambiguity gracefully and ask for clarification when needed
- Many prompts require discovering current state before making changes
- Real-world workflows often mix querying, control, and discovery operations
