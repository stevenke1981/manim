param(
    [string]$RepoDir = "D:\manim",
    [ValidateSet("Edge", "Sapi")]
    [string]$TtsEngine = "Edge",
    [string]$VoiceName = "zh-TW-HsiaoChenNeural",
    [string]$EdgeRate = "+6%",
    [double]$PauseSeconds = 0.12,
    [string]$VariantName = "",
    [string]$BackgroundColor = ""
)

$ErrorActionPreference = "Stop"

$ProjectDir = Join-Path $RepoDir "projects\xy_equals_k"
$OutputDir = Join-Path $ProjectDir "output"
$TmpDir = Join-Path $ProjectDir "tmp"
$SegmentsPath = Join-Path $ProjectDir "segments.json"
$ScenePath = Join-Path $ProjectDir "xy_equals_k_scene.py"
$Manimgl = Join-Path $RepoDir ".venv\Scripts\manimgl.exe"
$EdgeTts = Join-Path $RepoDir ".venv\Scripts\edge-tts.exe"
$variantSuffix = ""
if (-not [string]::IsNullOrWhiteSpace($VariantName)) {
    $variantSuffix = "_" + ($VariantName -replace '[^A-Za-z0-9_-]', '_')
}
$commandParts = @(
    "powershell -ExecutionPolicy Bypass -File `"$ProjectDir\build_xy_equals_k.ps1`"",
    "-TtsEngine $TtsEngine",
    "-VoiceName `"$VoiceName`"",
    "-EdgeRate `"$EdgeRate`"",
    "-PauseSeconds $PauseSeconds"
)
if (-not [string]::IsNullOrWhiteSpace($VariantName)) {
    $commandParts += "-VariantName `"$VariantName`""
}
if (-not [string]::IsNullOrWhiteSpace($BackgroundColor)) {
    $commandParts += "-BackgroundColor `"$BackgroundColor`""
}
$buildCommand = $commandParts -join " "

New-Item -ItemType Directory -Force -Path $OutputDir, $TmpDir | Out-Null

$segments = Get-Content -LiteralPath $SegmentsPath -Raw -Encoding UTF8 | ConvertFrom-Json

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE"
    }
}

$selectedVoice = $VoiceName
$synth = $null
if ($TtsEngine -eq "Edge") {
    if (-not (Test-Path -LiteralPath $EdgeTts)) {
        throw "edge-tts.exe not found. Run: uv pip install edge-tts"
    }
} else {
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $availableVoice = $synth.GetInstalledVoices() |
        ForEach-Object { $_.VoiceInfo.Name } |
        Where-Object { $_ -eq $VoiceName } |
        Select-Object -First 1
    if (-not $availableVoice) {
        $availableVoice = ($synth.GetInstalledVoices() |
            Where-Object { $_.VoiceInfo.Culture.Name -eq "zh-TW" } |
            Select-Object -First 1).VoiceInfo.Name
    }
    if (-not $availableVoice) {
        throw "No zh-TW SAPI voice found."
    }
    $selectedVoice = $availableVoice
    $synth.SelectVoice($selectedVoice)
    $synth.Rate = 0
    $synth.Volume = 100
}

function Get-Duration([string]$Path) {
    $value = & ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 $Path
    return [double]::Parse($value.Trim(), [System.Globalization.CultureInfo]::InvariantCulture)
}

function Format-SrtTime([double]$Seconds) {
    $ts = [TimeSpan]::FromSeconds($Seconds)
    return "{0:00}:{1:00}:{2:00},{3:000}" -f [Math]::Floor($ts.TotalHours), $ts.Minutes, $ts.Seconds, $ts.Milliseconds
}

function Escape-ConcatPath([string]$Path) {
    return ($Path.Replace("\", "/").Replace("'", "'\''"))
}

$timingRows = @()
$srtLines = New-Object System.Collections.Generic.List[string]
$concatLines = New-Object System.Collections.Generic.List[string]
$cursor = 0.0

$silencePath = Join-Path $TmpDir "silence.wav"
Invoke-Checked { ffmpeg -y -hide_banner -loglevel error -f lavfi -i "anullsrc=r=48000:cl=mono" -t $PauseSeconds -c:a pcm_s16le $silencePath }

foreach ($seg in $segments) {
    $id = [int]$seg.id
    $rawPath = Join-Path $TmpDir ("seg_{0:00}_raw.wav" -f $id)
    $normPath = Join-Path $TmpDir ("seg_{0:00}.wav" -f $id)
    if ($TtsEngine -eq "Edge") {
        $textPath = Join-Path $TmpDir ("seg_{0:00}.txt" -f $id)
        $mp3Path = Join-Path $TmpDir ("seg_{0:00}.mp3" -f $id)
        [System.IO.File]::WriteAllText($textPath, [string]$seg.text, [System.Text.UTF8Encoding]::new($false))
        Invoke-Checked { & $EdgeTts --voice $selectedVoice --rate $EdgeRate --file $textPath --write-media $mp3Path }
        Invoke-Checked { ffmpeg -y -hide_banner -loglevel error -i $mp3Path -ar 48000 -ac 1 -c:a pcm_s16le $normPath }
    } else {
        $synth.SetOutputToWaveFile($rawPath)
        $synth.Speak([string]$seg.text)
        $synth.SetOutputToNull()
        Invoke-Checked { ffmpeg -y -hide_banner -loglevel error -i $rawPath -ar 48000 -ac 1 -c:a pcm_s16le $normPath }
    }
    $speechDuration = Get-Duration $normPath
    $visualDuration = $speechDuration + $PauseSeconds

    $start = $cursor
    $end = $cursor + $speechDuration
    $srtLines.Add([string]$id)
    $srtLines.Add(("{0} --> {1}" -f (Format-SrtTime $start), (Format-SrtTime $end)))
    $srtLines.Add([string]$seg.text)
    $srtLines.Add("")

    $timingRows += [pscustomobject]@{
        id = $id
        text = [string]$seg.text
        speech_duration = [Math]::Round($speechDuration, 3)
        pause = $PauseSeconds
        duration = [Math]::Round($visualDuration, 3)
    }

    $concatLines.Add("file '$((Escape-ConcatPath $normPath))'")
    $concatLines.Add("file '$((Escape-ConcatPath $silencePath))'")
    $cursor += $visualDuration
}

$timings = [pscustomobject]@{
    tts_engine = $TtsEngine
    voice = $selectedVoice
    edge_rate = $(if ($TtsEngine -eq "Edge") { $EdgeRate } else { $null })
    total_duration = [Math]::Round($cursor, 3)
    segments = $timingRows
}
$timings | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $OutputDir "timings.json") -Encoding UTF8
$srtLines | Set-Content -LiteralPath (Join-Path $OutputDir "subtitles.srt") -Encoding UTF8
$concatLines | Set-Content -LiteralPath (Join-Path $TmpDir "concat_audio.txt") -Encoding ASCII

$audioPath = Join-Path $OutputDir "xy_equals_k_narration.wav"
Invoke-Checked { ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i (Join-Path $TmpDir "concat_audio.txt") -c copy $audioPath }

$scriptPath = Join-Path $OutputDir "narration_zh-TW.md"
$scriptLines = @(
    "# xy = k narration script",
    "",
    "TTS engine: $TtsEngine",
    "Voice: $selectedVoice",
    $(if ($TtsEngine -eq "Edge") { "Rate: $EdgeRate" } else { "Rate: SAPI default" }),
    "Accent target: Taiwan Mandarin / zh-TW",
    "",
    "## Segments",
    ""
)
foreach ($row in $timingRows) {
    $scriptLines += ("{0}. {1}" -f $row.id, $row.text)
}
$scriptLines | Set-Content -LiteralPath $scriptPath -Encoding UTF8

Set-Location -LiteralPath $RepoDir
$videoDir = Join-Path $OutputDir ("manim" + $variantSuffix)
New-Item -ItemType Directory -Force -Path $videoDir | Out-Null
$animationStem = "xy_equals_k_animation" + $variantSuffix
$renderArgs = @($ScenePath, "XYEqualsKTeaching", "-w", "-r", "1280x720", "--fps", "30", "--video_dir", $videoDir, "--file_name", $animationStem, "--quiet")
if (-not [string]::IsNullOrWhiteSpace($BackgroundColor)) {
    $renderArgs += @("-c", $BackgroundColor)
}
Invoke-Checked { & $Manimgl @renderArgs }

$silentVideo = Join-Path $videoDir ($animationStem + ".mp4")
$narratedVideo = Join-Path $OutputDir ("xy_equals_k_narrated" + $variantSuffix + ".mp4")
$finalName = "xy_equals_k_teaching_zhTW" + $variantSuffix + "_subtitled.mp4"
$finalVideo = Join-Path $OutputDir $finalName

Invoke-Checked { ffmpeg -y -hide_banner -loglevel error -i $silentVideo -i $audioPath -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest $narratedVideo }

Push-Location -LiteralPath $OutputDir
Invoke-Checked { ffmpeg -y -hide_banner -loglevel error -i (Split-Path -Leaf $narratedVideo) -vf "subtitles=subtitles.srt:force_style='FontName=Microsoft JhengHei,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1.4,Shadow=0,Alignment=2,MarginV=6'" -c:v libx264 -crf 18 -preset medium -c:a copy $finalName }
Pop-Location

$probe = & ffprobe -v error -show_entries format=duration,size -of default=nw=1 $finalVideo
$logPath = Join-Path $OutputDir "process_log.md"
$log = @(
    "# xy = k teaching video process log",
    "",
    "- Skill used: manimgl-3b1b for ManimGL rendering.",
    "- Skills used: piper1-gpl was checked for local TTS options; speech skill was checked but OPENAI_API_KEY was not set; ffmpeg skill was used for audio/video/subtitle assembly.",
    "- TTS engine used: $TtsEngine.",
    "- Voice used: $selectedVoice.",
    $(if ($TtsEngine -eq "Edge") { "- Edge rate: $EdgeRate." } else { "- SAPI rate: default." }),
    "- Segment pause: $PauseSeconds seconds.",
    "- Variant: $(if ($VariantName) { $VariantName } else { 'default' }).",
    "- Background color: $(if ($BackgroundColor) { $BackgroundColor } else { 'default' }).",
    "- Accent target: Taiwan Mandarin / zh-TW.",
    "- Manim scene: $ScenePath.",
    "- Narration script: $scriptPath.",
    "- Subtitles: $(Join-Path $OutputDir "subtitles.srt").",
    "- Narration audio: $audioPath.",
    "- Silent animation: $silentVideo.",
    "- Narrated video: $narratedVideo.",
    "- Final subtitled video: $finalVideo.",
    "",
    "## Verification",
    "",
    '```text',
    ($probe -join [Environment]::NewLine),
    '```',
    "",
    "## Build command",
    "",
    '```powershell',
    $buildCommand,
    '```'
)
$log | Set-Content -LiteralPath $logPath -Encoding UTF8

Write-Host "Final video: $finalVideo"
Write-Host "Subtitles: $(Join-Path $OutputDir "subtitles.srt")"
Write-Host "Narration: $audioPath"
Write-Host "Process log: $logPath"
