import unicodedata
import re

from game_assistant.models import Village, Instance

def clean_text(text):
    text = unicodedata.normalize('NFKC', text)

    replacements = {
        '\u00a0': ' ',
        '“': '"', '”': '"',
        '‘': "'", '’': "'",
        '…': '...',
        '\u2212': '-',
        '\u202D': '', '\u202E': '', '\u202C': '',
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    invisible_chars = ['\u200b', '\u200c', '\u200d', '\ufeff']
    for char in invisible_chars:
        text = text.replace(char, '')

    text = re.sub(r'[ \t]+', ' ', text)

    return text.strip()

def parse_instance(input_str: str) -> Instance:
    lines = input_str.strip().split('\n')
    villages = []

    pattern = r'^\s*\(\s*-?\d+\s*\|\s*-?\d+\s*\)$'

    l1 = lines.pop(0).strip()
    while lines:
        l2 = lines.pop(0).strip()
        if re.match(pattern, l2) is not None:
            name = l1.strip()
            production = 0
            villages.append(Village(name=name, production=production))
        l1 = l2
    return Instance(villages=villages)

def get_instance_from_input(input_str: str) -> Instance:
    cleaned_input = clean_text(input_str)
    return parse_instance(cleaned_input)
