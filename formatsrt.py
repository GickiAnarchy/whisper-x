import whisperx
import torch

# 1. Choose model and device
device = "cuda" if torch.cuda.is_available() else "cpu"
batch_size = 16 # Reduce if you run out of VRAM (especially with large models)
compute_type = "float16" if torch.cuda.is_available() else "int8"

# 2. Load model
model = whisperx.load_model("large-v2", device, compute_type=compute_type)

# 3. Transcribe audio
# You can specify the language here, or let it detect: language="en"
audio = whisperx.load_audio(audio_file_path)
print("--- Transcribing ---")
result = model.transcribe(audio, batch_size=batch_size)

# 4. Load Alignment model and align
print("--- Aligning (Word-level timestamps) ---")
model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

# The final result with word-level timestamps is in result["segments"]
print("\n--- Transcription Result with Word Timestamps ---")
for segment in result["segments"]:
    print(segment)
