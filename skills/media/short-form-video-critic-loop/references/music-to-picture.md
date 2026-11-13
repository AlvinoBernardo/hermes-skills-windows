# Music edited to the picture (numpy/scipy + ffmpeg)

1. **Find each candidate track's drop.**
   - With librosa, compute per-0.1 s RMS dB over the first 60 s, plus onset strength.
   - A drop is a near-silent gap (below −60 dB) followed by a big jump, e.g. a trap beat stop at 13.9–14.1 s and slam at 14.22 s.
   - Pick tracks with an obvious stop→slam and high onset density. Chill or flat-loudness tracks don't work.
2. **Offset the source** so that `src_start = drop - flash_time`. Decode that slice with `ffmpeg -ss src_start -t dur -af loudnorm=I=-14 -ac 2 -ar 48000 -f f32le -`.
3. **Under section/chapter cards**, crossfade to a 4th-order 380 Hz low-pass copy (`scipy.signal.butter` + `sosfiltfilt`) with 50 ms ramps. This gives a muffled "other room" feel.
4. **Add SFX in numpy:**
   - **Sub-boom on the flash:** `0.55*sin(2π(48+40e^{-18t})t)e^{-6t}` plus band-passed (800–6000 Hz) noise with `e^{-22t}`.
   - **Rising whoosh into each card:** band-passed (1500–7000 Hz) noise × t^2.2 over 0.32 s, ending at the cut.
5. **Mix with ffmpeg:**
   - Voice: loudnorm −14, `aresample` + `asetpts=N/SR/TB`, `apad`.
   - Bed: `volume=0.32`, sidechaincompress (threshold 0.05, ratio 4) keyed by the voice.
   - Then `amix normalize=0`, a final loudnorm −14 TP −1.5, and stereo.
6. **Verify:** music −21 dB before the flash and about −14 after; high-band energy under cards should drop to about −95 dB. Full decode, then measure the final LUFS.
7. **Offer 2 alternates** with the same edit. Render them audio-only by muxing the new mix onto the existing picture (`-map 0:v -map 1:a -c copy`) instead of re-rendering frames.
