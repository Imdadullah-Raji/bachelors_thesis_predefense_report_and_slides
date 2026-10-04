"""Count report prose, headings, table text, and captions, excluding references.

Displayed/inline mathematics, citation markers, title-page metadata, and words
embedded in figure images are excluded. Hyphenated words count as one word.
Requires the installed detex command; no third-party Python packages are needed.
"""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / 'texFiles'
source = (TEX / 'writeup.tex').read_text()
source = re.sub(r'\\input\{([^}]+)\}', lambda m: (TEX / m.group(1)).read_text(), source)

def group(text, start):
    assert text[start] == '{'
    depth = 1
    end = start + 1
    while depth:
        if text[end] == '{' and text[end - 1] != '\\':
            depth += 1
        elif text[end] == '}' and text[end - 1] != '\\':
            depth -= 1
        end += 1
    return text[start + 1:end - 1], end

while '\\fig{' in source:
    start = source.index('\\fig{')
    end = start + len('\\fig')
    args = []
    for _ in range(4):
        arg, end = group(source, end)
        args.append(arg)
    source = source[:start] + '\\caption{' + args[2] + '}' + source[end:]

source = re.sub(r'\\(?:cite|ref|label)\{[^}]*\}', '', source)
source = re.sub(r'\\begin\{tabularx\}[^\n]*', '', source)
count_input = ROOT / 'build/count_input.tex'
count_input.write_text(source)
plain = subprocess.check_output(['detex', '-l', str(count_input)], text=True)
plain = plain.replace('&', ' ')
(ROOT / 'build/word_count_text.txt').write_text(plain)
count = len(re.findall(r"[A-Za-z0-9]+(?:[-'’][A-Za-z0-9]+)*", plain))
message = f'{count} words (prose, headings, captions, and table; excluding mathematics, references, title metadata, and text embedded in figures).\n'
(ROOT / 'WORD_COUNT.txt').write_text(message)
print(message, end='')
