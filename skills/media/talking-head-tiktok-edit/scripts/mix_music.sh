#!/bin/bash
# Mux music under the rendered no-music video with this user's default mix.
# Usage: mix_music.sh overlay_nomusic.mp4 TRACK.mp3 START_S OUT.mp4 [VOL=1.0]
# Voice in the input is already loudnorm'd to -11 LUFS by the render step.
# Target: the ducked music stem should measure about -22 LUFS (~11 dB under the voice). Check with --stem.
# Runs on macOS and in Windows git-bash (only needs ffmpeg/ffprobe/awk/grep; no python).
# On Windows pass C:/... or relative paths to the files (not /c/...), because ffmpeg is a native exe.
IN=$1; TRACK=$2; SS=$3; OUT=$4; VOL=${5:-1.0}
T=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN" | tr -d '\r')
FO=$(awk -v t="$T" 'BEGIN{x=t-1.5; if(x<0)x=0; print x}')
STEM="${OUT%.*}._stem_$$.wav"   # next to OUT: /tmp is not a path native Windows ffmpeg can see
ffmpeg -y -v error -i "$IN" -ss "$SS" -i "$TRACK" -filter_complex \
"[1:a]aresample=48000,loudnorm=I=-18:TP=-2,volume=$VOL,afade=t=in:d=0.05,afade=t=out:st=$FO:d=1.5[m];[0:a]asplit[v1][v2];[m][v2]sidechaincompress=threshold=0.05:ratio=2.5:attack=20:release=300:knee=3[md];[v1][md]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.93[a]" \
-map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -movflags +faststart "$OUT"
# Ducked stem loudness (feed the voice straight in as sidechain; an unused asplit output makes ffmpeg error):
ffmpeg -v error -y -i "$IN" -ss "$SS" -t "$T" -i "$TRACK" -filter_complex \
"[1:a]aresample=48000,loudnorm=I=-18:TP=-2,volume=$VOL[m];[m][0:a]sidechaincompress=threshold=0.05:ratio=2.5:attack=20:release=300:knee=3[md]" \
-map "[md]" "$STEM"
echo "music stem: $(ffmpeg -i "$STEM" -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1 | tr -d '\r')"
echo "full mix:   $(ffmpeg -i "$OUT" -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1 | tr -d '\r')"
rm -f "$STEM"
