import json
import os
import glob

# --- Configuration ---
# Directory where your WhisperX JSON files are located
JSON_DIR = "./subtitles/" 
# Directory where the new word-level SRT files will be saved
OUTPUT_DIR = "word_subtitles/" 

# --- Utility Function ---

def format_timestamp(seconds):
    """Converts a time in seconds (float) to the SRT timestamp format."""
    if seconds is None:
        return "00:00:00,000"
    
    hours, remainder = divmod(seconds, 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds, milliseconds = divmod(remainder, 1)
    
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds*1000):03}"

def convert_json_to_word_srt(json_path, output_path):
    """Reads a WhisperX JSON and writes a word-level SRT file."""
    
    print(f"  Reading: {os.path.basename(json_path)}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return

    # WhisperX stores the word-level data in the 'word_segments' key
    words = data.get("word_segments")
    
    if not words:
        print("⚠️ Warning: 'word_segments' not found in JSON. Skipping.")
        return

    with open(output_path, "w", encoding="utf-8") as f:
        subtitle_index = 1
        for word_data in words:
            # Check for required data and skip words without timing
            if 'start' not in word_data or 'end' not in word_data or 'word' not in word_data:
                continue

            start = format_timestamp(word_data['start'])
            end = format_timestamp(word_data['end'])
            text = word_data['word'].strip()

            # Skip empty strings
            if not text:
                continue
            
            # 1. Subtitle Index
            f.write(f"{subtitle_index}\n")
            # 2. Timecode
            f.write(f"{start} --> {end}\n")
            # 3. Subtitle Text (one word)
            f.write(f"{text}\n\n")
            
            subtitle_index += 1

    print(f"  🎉 Saved word-level SRT to: **{os.path.basename(output_path)}**")


# --- Main Logic ---

def batch_convert():
    """Finds all JSON files and converts them to word-level SRTs."""
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    json_files = glob.glob(os.path.join(JSON_DIR, "*.json"))

    if not json_files:
        print(f"❌ No JSON files found in {JSON_DIR}. Did you run the transcription script first?")
        return

    print(f"📦 Found {len(json_files)} JSON files. Starting word-level conversion...")

    for i, json_path in enumerate(json_files):
        print(f"\n--- Processing file {i+1}/{len(json_files)} ---")
        
        base_name = os.path.splitext(os.path.basename(json_path))[0]
        # Use a distinctive name
        srt_output_path = os.path.join(OUTPUT_DIR, base_name + ".word.srt") 
        
        # Skip if the word-level SRT already exists
        if os.path.exists(srt_output_path):
            print(f"⏭️ Skipping: Word-level SRT already exists.")
            continue

        convert_json_to_word_srt(json_path, srt_output_path)
            
    print("\n✅ Batch conversion complete.")

if __name__ == "__main__":
    batch_convert()
