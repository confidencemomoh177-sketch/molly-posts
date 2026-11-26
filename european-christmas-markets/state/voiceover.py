"""Narration for post videos (free, offline: Kokoro TTS).
Setup once per workspace:
  pip install kokoro-onnx soundfile --break-system-packages
  curl -L -o kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
  curl -L -o voices.bin  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
Usage: python3 voiceover.py <model_dir> <out.wav> "<script>" [voice=af_heart] [speed=1.05]
Keep scripts to ~35-40 words so narration ends by ~14 s. Only facts from the book; no author name.
Chosen voice (Charlize, 2026-11-26): af_heart, American female.
"""
import sys, soundfile as sf
from kokoro_onnx import Kokoro
d, out, text = sys.argv[1], sys.argv[2], sys.argv[3]
voice = sys.argv[4] if len(sys.argv) > 4 else "af_heart"
speed = float(sys.argv[5]) if len(sys.argv) > 5 else 1.05
k = Kokoro(f"{d}/kokoro.onnx", f"{d}/voices.bin")
s, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
sf.write(out, s, sr)
print(f"{len(s) / sr:.1f}s")
