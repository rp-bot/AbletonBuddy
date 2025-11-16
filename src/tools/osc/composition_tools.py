"""
Marvin-compatible tools for generating musically coherent MIDI content.
These tools create MIDI clips with melodies, chord progressions, and drum patterns.
"""

from __future__ import annotations

from typing import Optional, Annotated, List, Tuple
from pydantic import Field
import marvin
import asyncio
import concurrent.futures

from tools.osc.clip_slot_tools import control_clip_slot
from tools.osc.clip_tools import control_clip


def _run_async_safe(coro):
    """
    Safely run an async coroutine, handling both sync and async contexts.
    If an event loop is already running, use a thread pool executor.
    Otherwise, create a new event loop with asyncio.run().
    """
    try:
        # Check if there's a running event loop
        loop = asyncio.get_running_loop()
        # Event loop is already running - use a thread pool to run the coroutine
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No event loop running - safe to use asyncio.run()
        return asyncio.run(coro)


def _parse_scale_key(scale_key: str) -> Tuple[int, str]:
    """
    Parse scale/key string (e.g., "C major", "A minor") into root note and mode.
    Returns (root_note, mode) where root_note is MIDI note number and mode is "major" or "minor".
    """
    scale_key = scale_key.strip().lower()
    parts = scale_key.split()
    
    if len(parts) < 2:
        # Default to major if not specified
        root = parts[0] if parts else "c"
        mode = "major"
    else:
        root = parts[0]
        mode = parts[1]
    
    # Map note names to MIDI numbers (C4 = 60)
    note_map = {
        "c": 60, "c#": 61, "db": 61, "d": 62, "d#": 63, "eb": 63,
        "e": 64, "f": 65, "f#": 66, "gb": 66, "g": 67, "g#": 68,
        "ab": 68, "a": 69, "a#": 70, "bb": 70, "b": 71
    }
    
    root_note = note_map.get(root, 60)  # Default to C
    return (root_note, mode)


def _generate_melody_notes(
    scale_key: str, length_bars: int, style: str, beats_per_bar: int = 4
) -> List[Tuple[int, float, float, int, bool]]:
    """
    Generate musically coherent melody notes.
    Returns list of (pitch, start_time, duration, velocity, mute) tuples.
    Uses AI to generate musically coherent content.
    """
    # Calculate total length in beats
    total_beats = length_bars * beats_per_bar
    
    # Use AI to generate melody
    prompt = f"""Generate a musically coherent melody in {scale_key} style, {length_bars} bars long.
    
    Requirements:
    - Key/Scale: {scale_key}
    - Length: {length_bars} bars ({total_beats} beats at 4/4 time)
    - Style: {style}
    - Use notes from the {scale_key} scale
    - Create a melodic line with good phrasing and musical interest
    - Include some rhythmic variation
    - Use appropriate note durations (quarter notes, eighth notes, etc.)
    - Start time should be in beats (0.0 to {total_beats})
    - Duration should be in beats (typically 0.25 to 2.0)
    - Velocity should be 60-100 for musical expression
    - Return as a list of tuples: (pitch_midi, start_time_beats, duration_beats, velocity, mute)
    - Pitch should be MIDI note numbers (C4 = 60)
    - Make it musically coherent and stylistically appropriate
    
    Return only the list of tuples, no explanation."""
    
    try:
        notes = _run_async_safe(
            marvin.run_async(
                prompt,
                result_type=List[Tuple[int, float, float, int, bool]],
            )
        )
        return notes if notes else []
    except Exception as e:
        # Fallback: simple scale-based melody
        root_note, mode = _parse_scale_key(scale_key)
        scale_notes = _get_scale_notes(root_note, mode)
        notes = []
        beat = 0.0
        for i in range(length_bars * 4):  # Quarter notes
            pitch = scale_notes[i % len(scale_notes)]
            notes.append((pitch, beat, 0.5, 80, False))
            beat += 0.5
        return notes


def _generate_chord_progression_notes(
    scale_key: str, length_bars: int, style: str, progression_type: Optional[str] = None,
    beats_per_bar: int = 4
) -> List[Tuple[int, float, float, int, bool]]:
    """
    Generate musically coherent chord progression notes.
    Returns list of (pitch, start_time, duration, velocity, mute) tuples.
    """
    total_beats = length_bars * beats_per_bar
    
    prompt = f"""Generate a musically coherent chord progression in {scale_key} style, {length_bars} bars long.
    
    Requirements:
    - Key/Scale: {scale_key}
    - Length: {length_bars} bars ({total_beats} beats at 4/4 time)
    - Style: {style}
    - Progression type: {progression_type if progression_type else 'automatic based on style'}
    - Create chord voicings appropriate for the style
    - Each chord should be 1-2 bars long
    - Use 3-4 note chord voicings (triads or 7ths)
    - Stack notes vertically (same start_time for chord tones)
    - Start time should be in beats (0.0 to {total_beats})
    - Duration should be in beats (typically 1.0 to 4.0 for chords)
    - Velocity should be 70-100
    - Return as a list of tuples: (pitch_midi, start_time_beats, duration_beats, velocity, mute)
    - Pitch should be MIDI note numbers (C4 = 60)
    - Make it musically coherent with proper voice leading
    
    Return only the list of tuples, no explanation."""
    
    try:
        notes = _run_async_safe(
            marvin.run_async(
                prompt,
                result_type=List[Tuple[int, float, float, int, bool]],
            )
        )
        return notes if notes else []
    except Exception as e:
        # Fallback: simple triads
        root_note, mode = _parse_scale_key(scale_key)
        chords = _get_chord_progression(root_note, mode, length_bars)
        notes = []
        for i, chord in enumerate(chords):
            start_time = i * beats_per_bar
            for pitch in chord:
                notes.append((pitch, start_time, beats_per_bar, 80, False))
        return notes


def _generate_drum_pattern_notes(
    length_bars: int, style: str, beats_per_bar: int = 4
) -> List[Tuple[int, float, float, int, bool]]:
    """
    Generate musically coherent drum pattern notes.
    Returns list of (pitch, start_time, duration, velocity, mute) tuples.
    Uses standard MIDI drum mapping (kick=36, snare=38, hihat=42, etc.)
    """
    total_beats = length_bars * beats_per_bar
    
    # Standard MIDI drum notes
    drum_map = {
        "kick": 36, "snare": 38, "hihat_closed": 42, "hihat_open": 46,
        "crash": 49, "ride": 51, "tom_low": 41, "tom_mid": 47, "tom_high": 48
    }
    
    prompt = f"""Generate a musically coherent {style} drum pattern, {length_bars} bars long.
    
    Requirements:
    - Length: {length_bars} bars ({total_beats} beats at 4/4 time)
    - Style: {style}
    - Use standard MIDI drum notes:
      - Kick drum: 36
      - Snare drum: 38
      - Closed hihat: 42
      - Open hihat: 46
      - Crash: 49
      - Ride: 51
      - Toms: 41 (low), 47 (mid), 48 (high)
    - Create a stylistically appropriate pattern
    - Include kick on strong beats, snare on backbeats (typically beats 2 and 4)
    - Add hihat patterns appropriate for the style
    - Use appropriate velocities (kick/snare: 80-100, hihat: 60-80)
    - Start time should be in beats (0.0 to {total_beats})
    - Duration should be short for drums (typically 0.1 to 0.25 beats)
    - Return as a list of tuples: (pitch_midi, start_time_beats, duration_beats, velocity, mute)
    - Make it musically coherent and rhythmically interesting
    
    Return only the list of tuples, no explanation."""
    
    try:
        notes = _run_async_safe(
            marvin.run_async(
                prompt,
                result_type=List[Tuple[int, float, float, int, bool]],
            )
        )
        return notes if notes else []
    except Exception as e:
        # Fallback: simple 4/4 pattern
        notes = []
        for bar in range(length_bars):
            # Kick on 1 and 3
            notes.append((36, bar * 4 + 0, 0.1, 90, False))  # Kick
            notes.append((36, bar * 4 + 2, 0.1, 90, False))  # Kick
            # Snare on 2 and 4
            notes.append((38, bar * 4 + 1, 0.1, 85, False))  # Snare
            notes.append((38, bar * 4 + 3, 0.1, 85, False))  # Snare
            # Hihat on every beat
            for beat in range(4):
                notes.append((42, bar * 4 + beat, 0.1, 70, False))  # Hihat
        return notes


def _get_scale_notes(root_note: int, mode: str) -> List[int]:
    """Get scale notes for a given root and mode."""
    if mode == "major":
        intervals = [0, 2, 4, 5, 7, 9, 11]
    else:  # minor
        intervals = [0, 2, 3, 5, 7, 8, 10]
    return [root_note + interval for interval in intervals]


def _get_chord_progression(root_note: int, mode: str, length_bars: int) -> List[List[int]]:
    """Get a simple chord progression."""
    scale_notes = _get_scale_notes(root_note, mode)
    if mode == "major":
        # I, IV, V, vi progression
        chords = [
            [scale_notes[0], scale_notes[2], scale_notes[4]],  # I
            [scale_notes[3], scale_notes[5], scale_notes[0]],  # IV
            [scale_notes[4], scale_notes[6], scale_notes[1]],  # V
            [scale_notes[5], scale_notes[0], scale_notes[2]],  # vi
        ]
    else:  # minor
        # i, iv, v, VI progression
        chords = [
            [scale_notes[0], scale_notes[2], scale_notes[4]],  # i
            [scale_notes[3], scale_notes[5], scale_notes[0]],  # iv
            [scale_notes[4], scale_notes[6], scale_notes[1]],  # v
            [scale_notes[5], scale_notes[0], scale_notes[2]],  # VI
        ]
    
    # Repeat progression to fill length
    result = []
    for i in range(length_bars):
        result.append(chords[i % len(chords)])
    return result


def create_melody_clip(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
    slot_id: Annotated[int, Field(description="Clip slot index (0-based)")],
    scale_key: Annotated[
        str,
        Field(description="Musical key and scale (e.g., 'C major', 'A minor', 'D major')"),
    ],
    length_bars: Annotated[
        int,
        Field(description="Length of the clip in bars (typically 1-16 bars)"),
    ],
    style: Annotated[
        str,
        Field(description="Musical style (e.g., 'jazz', 'pop', 'classical', 'blues', 'rock')"),
    ],
    beats_per_bar: Annotated[
        int,
        Field(description="Beats per bar (default 4, for 4/4 time)"),
    ] = 4,
) -> str:
    """
    Create a MIDI clip with a musically coherent melody on the specified track and slot.
    The melody will be generated based on the scale/key, length, and style parameters.
    """
    # Calculate clip length in beats
    clip_length_beats = length_bars * beats_per_bar
    
    # Create empty MIDI clip
    create_result = control_clip_slot(
        track_id=track_id,
        clip_index=slot_id,
        command_type="create_clip",
        value=clip_length_beats,
    )
    
    if "error" in create_result.lower() or "failed" in create_result.lower():
        return f"Failed to create clip: {create_result}"
    
    # Generate melody notes
    notes = _generate_melody_notes(scale_key, length_bars, style, beats_per_bar)
    
    if not notes:
        return f"Failed to generate melody notes for {scale_key} {style} melody"
    
    # Format notes for add_notes command
    # Format: pitch,start_time,duration,velocity,mute for each note, comma-separated
    note_strings = []
    for pitch, start_time, duration, velocity, mute in notes:
        note_strings.append(f"{pitch},{start_time},{duration},{velocity},{str(mute).lower()}")
    
    note_data = ",".join(note_strings)
    
    # Add notes to clip
    add_result = control_clip(
        track_id=track_id,
        clip_id=slot_id,
        command_type="add_notes",
        additional_params=note_data,
    )
    
    if "error" in add_result.lower() or "failed" in add_result.lower():
        return f"Created clip but failed to add notes: {add_result}"
    
    return (
        f"Successfully created melody clip on track {track_id}, slot {slot_id}. "
        f"Generated {len(notes)} notes in {scale_key} style ({style}). "
        f"Clip length: {length_bars} bars ({clip_length_beats} beats)."
    )


def create_chord_progression_clip(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
    slot_id: Annotated[int, Field(description="Clip slot index (0-based)")],
    scale_key: Annotated[
        str,
        Field(description="Musical key and scale (e.g., 'C major', 'A minor', 'D major')"),
    ],
    length_bars: Annotated[
        int,
        Field(description="Length of the clip in bars (typically 1-16 bars)"),
    ],
    style: Annotated[
        str,
        Field(description="Musical style (e.g., 'jazz', 'pop', 'classical', 'blues', 'rock')"),
    ],
    progression_type: Annotated[
        Optional[str],
        Field(description="Optional chord progression type (e.g., 'I-V-vi-IV', 'ii-V-I'). If not specified, will be chosen based on style."),
    ] = None,
    beats_per_bar: Annotated[
        int,
        Field(description="Beats per bar (default 4, for 4/4 time)"),
    ] = 4,
) -> str:
    """
    Create a MIDI clip with a musically coherent chord progression on the specified track and slot.
    The chord progression will be generated based on the scale/key, length, style, and optional progression type.
    """
    # Calculate clip length in beats
    clip_length_beats = length_bars * beats_per_bar
    
    # Create empty MIDI clip
    create_result = control_clip_slot(
        track_id=track_id,
        clip_index=slot_id,
        command_type="create_clip",
        value=clip_length_beats,
    )
    
    if "error" in create_result.lower() or "failed" in create_result.lower():
        return f"Failed to create clip: {create_result}"
    
    # Generate chord progression notes
    notes = _generate_chord_progression_notes(
        scale_key, length_bars, style, progression_type, beats_per_bar
    )
    
    if not notes:
        return f"Failed to generate chord progression notes for {scale_key} {style} progression"
    
    # Format notes for add_notes command
    note_strings = []
    for pitch, start_time, duration, velocity, mute in notes:
        note_strings.append(f"{pitch},{start_time},{duration},{velocity},{str(mute).lower()}")
    
    note_data = ",".join(note_strings)
    
    # Add notes to clip
    add_result = control_clip(
        track_id=track_id,
        clip_id=slot_id,
        command_type="add_notes",
        additional_params=note_data,
    )
    
    if "error" in add_result.lower() or "failed" in add_result.lower():
        return f"Created clip but failed to add notes: {add_result}"
    
    return (
        f"Successfully created chord progression clip on track {track_id}, slot {slot_id}. "
        f"Generated {len(notes)} notes in {scale_key} style ({style}). "
        f"Clip length: {length_bars} bars ({clip_length_beats} beats)."
    )


def create_drum_pattern_clip(
    track_id: Annotated[int, Field(description="Track index (0-based)")],
    slot_id: Annotated[int, Field(description="Clip slot index (0-based)")],
    length_bars: Annotated[
        int,
        Field(description="Length of the clip in bars (typically 1-16 bars)"),
    ],
    style: Annotated[
        str,
        Field(description="Drum style (e.g., 'hip-hop', 'rock', 'electronic', 'jazz', 'pop')"),
    ],
    beats_per_bar: Annotated[
        int,
        Field(description="Beats per bar (default 4, for 4/4 time)"),
    ] = 4,
) -> str:
    """
    Create a MIDI clip with a musically coherent drum pattern on the specified track and slot.
    The drum pattern will be generated based on the length and style parameters.
    Uses standard MIDI drum mapping (kick=36, snare=38, hihat=42, etc.).
    """
    # Calculate clip length in beats
    clip_length_beats = length_bars * beats_per_bar
    
    # Create empty MIDI clip
    create_result = control_clip_slot(
        track_id=track_id,
        clip_index=slot_id,
        command_type="create_clip",
        value=clip_length_beats,
    )
    
    if "error" in create_result.lower() or "failed" in create_result.lower():
        return f"Failed to create clip: {create_result}"
    
    # Generate drum pattern notes
    notes = _generate_drum_pattern_notes(length_bars, style, beats_per_bar)
    
    if not notes:
        return f"Failed to generate drum pattern notes for {style} pattern"
    
    # Format notes for add_notes command
    note_strings = []
    for pitch, start_time, duration, velocity, mute in notes:
        note_strings.append(f"{pitch},{start_time},{duration},{velocity},{str(mute).lower()}")
    
    note_data = ",".join(note_strings)
    
    # Add notes to clip
    add_result = control_clip(
        track_id=track_id,
        clip_id=slot_id,
        command_type="add_notes",
        additional_params=note_data,
    )
    
    if "error" in add_result.lower() or "failed" in add_result.lower():
        return f"Created clip but failed to add notes: {add_result}"
    
    return (
        f"Successfully created drum pattern clip on track {track_id}, slot {slot_id}. "
        f"Generated {len(notes)} notes in {style} style. "
        f"Clip length: {length_bars} bars ({clip_length_beats} beats)."
    )

