import os
os.environ['PATH'] += os.pathsep + "C:/ffmpeg/bin"
import sys
import gtts
import re
from pydub import AudioSegment
import io


def change_pitch(audio, semitones):
    new_sample_rate = int(audio.frame_rate * (2.0 ** (semitones / 12.0)))
    return audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate}).set_frame_rate(audio.frame_rate)

def extract_quoted_text(text):
    """Extracts all text enclosed in double backticks from a string.

    Args:
        text: The input string.

    Returns:
        A list of strings, where each string is a segment of text enclosed in double backticks, or an empty list if no backticks are found.
    """
    return re.findall(r'`([^`]*)`', text)

text = ''.join(extract_quoted_text(sys.argv[1]))

tmp_name = sys.argv[2]

language = 'en'
tts = gtts.gTTS(text=text, lang=language, slow=False, tld="co.uk")

fp = io.BytesIO()
tts.write_to_fp(fp)
fp.seek(0)

sound = AudioSegment.from_file(fp, format="mp3")

lowered = change_pitch(sound, semitones=-8)  

lowered.export(tmp_name, format="mp3")