# ManimGL Teaching Video Template

This reusable workflow was distilled from the `xy = k` teaching video project.

## Skills Used

- `$manimgl-3b1b`: ManimGL setup, scene rendering, and style variants.
- `$ffmpeg`: audio normalization, concatenation, muxing, subtitle burn-in, preview screenshots, and `ffprobe` verification.
- `$speech`: check only when OpenAI TTS is requested and `OPENAI_API_KEY` is configured.
- `$piper1-gpl` or `$moss-tts-nano`: use when local/offline voice generation is requested.
- `$manimgl-teaching-video`: global workflow skill for future teaching videos.

## Reusable Project Shape

```text
projects/<lesson_slug>/
  segments.json
  <lesson_slug>_scene.py
  build_<lesson_slug>.ps1
  teaching_video_agent_template.md
  output/
    <lesson_slug>_teaching_zhTW_subtitled.mp4
    <lesson_slug>_teaching_zhTW_blackboard_subtitled.mp4
    <lesson_slug>_narration.wav
    subtitles.srt
    narration_zh-TW.md
    timings.json
    process_log.md
    preview_*.png
  tmp/
```

`output/` and `tmp/` are generated artifacts and should stay out of git unless the user explicitly asks to version final media.

## Agent Workflow

1. Write the lesson as short narration segments in `segments.json`.
2. Generate one TTS clip per segment.
3. Normalize clips to 48 kHz mono WAV.
4. Measure each clip with `ffprobe`.
5. Add a short pause, usually `0.08` to `0.15` seconds for Edge neural TTS.
6. Write `timings.json` and `subtitles.srt` from the same timing data.
7. Render the silent ManimGL animation using `timings.json`.
8. Mux narration and video.
9. Burn Traditional Chinese subtitles.
10. Extract preview frames and fix layout issues from user-marked screenshots.
11. Save a process log with commands, skills, voices, outputs, and verification.

## Current Commands

Default version:

```powershell
powershell -ExecutionPolicy Bypass -File "D:\manim\projects\xy_equals_k\build_xy_equals_k.ps1" -TtsEngine Edge -VoiceName "zh-TW-HsiaoChenNeural" -EdgeRate "+6%" -PauseSeconds 0.12
```

Blackboard version:

```powershell
powershell -ExecutionPolicy Bypass -File "D:\manim\projects\xy_equals_k\build_xy_equals_k.ps1" -TtsEngine Edge -VoiceName "zh-TW-HsiaoChenNeural" -EdgeRate "+6%" -PauseSeconds 0.12 -VariantName blackboard -BackgroundColor "#123B2A"
```

## Layout Rules Learned

- Keep title and navigation labels in the upper-left safe area.
- Keep formulas and summaries on the right side, but wrap long labels.
- Put subtitles close to the bottom with a readable outline.
- Extract screenshots after every user layout edit.
- Preserve variants instead of overwriting the only final output.

## Output Checklist

- MP4 has video and audio streams.
- Duration matches the TTS timing table.
- Subtitles are readable and do not block important labels.
- Long right-side text is wrapped.
- Blackboard and default variants are separate files.
- Process log includes exact TTS voice, rate, pause, background color, and command.
