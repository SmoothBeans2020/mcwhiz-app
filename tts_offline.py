import os
os.environ['PATH'] += os.pathsep + "C:/ffmpeg/bin"
import sys
import pyttsx3
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

engine = pyttsx3.init(driverName='sapi5')
engine.setProperty('rate', 180)
engine.say(f'<pitch absmiddle="10">{text}</pitch>')
engine.runAndWait()
