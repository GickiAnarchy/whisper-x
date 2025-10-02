import json
import datetime

def convert_seconds_to_srt_time(seconds):
    if seconds is None:
        return "00:00:00,000"
    
    milliseconds = int((seconds - int(seconds)) * 1000)
    dt = datetime.datetime.fromtimestamp(seconds, datetime.timezone.utc)
    time_str = dt.strftime("%H:%M:%S")
    return f"{time_str},{milliseconds:03d}"

def whisperx_json_to_word_level_srt(json_path, srt_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    srt_content = []
    index = 1
    
    for segment in data['segments']:
        for word_data in segment['words']:
            start = word_data.get('start')
            end = word_data.get('end')
            word = word_data.get('word')

            if start is None or end is None or word is None:
                continue

            srt_content.append(str(index))
            srt_content.append(f"{convert_seconds_to_srt_time(start)} --> {convert_seconds_to_srt_time(end)}")
            srt_content.append(word.strip())
            srt_content.append("")
            
            index += 1

    with open(srt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_content))

    print(f"Word-level SRT file saved to {srt_path}")


if __name__ == "__main__":
    json_file = 'btmb.json'
    srt_file = 'your_output_word_level.srt'
    
    whisperx_json_to_word_level_srt(json_file, srt_file)