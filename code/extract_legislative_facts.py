import os
import re
import json

CHUNKS_DIR = "chunks"
OUTPUT_DIR = "json_chunks"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Regex patterns (heuristic examples, adjust as needed)
us_code_pattern = re.compile(r'\b\d+\s*U\.S\.C\.?\s*[\w\(\)\.\-]*', re.IGNORECASE)
public_law_pattern = re.compile(r'Public Law \d+–\d+', re.IGNORECASE)

# Funding pattern: lines with $, try to capture amount and purpose if on the same line
funding_pattern = re.compile(r'\$(?P<amount>[0-9,]+)(.*?)(?:until|to remain|for fiscal year|for FY|\n|$)', 
                           re.IGNORECASE)

# Dates & Deadlines: capture dates like "January 15, 2025" or "not later than January 15, 2025"
date_pattern = re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s*\d{4}', re.IGNORECASE)
not_later_than_pattern = re.compile(r'not later than\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s*\d{4}', re.IGNORECASE)

# Duties and Requirements: lines with "The Secretary", "The Administrator", "The Comptroller General"
duty_pattern = re.compile(r'(The Secretary of [A-Za-z&\s]+|The Secretary|The Administrator|The Comptroller General of the United States|The Director)\s+(shall|may|must)\s+(.*)', re.IGNORECASE)

# Programs and Entities: simplistic approach - look for phrases like "Department of...", "Office of...", "Administration", "Agency"
entity_pattern = re.compile(r'\b(Department of [A-Za-z\&\s]+|Office of [A-Za-z\&\s]+|Administration|Agency|Commission|Authority|Bureau|Inspector General)\b', re.IGNORECASE)

# Extract other legislative refs (Acts, e.g. "Robert T. Stafford Disaster Relief and Emergency Assistance Act")
other_legislative_ref_pattern = re.compile(r'\b([A-Z][a-zA-Z\.]* [A-Z][a-zA-Z\.]* [A-Z][a-zA-Z\.]* (Act|Code))\b')

for filename in os.listdir(CHUNKS_DIR):
    if filename.endswith(".txt"):
        filepath = os.path.join(CHUNKS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        # Initialize the data structure
        data = {
            "chunk_id": filename.replace(".txt",""),
            "original_text": text,  # Store the original text content
            "references": {
                "us_code": [],
                "public_laws": [],
                "other_legislative_refs": []
            },
            "funding": [],
            "deadlines": [],
            "duties_and_requirements": [],
            "programs_and_entities": [],
            "dates": [],
            "other_facts": []
        }

        # Extract references
        us_codes = us_code_pattern.findall(text)
        if us_codes:
            data["references"]["us_code"].extend(list(set(us_codes)))

        pls = public_law_pattern.findall(text)
        if pls:
            data["references"]["public_laws"].extend(list(set(pls)))

        other_refs = other_legislative_ref_pattern.findall(text)
        # other_legislative_ref_pattern returns tuples due to the group (Act|Code), so extract first group only
        if other_refs:
            unique_other_refs = list(set([r[0] for r in other_refs]))
            data["references"]["other_legislative_refs"].extend(unique_other_refs)

        # Funding
        # We'll split by lines and try to parse funding line-by-line
        lines = text.split("\n")
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            fund_match = funding_pattern.search(line_stripped)
            if fund_match:
                amount = fund_match.group("amount")
                # Attempt to parse purpose from remainder of line after amount
                remainder = line_stripped[fund_match.end("amount"):]
                # Quick heuristic: look for "for XYZ" or mention of a program
                purpose = None
                availability = None
                
                # Check if line mentions "available until"
                if "until" in remainder.lower():
                    # Extract availability date if any
                    date_match = date_pattern.search(remainder)
                    if date_match:
                        availability = date_match.group(0)
                    else:
                        # If no specific date, just say "until" something else
                        availability = "unspecified extended availability"

                # Purpose: look for "for <program name>"
                purpose_match = re.search(r'for\s+([A-Za-z0-9,\-\s]+)', remainder, re.IGNORECASE)
                if purpose_match:
                    purpose = purpose_match.group(1).strip()

                data["funding"].append({
                    "amount": "$" + amount,
                    "purpose": purpose or "unspecified",
                    "availability": availability or "not specified",
                    "fiscal_years": []  # This would require extra logic if FY references appear
                })

            # Dates & Deadlines
            # Direct dates
            date_matches = date_pattern.findall(line_stripped)
            if date_matches:
                # date_pattern finds month in group(1), but we need full match
                # Use finditer for full matches:
                for m in date_pattern.finditer(line_stripped):
                    date_full = m.group(0)
                    if date_full not in data["dates"]:
                        data["dates"].append(date_full)

            # Deadlines (not later than)
            nl_match = not_later_than_pattern.search(line_stripped)
            if nl_match:
                deadline_date = nl_match.group(0).replace("not later than ", "").strip()
                data["deadlines"].append({
                    "action": "unknown action",  # Without deeper parsing, we don't know what action is due
                    "date": deadline_date
                })

            # Duties/Requirements
            duty_match = duty_pattern.search(line_stripped)
            if duty_match:
                entity = duty_match.group(1).strip()
                modal = duty_match.group(2).strip()
                action = duty_match.group(3).strip()
                data["duties_and_requirements"].append({
                    "entity": entity,
                    "action": action
                })

            # Programs/Entities
            entity_matches = entity_pattern.findall(line_stripped)
            if entity_matches:
                # Normalize casing and collect unique entities
                for e in entity_matches:
                    e_norm = e.strip()
                    if e_norm not in data["programs_and_entities"]:
                        data["programs_and_entities"].append(e_norm)

        # Write out JSON
        out_name = filename.replace(".txt", ".json")
        out_path = os.path.join(OUTPUT_DIR, out_name)
        with open(out_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=2, ensure_ascii=False)

print("Parsing complete. Check the 'json_chunks' directory for the JSON output files.")