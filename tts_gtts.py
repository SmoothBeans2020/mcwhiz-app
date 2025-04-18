import os
os.environ['PATH'] += os.pathsep + "C:/ffmpeg/bin"
import sys
from gtts import gTTS
import re

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
tts = gTTS(text=text, lang=language, slow=False, tld="com.au")

tts.save(tmp_name)