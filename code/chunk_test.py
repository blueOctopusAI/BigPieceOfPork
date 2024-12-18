import os
import json
import re

JSON_DIR = "json_chunks"

# Basic expectations:
# Set these to True if you expect at least one entry in that category.
must_have_data = {
    "references": True,  # expect at least one reference (us_code, public_laws, or other_legislative_refs)
    "funding": False,    # set to True if you always expect at least one funding entry
    "dates": False,
    "duties_and_requirements": False,
    "programs_and_entities": False,
    "deadlines": False,
    "other_facts": False
}

failures = []
success_count = 0

def has_meaningful_data(data):
    # Check references first if required
    if must_have_data["references"]:
        # Check if at least one reference array is non-empty
        if not (data["references"]["us_code"] or 
                data["references"]["public_laws"] or 
                data["references"]["other_legislative_refs"]):
            return False, "No references found, but references are required."

    # Check other required fields
    # For each field in must_have_data, if it's True, ensure there's at least one item
    # Funding, deadlines, duties_and_requirements, etc.
    for field in must_have_data:
        if field == "references":
            # Already checked above
            continue
        if must_have_data[field]:
            # Check if that field is non-empty
            if field in ["funding", "duties_and_requirements", "programs_and_entities", "dates", "deadlines", "other_facts"]:
                if len(data[field]) == 0:
                    return False, f"Expected {field} to have data, but it's empty."

    # If references are not required (or are empty), and all other fields are empty, we can warn.
    # This is a fallback if you want to ensure that the chunk isn't completely empty.
    if not must_have_data["references"]:
        # Check if references are also empty
        refs_empty = not (data["references"]["us_code"] or data["references"]["public_laws"] or data["references"]["other_legislative_refs"])
        # Check all other arrays
        all_empty = (refs_empty and 
                     len(data["funding"]) == 0 and
                     len(data["duties_and_requirements"]) == 0 and
                     len(data["programs_and_entities"]) == 0 and
                     len(data["dates"]) == 0 and
                     len(data["deadlines"]) == 0 and
                     len(data["other_facts"]) == 0)

        if all_empty:
            return False, "No meaningful data found in any category."

    return True, None

for filename in os.listdir(JSON_DIR):
    if filename.endswith(".json"):
        filepath = os.path.join(JSON_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Basic structural keys check
            required_keys = {
                "chunk_id",
                "references",
                "funding",
                "deadlines",
                "duties_and_requirements",
                "programs_and_entities",
                "dates",
                "other_facts"
            }
            if not required_keys.issubset(data.keys()):
                missing = required_keys - data.keys()
                failures.append((filename, f"Missing expected keys: {missing}"))
                continue
            
            # Check for presence of some data
            valid, msg = has_meaningful_data(data)
            if not valid:
                failures.append((filename, msg))
                continue

            success_count += 1
        
        except json.JSONDecodeError as e:
            failures.append((filename, f"JSON decode error: {str(e)}"))
        except Exception as e:
            failures.append((filename, f"Unexpected error: {str(e)}"))

# Report
print(f"Tested {success_count + len(failures)} files.")
if failures:
    print("The following files had issues:")
    for f, msg in failures:
        print(f"- {f}: {msg}")
else:
    print("All JSON files passed the data presence test!")
