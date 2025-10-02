import json

def format_timestamp(seconds):
    """Formats a float timestamp into SRT format (HH:MM:SS,ms)."""
    if seconds is None:
        return "00:00:00,000"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"

def convert_whisperx_json_to_srt(json_filepath, srt_filepath):
    """Converts a WhisperX JSON output file to an SRT file."""
    with open(json_filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(srt_filepath, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(data['segments']):
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            text = segment['text'].strip()

            f.write(f"{i + 1}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")

if __name__ == "__main__":
    convert_whisperx_json_to_srt('btmb.json', 'output.srt')