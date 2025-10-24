import whisperx
import os
import glob
import torch
import gc
import json # Added for JSON file handling

# --- Configuration ---
# 1. Directory to search for audio files
AUDIO_DIR = "whisper-x/music/"
# 2. Output directory for subtitle files (will be created if it doesn't exist)
OUTPUT_DIR = "./subtitles/"
# 3. Model parameters (Same as before, keep these if using Colab/GPU)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8"
WHISPER_MODEL = "large-v2"
BATCH_SIZE = 4 

# --- Utility Functions ---

def create_srt_file(result, output_path):
    """Creates an SRT subtitle file from the WhisperX result segments."""
    def format_timestamp(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, remainder = divmod(remainder, 60)
        seconds, milliseconds = divmod(remainder, 1)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds*1000):03}"

    with open(output_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"], 1):
            # Check for 'start' and 'end' keys, which should exist after alignment
            start = format_timestamp(segment.get("start", 0)) 
            end = format_timestamp(segment.get("end", 0))
            text = segment["text"].strip()
            
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")

def create_json_file(result, output_path):
    """Saves the entire WhisperX result dictionary to a JSON file."""
    # Use json.dump to save the result. The 'indent=2' makes it readable.
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


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

    # Load initial model
    try:
        print(f"⏳ Loading Whisper model '{WHISPER_MODEL}'...")
        model = whisperx.load_model(WHISPER_MODEL, DEVICE, compute_type=COMPUTE_TYPE)
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    print(f"📦 Found {len(audio_files)} files to process.")
    
    for i, audio_path in enumerate(audio_files):
        print(f"\n--- Processing file {i+1}/{len(audio_files)}: {os.path.basename(audio_path)} ---")
        
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        srt_output_path = os.path.join(output_dir, base_name + ".srt")
        json_output_path = os.path.join(output_dir, base_name + ".json") # New JSON path
        
        if os.path.exists(srt_output_path) and os.path.exists(json_output_path):
            print(f"⏭️ Skipping: Both subtitle and JSON files already exist.")
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
            # Note: We skip deleting the model here to prevent constant re-loading 
            # if memory allows, but re-enable it if you run into OOM errors.
            # del model; gc.collect(); torch.cuda.empty_cache() 

            # 2. Load and Run Alignment Model
            print("  2. Aligning and getting word-level timestamps...")
            model_a, metadata = whisperx.load_align_model(language_code=language, device=DEVICE)
            result = whisperx.align(result["segments"], model_a, metadata, audio, DEVICE, return_char_alignments=False)
            
            # Clean up GPU memory from the alignment model
            del model_a; gc.collect()
            if DEVICE == "cuda":
                torch.cuda.empty_cache()

            # 3. Create Output Files
            create_srt_file(result, srt_output_path)
            print(f"  🎉 Success! Subtitle saved to: **{srt_output_path}**")
            
            create_json_file(result, json_output_path) # Save JSON file
            print(f"  💾 Success! Full data saved to: **{json_output_path}**")


        except Exception as e:
            print(f"❌ An error occurred while processing {os.path.basename(audio_path)}: {e}")
            
    print("\n✅ Batch processing complete.")

if __name__ == "__main__":
    
    # ⚠️ REMINDER FOR COLAB USERS: 
    # If you are still getting the cuDNN error, run these commands 
    # in a separate cell BEFORE this script to fix the dependency conflict:
    # !pip uninstall ctranslate2 -y
    # !pip install ctranslate2==4.4.0
    
    process_audio_directory(AUDIO_DIR, OUTPUT_DIR)
