import json
from datetime import timedelta

# --- Configuration ---
# Your desired minimum duration for a single 'word-chunk' (in seconds)
MIN_DURATION_SECONDS = 0.15 # Set this to your desired time (e.g., 0.1s, 0.15s) 
# --- Configuration ---

def format_time(seconds):
    """Converts seconds to the SRT time format: HH:MM:SS,mmm"""
    ms = round(seconds * 1000)
    return str(timedelta(milliseconds=ms)).replace('.', ',')

def process_and_merge_words(segments, min_duration):
    """
    Reads the WhisperX word list and merges words whose duration is too short.
    It returns a flattened list of 'merged_words'.
    """
    merged_words = []
    
    # 1. Flatten all words from all segments into one continuous list
    all_words = []
    for segment in segments:
        if 'words' in segment:
            all_words.extend(segment['words'])

    if not all_words:
        return []

    # 2. Start the merging process
    current_word_chunk = None

    for word in all_words:
        # Initialize the first chunk
        if current_word_chunk is None:
            current_word_chunk = {
                'start': word['start'],
                'end': word['end'],
                'text': word['word']
            }
            continue
        
        # Calculate the duration of the current chunk
        duration = current_word_chunk['end'] - current_word_chunk['start']
        
        if duration < min_duration:
            # Current chunk is too short, so merge the new word into it
            current_word_chunk['text'] += ' ' + word['word']
            current_word_chunk['end'] = word['end'] # Extend the end time
        else:
            # Current chunk is long enough, finalize it and start a new one
            merged_words.append(current_word_chunk)
            current_word_chunk = {
                'start': word['start'],
                'end': word['end'],
                'text': word['word']
            }

    # Don't forget the last accumulated word chunk
    if current_word_chunk is not None:
        merged_words.append(current_word_chunk)
        
    return merged_words


def generate_srt(merged_words, output_filename):
    """
    Groups the merged word chunks into subtitle lines based on large gaps 
    and writes the final SRT file.
    """
    # A large time gap (e.g., > 1.0 seconds) is a natural cue break
    MAX_GAP_SECONDS = 1.0 
    
    srt_content = ""
    cue_index = 1
    current_cue_start = None
    current_cue_text = []

    for i, word in enumerate(merged_words):
        
        # Start of a new cue
        if current_cue_start is None:
            current_cue_start = word['start']
        
        # Check for a large gap to force a new cue
        if i > 0:
            previous_word_end = merged_words[i-1]['end']
            time_gap = word['start'] - previous_word_end
            
            if time_gap > MAX_GAP_SECONDS:
                # 1. Finalize the previous cue
                end_time = merged_words[i-1]['end']
                time_line = f"{format_time(current_cue_start)} --> {format_time(end_time)}"
                text_line = " ".join(current_cue_text)
                
                srt_content += f"{cue_index}\n{time_line}\n{text_line}\n\n"
                cue_index += 1
                
                # 2. Start the new cue
                current_cue_start = word['start']
                current_cue_text = []
        
        current_cue_text.append(word['text'])
        
    # Finalize the very last cue
    if current_cue_start is not None:
        end_time = merged_words[-1]['end']
        time_line = f"{format_time(current_cue_start)} --> {format_time(end_time)}"
        text_line = " ".join(current_cue_text)
        
        srt_content += f"{cue_index}\n{time_line}\n{text_line}\n\n"

    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(srt_content.strip()) # strip removes the final newline

    print(f"Successfully created SRT file: {output_filename}")


def main(json_file, srt_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    merged_words = process_and_merge_words(data['segments'], MIN_DURATION_SECONDS)
    
    if merged_words:
        generate_srt(merged_words, srt_file)
    else:
        print("No words found in the JSON data.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Custom SRT generator from WhisperX JSON with short word merging.")
    parser.add_argument("json_file", help="Path to the WhisperX JSON output file.")
    parser.add_argument("srt_file", help="Name of the output SRT file.")
    args = parser.parse_args()
    
    main(args.json_file, args.srt_file)

