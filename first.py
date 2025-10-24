import whisperx
import os
import glob
import torch
import gc

# --- Configuration ---
# 1. Directory to search for audio files
AUDIO_DIR = "whisper-x/music/"
# 2. Output directory for subtitle files (will be created if it doesn't exist)
OUTPUT_DIR = "whisper-x/subtitles/"
# 3. Model parameters
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8" # Use float16 on CUDA for speed/memory
WHISPER_MODEL = "large-v2" # You can change this to "medium", "base", etc.
BATCH_SIZE = 4 # Adjust based on your GPU memory (lower if out of memory)

# --- Utility Functions ---

def create_srt_file(result, output_path):
    """
    Creates an SRT subtitle file from the WhisperX result.
    This is a basic implementation; a more robust one would handle VTT/other formats.
    """
    def format_timestamp(seconds):
        # Converts seconds to SRT time format: HH:MM:SS,mmm
        # Note: WhisperX segments have a 'start' and 'end' key
        hours, remainder = divmod(seconds, 3600)
        minutes, remainder = divmod(remainder, 60)
        seconds, milliseconds = divmod(remainder, 1)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds*1000):03}"

    with open(output_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"], 1):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()
            
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")


# --- Main Processing Logic ---

def process_audio_directory(audio_dir, output_dir):
    print(f"✅ Running WhisperX on device: {DEVICE} with compute type: {COMPUTE_TYPE}")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Supported audio file extensions
    audio_extensions = ['*.mp3', '*.wav', '*.m4a', '*.flac', '*.ogg']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(glob.glob(os.path.join(audio_dir, ext)))

    if not audio_files:
        print(f"❌ No audio files found in {audio_dir}")
        return

    # Load models once outside the loop for efficiency
    try:
        # 1. Load Whisper model
        print(f"⏳ Loading Whisper model '{WHISPER_MODEL}'...")
        model = whisperx.load_model(WHISPER_MODEL, DEVICE, compute_type=COMPUTE_TYPE)
        
        # 2. Load alignment model (language will be auto-detected per file)
        # We load the align model inside the loop/or a function if language is unknown for each
        # For simplicity, let's load it inside the loop after transcription to get the language.
        # However, for a *fixed* language, you'd load it here.

    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    print(f"📦 Found {len(audio_files)} files to process.")
    
    for i, audio_path in enumerate(audio_files):
        print(f"\n--- Processing file {i+1}/{len(audio_files)}: {os.path.basename(audio_path)} ---")
        
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        srt_output_path = os.path.join(output_dir, base_name + ".srt")
        
        if os.path.exists(srt_output_path):
            print(f"⏭️ Skipping: Subtitle file already exists at {srt_output_path}")
            continue

        try:
            # Load audio
            audio = whisperx.load_audio(audio_path)
            
            # 1. Transcribe (includes language detection)
            print("  1. Transcribing...")
            result = model.transcribe(audio, batch_size=BATCH_SIZE)
            language = result["language"]
            print(f"  -> Detected language: **{language}**")

            # Clean up GPU memory from the transcription model
            del model
            gc.collect()
            if DEVICE == "cuda":
                torch.cuda.empty_cache()

            # 2. Load and Run Alignment Model
            print("  2. Aligning and getting word-level timestamps...")
            # Alignment model needs the detected language
            model_a, metadata = whisperx.load_align_model(language_code=language, device=DEVICE)
            result = whisperx.align(result["segments"], model_a, metadata, audio, DEVICE, return_char_alignments=False)
            
            # Clean up GPU memory from the alignment model
            del model_a
            gc.collect()
            if DEVICE == "cuda":
                torch.cuda.empty_cache()

            # 3. Create SRT File
            create_srt_file(result, srt_output_path)
            print(f"  🎉 Success! Subtitle saved to: **{srt_output_path}**")

        except Exception as e:
            print(f"❌ An error occurred while processing {os.path.basename(audio_path)}: {e}")
            
    # Reload model for next run (optional, but good practice if you deleted it above)
    # If you remove the 'del model' steps, you should ensure memory is sufficient.
    print("\n✅ Batch processing complete.")

if __name__ == "__main__":
    process_audio_directory(AUDIO_DIR, OUTPUT_DIR)
