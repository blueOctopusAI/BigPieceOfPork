import os
import sys
import json
import importlib.util
from typing import Dict, Optional, Any, List

class LegislativeProcessor:
    def __init__(self):
        self.config = self.load_config()
        self.ensure_directories()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration or create default if it doesn't exist."""
        config_path = "config.json"
        default_config = {
            "input_file": "raw_input.txt",
            "cleaned_file": "cleaned_output.txt",
            "chunks_dir": "chunks",
            "json_chunks_dir": "json_chunks",
            "output_dir": "output",
            "max_chars": 20000,
            "chunking_strategy": "size",  # Default strategy
            "script_paths": {
                "clean": "cleanText.py",
                "chunk": "chunk_legislation.py",
                "extract": "extract_legislative_facts.py"
            }
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    existing_config = json.load(f)
                # Merge existing config with defaults to ensure all keys exist
                merged_config = default_config.copy()
                merged_config.update(existing_config)
                # Save the merged config back to ensure new options are persisted
                with open(config_path, 'w') as f:
                    json.dump(merged_config, f, indent=2)
                return merged_config
            except json.JSONDecodeError:
                print("Error reading config file. Using defaults.")
                return default_config
        else:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
            
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            self.config["chunks_dir"],
            self.config["json_chunks_dir"],
            self.config["output_dir"]
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def get_chunking_options(self) -> Dict[str, Any]:
        """Get user preferences for chunking strategy."""
        options = {
            "strategy": self.config["chunking_strategy"],
            "max_chars": self.config["max_chars"]
        }

        print("\nCHUNKING STRATEGY OPTIONS")
        print("------------------------")
        print("Available strategies:")
        print("1. Size-based chunking (default)")
        print("   - Splits by maximum character count")
        print("   - Tries to maintain structural integrity")
        print("2. Structure-based chunking")
        print("   - Splits by DIVISION/TITLE markers")
        print("   - May result in larger chunks")

        choice = input("\nSelect chunking strategy (1-2) [1]: ").strip() or "1"

        if choice == "1":
            options["strategy"] = "size"
            size_choice = input(f"\nMax characters per chunk [{self.config['max_chars']}]: ").strip()
            if size_choice.isdigit():
                options["max_chars"] = int(size_choice)
        elif choice == "2":
            options["strategy"] = "structure"

        print("\nSelected options:")
        print(f"- Chunking strategy: {options['strategy']}")
        if options['strategy'] == 'size':
            print(f"- Max characters: {options['max_chars']}")

        confirm = input("\nProceed with these options? [Y/n]: ").strip().lower() or 'y'
        if confirm.startswith('n'):
            return self.get_chunking_options()

        # Update config with new options
        self.config["chunking_strategy"] = options["strategy"]
        self.config["max_chars"] = options["max_chars"]
        self.save_config()

        return options

    def save_config(self) -> None:
        """Save current configuration to file."""
        with open("config.json", 'w') as f:
            json.dump(self.config, f, indent=2)

    def modify_config(self) -> None:
        """Allow user to modify configuration settings."""
        print("\nCurrent Configuration:")
        # Filter out script_paths for simpler display
        display_config = {k: v for k, v in self.config.items() if k != "script_paths"}
        for key, value in display_config.items():
            print(f"{key}: {value}")

        print("\nWhich setting would you like to modify?")
        print("Available options:", ", ".join(display_config.keys()))
        setting = input("Enter setting name (or 'back' to return): ").strip()

        if setting.lower() == 'back':
            return

        if setting in display_config:
            new_value = input(f"Enter new value for {setting}: ").strip()
            # Handle numeric values
            if isinstance(self.config[setting], int):
                try:
                    new_value = int(new_value)
                except ValueError:
                    print("Invalid numeric value. Setting not updated.")
                    return

            self.config[setting] = new_value
            self.save_config()
            print(f"Updated {setting} to: {new_value}")
        else:
            print("Invalid setting name")

    def save_config(self) -> None:
        """Save current configuration to file."""
        with open("config.json", 'w') as f:
            json.dump(self.config, f, indent=2)

    def modify_config(self) -> None:
        """Allow user to modify configuration settings."""
        print("\nCurrent Configuration:")
        # Filter out script_paths for simpler display
        display_config = {k: v for k, v in self.config.items() if k != "script_paths"}
        for key, value in display_config.items():
            print(f"{key}: {value}")
        
        print("\nWhich setting would you like to modify?")
        print("Available options:", ", ".join(display_config.keys()))
        setting = input("Enter setting name (or 'back' to return): ").strip()
        
        if setting.lower() == 'back':
            return
            
        if setting in display_config:
            new_value = input(f"Enter new value for {setting}: ").strip()
            # Handle numeric values
            if isinstance(self.config[setting], int):
                try:
                    new_value = int(new_value)
                except ValueError:
                    print("Invalid numeric value. Setting not updated.")
                    return
            self.config[setting] = new_value
            self.save_config()
            print(f"Updated {setting} to: {new_value}")
        else:
            print("Invalid setting name")

    def run_script(self, script_name: str, options: Dict[str, Any] = None) -> None:
        """Run a Python script by importing it as a module."""
        script_path = self.config["script_paths"][script_name]
        if not os.path.exists(script_path):
            print(f"Error: Script {script_path} not found!")
            return
            
        try:
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            if spec is None or spec.loader is None:
                print(f"Error: Could not load {script_path}")
                return
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[script_name] = module
            spec.loader.exec_module(module)
            
            # If this is the chunking script, pass the strategy options
            if script_name == "chunk" and options:
                if hasattr(module, 'process_with_options'):
                    module.process_with_options(options)
                else:
                    print("Warning: Chunking script doesn't support strategy options")
                    module  # Run default behavior
            
            print(f"Successfully ran {script_path}")
        except Exception as e:
            print(f"Error running {script_path}: {str(e)}")

    def get_reconstruction_options(self) -> Dict[str, bool]:
        """Get user preferences for document reconstruction."""
        options = {
            "create_text": True,
            "create_json": True,
            "include_chunks": False,
            "include_original_text": False
        }
        
        print("\nRECONSTRUCTION OPTIONS")
        print("----------------------")
        print("Which output files would you like to create?")
        print("1. Text file only")
        print("2. JSON file only")
        print("3. Both files (default)")
        choice = input("Enter choice (1-3) [3]: ").strip() or "3"
        
        if choice == "1":
            options["create_json"] = False
        elif choice == "2":
            options["create_text"] = False
        
        if options["create_json"]:
            print("\nJSON Content Options:")
            include_chunks = input("Include original chunk data? (useful for testing) [y/N]: ").strip().lower()
            include_text = input("Include full text in JSON? (increases file size significantly) [y/N]: ").strip().lower()
            
            options["include_chunks"] = include_chunks.startswith('y')
            options["include_original_text"] = include_text.startswith('y')
        
        print("\nSelected options:")
        print(f"- Create text file: {options['create_text']}")
        print(f"- Create JSON file: {options['create_json']}")
        if options["create_json"]:
            print(f"- Include chunk data: {options['include_chunks']}")
            print(f"- Include full text: {options['include_original_text']}")
        
        confirm = input("\nProceed with these options? [Y/n]: ").strip().lower() or 'y'
        if confirm.startswith('n'):
            return self.get_reconstruction_options()
        
        return options

    def combine_json_data(self, json_files: List[str], json_dir: str, options: Dict[str, bool]) -> Dict:
        """Combine all JSON chunks into a single structured document."""
        combined_data = {
            "document_metadata": {
                "total_chunks": len(json_files),
                "chunking_strategy": self.config["chunking_strategy"]
            },
            "aggregated_data": {
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
        }
        
        # Only add these fields if requested
        if options["include_original_text"]:
            combined_data["full_text"] = ""
            full_text_parts = []
            
        if options["include_chunks"]:
            combined_data["chunks"] = []
        
        # Process each chunk
        for json_file in json_files:
            filepath = os.path.join(json_dir, json_file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    chunk_data = json.load(f)
                    
                # Handle text if needed
                if options["include_original_text"] and "original_text" in chunk_data:
                    full_text_parts.append(chunk_data["original_text"])
                    
                # Store chunk data if requested
                if options["include_chunks"]:
                    if not options["include_original_text"]:
                        # Remove original text to save space if not needed
                        chunk_data.pop("original_text", None)
                    combined_data["chunks"].append(chunk_data)
                
                # Aggregate references
                for ref_type in ["us_code", "public_laws", "other_legislative_refs"]:
                    combined_data["aggregated_data"]["references"][ref_type].extend(
                        chunk_data.get("references", {}).get(ref_type, [])
                    )
                
                # Aggregate other data types
                for data_type in ["funding", "deadlines", "duties_and_requirements", 
                                "dates", "other_facts"]:
                    combined_data["aggregated_data"][data_type].extend(
                        chunk_data.get(data_type, [])
                    )
                
                # Special handling for programs and entities - keep unique values
                if "programs_and_entities" in chunk_data:
                    current_entities = set(combined_data["aggregated_data"]
                        .get("programs_and_entities", []))
                    current_entities.update(chunk_data["programs_and_entities"])
                    combined_data["aggregated_data"]["programs_and_entities"] = \
                        list(current_entities)
                        
            except Exception as e:
                print(f"Error processing {json_file}: {str(e)}")
                continue
        
        # Remove duplicates from reference lists while preserving order
        for ref_type in combined_data["aggregated_data"]["references"]:
            combined_data["aggregated_data"]["references"][ref_type] = list(dict.fromkeys(
                combined_data["aggregated_data"]["references"][ref_type]
            ))
        
        # Add full text if requested
        if options["include_original_text"]:
            combined_data["full_text"] = "\n".join(full_text_parts)
        
        return combined_data

    def reconstruct_document(self, output_file: str = "reconstructed_document.txt", 
                           json_output: str = "combined_document.json") -> None:
        """Reconstruct documents based on user preferences."""
        json_dir = self.config["json_chunks_dir"]
        if not os.path.exists(json_dir):
            print("Error: JSON chunks directory not found!")
            return

        # Get user preferences for reconstruction
        options = self.get_reconstruction_options()

        def get_chunk_num(filename):
            base_name = os.path.splitext(filename)[0]
            num_str = base_name.split('_')[0] if '_' in base_name else base_name
            num_str = num_str.lstrip('0')
            try:
                return int(num_str) if num_str else 0
            except ValueError:
                return 0

        json_files = sorted([f for f in os.listdir(json_dir) if f.endswith('.json')],
                           key=get_chunk_num)
        
        if not json_files:
            print("No JSON files found to reconstruct!")
            return

        # Always process JSON data for text reconstruction
        print("Processing chunks...")
        combined_data = self.combine_json_data(json_files, json_dir, options)
        
        # Create requested output files
        if options["create_json"]:
            json_path = os.path.join(self.config["output_dir"], json_output)
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(combined_data, f, indent=2, ensure_ascii=False)
                print(f"Successfully wrote combined JSON to: {json_path}")
            except Exception as e:
                print(f"Error writing combined JSON: {str(e)}")
        
        if options["create_text"]:
            text_path = os.path.join(self.config["output_dir"], output_file)
            try:
                with open(text_path, 'w', encoding='utf-8') as f:
                    if options["include_original_text"]:
                        f.write(combined_data["full_text"])
                    else:
                        # If we didn't keep full text in JSON, read it again
                        text_parts = []
                        for json_file in json_files:
                            filepath = os.path.join(json_dir, json_file)
                            with open(filepath, 'r', encoding='utf-8') as jf:
                                chunk_data = json.load(jf)
                                if "original_text" in chunk_data:
                                    text_parts.append(chunk_data["original_text"])
                        f.write("\n".join(text_parts))
                print(f"Successfully wrote reconstructed text to: {text_path}")
            except Exception as e:
                print(f"Error writing reconstructed text: {str(e)}")

    def check_input_file(self) -> bool:
        """Check if input file exists."""
        if not os.path.exists(self.config["input_file"]):
            print(f"Error: Input file {self.config['input_file']} not found!")
            return False
        return True

    def process_all(self) -> None:
        """Run all processing steps in sequence."""
        if not self.check_input_file():
            return

        # Get chunking options first
        chunking_options = self.get_chunking_options()
            
        steps = ["clean", "chunk", "extract"]
        for step in steps:
            print(f"\nRunning {step} step...")
            if step == "chunk":
                self.run_script(step, chunking_options)
            else:
                self.run_script(step)

        print("\nReconstructing final document...")
        self.reconstruct_document()

    def edit_scripts(self) -> None:
        """Allow user to edit the script files."""
        import subprocess
        
        print("\nAvailable scripts:")
        for idx, (name, path) in enumerate(self.config["script_paths"].items(), 1):
            print(f"{idx}. {name}: {path}")
        
        choice = input("\nEnter script number to edit (or 'back' to return): ").strip()
        
        if choice.lower() == 'back':
            return
            
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(self.config["script_paths"]):
                print("Invalid script number")
                return
                
            script_name = list(self.config["script_paths"].keys())[idx]
            script_path = self.config["script_paths"][script_name]
            
            # Try to use the default system editor
            if sys.platform.startswith('win'):
                os.system(f'notepad "{script_path}"')
            else:
                editor = os.getenv('EDITOR', 'nano')  # Default to nano if EDITOR not set
                subprocess.call([editor, script_path])
                
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"Error opening editor: {str(e)}")

    def show_menu(self) -> None:
        """Display the main menu and handle user input."""
        while True:
            print("\n=== Legislative Text Processor ===")
            print("1. Run all processing steps")
            print("2. Clean text only")
            print("3. Chunk text only")
            print("4. Extract facts only")
            print("5. Reconstruct document from chunks")
            print("6. Modify configuration")
            print("7. View current configuration")
            print("8. Edit script files")
            print("9. Exit")
            
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == '1':
                self.process_all()
            elif choice == '2':
                if self.check_input_file():
                    self.run_script("clean")
            elif choice == '3':
                if os.path.exists(self.config["cleaned_file"]):
                    chunking_options = self.get_chunking_options()
                    self.run_script("chunk", chunking_options)
                else:
                    print("Error: Cleaned file not found. Run cleaning step first.")
            elif choice == '4':
                if os.path.exists(self.config["chunks_dir"]):
                    self.run_script("extract")
                else:
                    print("Error: Chunks directory not found. Run chunking step first.")
            elif choice == '5':
                self.reconstruct_document()
            elif choice == '6':
                self.modify_config()
            elif choice == '7':
                print("\nCurrent Configuration:")
                print(json.dumps(self.config, indent=2))
            elif choice == '8':
                self.edit_scripts()
            elif choice == '9':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

def main():
    processor = LegislativeProcessor()
    processor.show_menu()

if __name__ == "__main__":
    main()