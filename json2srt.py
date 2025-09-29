import json

def format_time(milliseconds):
    seconds = int(milliseconds / 1000)
    ms = int(milliseconds % 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)     
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"

def json_to_srt(json_file_path, srt_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(srt_file_path, 'w', encoding='utf-8') as srt_file:
        for i, segment in enumerate(data['segments']):
            start_time = format_time(segment['start'])
            end_time = format_time(segment['end'])
            text = segment['text'].strip()

            srt_file.write(f"{i + 1}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{text}\n\n")

    # Example usage:
json_to_srt('mic_small.json', 'output.srt')
