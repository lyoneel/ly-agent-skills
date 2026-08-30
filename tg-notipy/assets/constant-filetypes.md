# Constant: tg-notipy file types

File type maps for auto-detection, extension table first, MIME table
second, fallback `document`. Read by scripts/tg_constants.py and
referenced by the agent prose; never re-listed elsewhere. Append a new
entry here only, when a new type must be detected.

## Extension map

```text
.jpg: photo
.jpeg: photo
.png: photo
.gif: photo
.webp: photo
.bmp: photo
.mp3: audio
.m4a: audio
.aac: audio
.flac: audio
.ogg: voice
.opus: voice
.mp4: video
.webm: video
.mkv: video
.mov: video
.avi: video
.flv: video
.wmv: video
.m4v: video
.ogv: video
```

## MIME map

```text
image/jpeg: photo
image/png: photo
image/gif: photo
image/webp: photo
audio/mpeg: audio
audio/mp3: audio
audio/mp4: audio
audio/x-m4a: audio
audio/m4a: audio
audio/ogg: voice
audio/opus: voice
video/mp4: video
video/webm: video
video/x-matroska: video
video/quicktime: video
video/avi: video
video/x-msvideo: video
video/x-flv: video
video/mpeg: video
video/x-ms-wmv: video
```

Detection order, fallback rule, and album coercion live in
`../references/guide-filetypes.md`.
