import re

input_file = "raw_input.txt"
output_file = "cleaned_output.txt"

with open(input_file, "r", encoding="utf-8") as infile:
    text = infile.read()

# ============================================================
# PHASE 1: Remove known extraneous lines and references
# ============================================================
# Regex patterns for lines we want to remove entirely:
# - Standalone numeric lines (just a number or number with commas)
standalone_number_line = re.compile(r'^\s*\d+(\s*,\s*\d+)*\s*$', re.MULTILINE)

# - Fully qualified paths or XML references lines:
# Example: "l:\v7\121724\7121724.012.xml (955033|8)"
xml_reference_line = re.compile(r'^\s*[A-Za-z]:\\.*\.xml\s*\(\d+\|\d+\)\s*$', re.MULTILINE)
mixed_xml_ref = re.compile(r'^\s*\d*,\s*[A-Za-z]:\\.*\.xml\s*\(\d+\|\d+\)\s*$', re.MULTILINE)
parenthetical_pattern_line = re.compile(r'^\s*.*\(\d+\|\d+\).*$\n?', re.MULTILINE)

# - Timestamp lines (e.g., "December 17, 2024 (5:46 p.m.)")
timestamp_line = re.compile(
    r'^\w+\s+\d{1,2},\s+\d{4}\s*\(\d{1,2}:\d{2}\s*[ap]\.m\.\).*$',
    re.MULTILINE
)

# - VerDate and Jkt lines, as well as lines starting with a drive letter or path
verdate_line = re.compile(r'^VerDate.*$', re.MULTILINE)
jkt_line = re.compile(r'^.*Jkt.*$', re.MULTILINE)
filepath_line = re.compile(r'^[A-Z]:\\.*$', re.MULTILINE)

# Remove these known extraneous lines
text = standalone_number_line.sub('', text)
text = timestamp_line.sub('', text)
text = verdate_line.sub('', text)
text = jkt_line.sub('', text)
text = filepath_line.sub('', text)
text = xml_reference_line.sub('', text)
text = mixed_xml_ref.sub('', text)
text = parenthetical_pattern_line.sub('', text)

# ============================================================
# PHASE 2: Clean line numbers and artifacts within lines
# ============================================================
lines = text.split('\n')
cleaned_lines = []

# Regex to remove line numbers at the start of lines (e.g., "3 " or "10 ")
start_line_number = re.compile(r'^\s*\d+\s+')

for line in lines:
    original_line = line.strip()
    if not original_line:
        continue

    # Remove leading line numbers
    line = start_line_number.sub('', original_line)

    # Some artifacts may have inserted numbers in the middle of words:
    # Pattern: word + digit(s) + space + next part of word
    # For example: "strate2 gies" -> "strate gies"
    # We'll try to fix this by matching a letter sequence, digits, a space, then letters.
    # We must be careful not to remove actual references.
    # Let's start simple: replace patterns like "([a-zA-Z])(\d+)\s+([a-zA-Z])" with "\1\3"
    # This is a heuristic. If it removes too much or merges words incorrectly,
    # it can be refined or removed.
    embedded_number_pattern = re.compile(r'([A-Za-z])(\d+)\s+([A-Za-z])')
    line = embedded_number_pattern.sub(r'\1\3', line)

    # If line ends up empty after processing, skip
    if not line.strip():
        continue

    cleaned_lines.append(line)

cleaned_text = '\n'.join(cleaned_lines)

# ============================================================
# PHASE 3: Final normalization
# ============================================================
# Further normalization if needed. For now, we'll just ensure no extra spaces.
cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
cleaned_text = re.sub(r'\n\s*\n+', '\n\n', cleaned_text).strip()

with open(output_file, "w", encoding="utf-8") as outfile:
    outfile.write(cleaned_text)

print("Cleaning complete. Check 'cleaned_output.txt' for results.")