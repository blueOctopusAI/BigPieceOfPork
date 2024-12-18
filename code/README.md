#Some of this may be out of date and some of the code may not work
#Use at your own discretion for now 12/18/24 =j

# Legislative Text Processor

A suite of Python scripts for processing, analyzing, and extracting information from legislative text documents.

## Overview

This system processes legislative documents through several stages:
1. Cleaning and normalizing the raw text
2. Splitting the text into manageable chunks
3. Extracting key information (references, dates, funding, etc.)
4. Reconstructing the processed document

## Requirements

- Python 3.6 or higher
- Required packages: None (uses standard library only)

## File Structure

```
legislative-processor/
├── legislative_processor.py     # Main control script
├── cleanText.py                # Text cleaning script
├── chunk_legislation.py        # Text chunking script
├── extract_legislative_facts.py # Fact extraction script
├── config.json                 # Configuration file
├── raw_input.txt              # Your input file goes here
└── README.md                  # This file
```

Generated directories:
```
legislative-processor/
├── chunks/         # Contains chunked text files
├── json_chunks/    # Contains extracted data in JSON format
└── output/         # Contains final reconstructed document
```

## Setup

1. Clone or download this repository
2. Place your legislative text file in the directory as `raw_input.txt`
3. Run `legislative_processor.py`

## Usage

Run the main control script:
```bash
python legislative_processor.py
```

The menu provides the following options:
1. Run all processing steps
2. Clean text only
3. Chunk text only
4. Extract facts only
5. Reconstruct document from chunks
6. Modify configuration
7. View current configuration
8. Edit script files
9. Exit

### Configuration

Default settings can be modified through the menu or by editing `config.json`:
- `input_file`: Name of raw input file
- `cleaned_file`: Name of cleaned output file
- `chunks_dir`: Directory for text chunks
- `json_chunks_dir`: Directory for JSON data
- `output_dir`: Directory for final output
- `max_chars`: Maximum characters per chunk

## Process Details

### 1. Text Cleaning (cleanText.py)
- Removes extraneous markup and formatting
- Normalizes line endings and spaces
- Removes timestamps, version numbers, and other artifacts
- Outputs cleaned text to `cleaned_output.txt`

### 2. Chunking (chunk_legislation.py)
- Splits text into manageable chunks based on divisions and titles
- Maintains document structure
- Creates numbered chunk files
- Handles size limits and pagination

### 3. Fact Extraction (extract_legislative_facts.py)
Extracts and structures:
- US Code references
- Public Law references
- Funding amounts and purposes
- Dates and deadlines
- Duties and requirements
- Program and entity mentions

### 4. Document Reconstruction
- Preserves original text formatting
- Maintains document structure
- Creates a complete, processed document

## Error Handling

The system includes checks for:
- Missing input files
- Directory access
- File permissions
- Processing errors
- JSON validation

## Notes

- Keep original input file as backup
- Process may take time for large documents
- JSON files contain both structured data and original text
- Error messages will guide through common issues