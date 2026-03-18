#!/usr/bin/env python3
"""
PDF → Audiobook using Kokoro TTS (local)
Voice: am_fenrir (American male)
Usage: python3 scripts/convert.py
Run from: projects/audiobooks/logic-of-business-strategy/
"""

import re
import subprocess
import os
import sys
import numpy as np
import soundfile as sf

# --- Config ---
PDF_PATH   = "/Users/morriswong/Library/Mobile Documents/iCloud~com~apple~iBooks/Documents/The Logic of Business Strategy -- Henderson Bruce D_ -- Cambridge Mass United Kingdom 1986 -- HarperCollins Publishers -- 9780884109839 -- 757e193d2dfa0620ba755c11fa6ab00b -- Annas Archive.pdf"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')
VOICE      = 'am_fenrir'
LANG_CODE  = 'a'  # 'a' = American English, 'b' = British

# Sections: (name, start_line, end_line) — 1-indexed from pdftotext output
SECTIONS = [
    ('chapter1_concept_of_strategy', 329, 1449),
    # ('chapter1_strategic_sectors',   1449, 2000),  # uncomment to add more
]

SKIP_LINES = {'THE LOGIC OF BUSINESS STRATEGY', 'STRATEGIC CONCEPTS'}

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Extract full text ---
print('Extracting text from PDF...')
raw_txt = '/tmp/logic_raw.txt'
subprocess.run(['pdftotext', PDF_PATH, raw_txt], check=True)
with open(raw_txt) as f:
    all_lines = f.readlines()
print(f'Total lines: {len(all_lines)}')

# --- Tag types ---
SECTION_TITLE = 'section'
SUBSECTION    = 'subsection'
BLANK         = 'blank'
BODY          = 'body'
SKIP          = 'skip'

def clean_section(raw_lines):
    tagged = []
    for line in raw_lines:
        s = line.strip()
        if re.match(r'^\d+$', s):
            tagged.append((SKIP, ''))
        elif re.match(r'^[^a-zA-Z\s]*$', s) and s:
            tagged.append((SKIP, ''))
        elif s in SKIP_LINES:
            tagged.append((SKIP, ''))
        elif not s:
            tagged.append((BLANK, ''))
        elif re.match(r'^\d+\.\s+[A-Z][A-Z\s]+$', s):
            tagged.append((SECTION_TITLE, s))
        elif (2 <= len(s.split()) <= 7
              and not s.endswith(('.', ',', ';', ':'))
              and re.match(r'^[A-Z][a-z]+(\s+(of|the|and|in|a|an|to|for|with|by|on|at|from)|(\s+[A-Z][a-z]+))+$', s)):
            tagged.append((SUBSECTION, s))
        else:
            tagged.append((BODY, s))

    # Fix hyphenated line breaks
    merged = []
    i = 0
    while i < len(tagged):
        tag, content = tagged[i]
        if tag == BODY and content.endswith('-') and i + 1 < len(tagged):
            j = i + 1
            while j < len(tagged) and tagged[j][0] in (BLANK, SKIP):
                j += 1
            if j < len(tagged) and tagged[j][0] == BODY:
                merged.append((BODY, content[:-1] + tagged[j][1]))
                i = j + 1
                continue
        merged.append((tag, content))
        i += 1

    # Group into paragraphs
    paragraphs = []
    buf = []
    for tag, content in merged:
        if tag == SKIP:
            continue
        elif tag in (SECTION_TITLE, SUBSECTION):
            if buf:
                paragraphs.append((BODY, ' '.join(buf)))
                buf = []
            paragraphs.append((tag, content))
        elif tag == BLANK:
            if buf:
                paragraphs.append((BODY, ' '.join(buf)))
                buf = []
            paragraphs.append((BLANK, ''))
        else:
            if content:
                buf.append(content)
    if buf:
        paragraphs.append((BODY, ' '.join(buf)))

    # Merge short orphan fragments
    merged2 = []
    i = 0
    while i < len(paragraphs):
        tag, content = paragraphs[i]
        if (tag == BODY and len(content.split()) < 8
                and not content.endswith(('.', '?', '!', '"', '\u201d'))
                and i + 1 < len(paragraphs)):
            j = i + 1
            while j < len(paragraphs) and paragraphs[j][0] == BLANK:
                j += 1
            if j < len(paragraphs) and paragraphs[j][0] == BODY:
                paragraphs[j] = (BODY, content + ' ' + paragraphs[j][1])
                i += 1
                continue
        merged2.append((tag, content))
        i += 1
    paragraphs = merged2

    # Collapse consecutive blanks
    deduped = []
    for item in paragraphs:
        if item[0] == BLANK and deduped and deduped[-1][0] == BLANK:
            continue
        deduped.append(item)

    # Build TTS chunks split at section/subsection boundaries
    chunks = []
    current = []
    for tag, content in deduped:
        if tag in (SECTION_TITLE, SUBSECTION) and current:
            chunks.append(' '.join(current))
            current = [content + '.']
        elif tag == BLANK:
            current.append('')
        elif tag in (SECTION_TITLE, SUBSECTION):
            current.append(content + '.')
        else:
            current.append(content)
    if current:
        chunks.append(' '.join(current))

    return chunks

# --- Load Kokoro ---
print(f'Loading Kokoro pipeline (voice: {VOICE})...')
from kokoro import KPipeline
pipeline = KPipeline(lang_code=LANG_CODE)
silence = np.zeros(int(24000 * 0.6))  # 600ms between chunks

# --- Process sections ---
for name, start, end in SECTIONS:
    print(f'\nProcessing: {name} (lines {start}–{end})')
    raw = all_lines[start - 1:end - 1]
    chunks = clean_section(raw)
    print(f'  {len(chunks)} chunks')

    all_audio = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
        print(f'  Chunk {i+1}/{len(chunks)}...', end=' ', flush=True)
        audio_parts = [audio for _, _, audio in pipeline(chunk, voice=VOICE)]
        if audio_parts:
            all_audio.append(np.concatenate(audio_parts))
            all_audio.append(silence)
        print('done')

    final = np.concatenate(all_audio)
    out_path = os.path.join(OUTPUT_DIR, f'{name}_{VOICE}.wav')
    sf.write(out_path, final, 24000)
    duration = len(final) / 24000 / 60
    print(f'  Saved: {out_path} ({duration:.1f} min)')

print('\nAll done.')
