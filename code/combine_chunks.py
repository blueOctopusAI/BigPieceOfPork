import os
import json

JSON_DIR = "json_chunks"
combined_data = []  # or use a dict if you prefer: combined_data = {}

for filename in os.listdir(JSON_DIR):
    if filename.endswith(".json"):
        filepath = os.path.join(JSON_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            chunk_data = json.load(f)
            # Optional: Validate or normalize chunk_data here
            combined_data.append(chunk_data)  # If using a list
            
            # If using a dict keyed by chunk_id:
            # chunk_id = chunk_data["chunk_id"]
            # combined_data[chunk_id] = chunk_data

# Write out combined data to a single file
with open("combined.json", "w", encoding="utf-8") as outfile:
    json.dump(combined_data, outfile, indent=2, ensure_ascii=False)
