import pysubs2
from datetime import timedelta
import os

# --- Configuration ---
# File names
INPUT_SRT_FILE = "gp.srt"
OUTPUT_SRT_FILE = "output_combined.srt"

# Subtitle events shorter than this duration (in milliseconds) will be 
# combined with the next event. (0.5 seconds = 500 milliseconds)
SHORT_WORD_THRESHOLD_MS = 500

def combine_short_words(input_file: str, output_file: str, threshold_ms: int):
    """
    Combines subtitle events in an SRT file that are shorter than a given 
    threshold with the following event.
    """
    
    # 1. Load the subtitle file
    try:
        subs = pysubs2.load(input_file, encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except Exception as e:
        print(f"Error loading subtitle file: {e}")
        return

    print(f"Loaded {len(subs)} subtitle events from '{input_file}'.")
    
    # 2. Process each subtitle event using a while loop for safe list modification
    i = 0
    # Stop one short of the end because we always look at the next event (i + 1)
    while i < len(subs) - 1:
        sub = subs[i]
        
        # Calculate duration of the current subtitle event
        duration_ms = sub.duration
        
        # 3. Check and Combine
        if duration_ms < threshold_ms:
            next_sub = subs[i + 1]
            
            # Combine the text: Current text + a space + Next text
            sub.text = sub.text.strip() + ' ' + next_sub.text.strip()
            
            # Extend the time to the end of the next subtitle
            sub.end = next_sub.end
            
            # Print a message for the user. We use (i + 1) for the 1-based subtitle number.
            duration_s = duration_ms / 1000.0
            print(f"Merged event {i + 1} (Duration: {duration_s:.3f}s) with the next one.")
            
            # Remove the next subtitle from the list since its content/timing is now in the current one
            subs.pop(i + 1)
            
            # Do NOT increment 'i'. The new element at i+1 needs to be checked 
            # against the newly combined subtitle at index 'i'.
        else:
            # Only move to the next subtitle if no merge occurred
            i += 1

    # 4. Re-index and save the new subtitle file
    # This ensures the final SRT file has correctly numbered subtitles (1, 2, 3, ...)
    subs.sort()

    try:
        subs.save(output_file)
        print(f"\nSuccessfully saved new file with combined events to '{output_file}'.")
        print(f"Final event count: {len(subs)}")
    except Exception as e:
        print(f"Error saving subtitle file: {e}")


if __name__ == '__main__':
    print("--- SRT Event Combiner Script ---")
    print(f"Threshold set to {SHORT_WORD_THRESHOLD_MS / 1000.0} seconds.")
    # You may need to change the file names here if your files are named differently
    combine_short_words(INPUT_SRT_FILE, OUTPUT_SRT_FILE, SHORT_WORD_THRESHOLD_MS)

