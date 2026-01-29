
import os
import sys
import csv
import time
import struct
import argparse

# Try to import colorama
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback colors (ANSI codes)
    class Fore:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        MAGENTA = '\033[95m'
        RESET = '\033[0m'
    class Style:
        RESET_ALL = '\033[0m'
        BRIGHT = '\033[1m'

# Try to import paramiko
try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

# Try to import deep_translator
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

# --- Color Functions ---

def print_error(msg):
    """Print error message in red"""
    if COLORAMA_AVAILABLE:
        print(f"{Fore.RED}{msg}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}{msg}{Fore.RESET}")

def print_success(msg):
    """Print success message in green"""
    if COLORAMA_AVAILABLE:
        print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}{msg}{Fore.RESET}")

def print_warning(msg):
    """Print warning message in yellow"""
    if COLORAMA_AVAILABLE:
        print(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}{msg}{Fore.RESET}")

def print_info(msg):
    """Print info message in cyan"""
    if COLORAMA_AVAILABLE:
        print(f"{Fore.CYAN}{msg}{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}{msg}{Fore.RESET}")

def print_header(msg):
    """Print header message in blue/bright"""
    if COLORAMA_AVAILABLE:
        print(f"{Fore.BLUE}{Style.BRIGHT}{msg}{Style.RESET_ALL}")
    else:
        print(f"{Fore.BLUE}{Style.BRIGHT}{msg}{Fore.RESET}")

# --- IP Configuration Management ---

def get_config_path():
    """Get path to config file"""
    work_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(work_dir, ".printer_config.txt")

def save_printer_ip(ip):
    """Save printer IP to config file"""
    try:
        with open(get_config_path(), 'w') as f:
            f.write(ip)
    except Exception:
        pass  # Fail silently

def load_printer_ip():
    """Load printer IP from config file"""
    try:
        config_path = get_config_path()
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                ip = f.read().strip()
                if ip:
                    return ip
    except Exception:
        pass
    return None

def get_printer_ip(prompt="Enter Printer IP Address"):
    """Get printer IP with saved default"""
    saved_ip = load_printer_ip()
    
    if saved_ip:
        user_input = input(f"\n{prompt} [{saved_ip}]: ").strip()
        ip = user_input if user_input else saved_ip
    else:
        ip = input(f"\n{prompt}: ").strip()
    
    if ip:
        save_printer_ip(ip)
    
    return ip

# --- Helper Functions for Packing/Unpacking ---

def pack_csv_to_bin(csv_path, bin_path):
    print_info(f"Packing {csv_path} to {bin_path}...")
    rows = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                rows.append(row)
    except Exception as e:
        print_error(f"Error reading CSV for packing: {e}")
        return False

    if not rows:
        print_error("Error: Empty CSV")
        return False

    header_row = rows[0]
    data_rows = rows[1:]
    
    # Col 0: ID, Col 1: Aux, Col 2+: Languages
    num_cols = len(header_row)
    lang_count = num_cols - 2
    str_count = len(data_rows)
    
    print_info(f"Detected {lang_count} languages, {str_count} strings.")
    
    header_fixed_size = 0x0F
    offset_list_size = lang_count * 4
    lang_table_size = str_count * 8
    
    current_table_offset = header_fixed_size + offset_list_size
    blob_start_offset = current_table_offset + (lang_count * lang_table_size)
    current_string_offset = blob_start_offset
    
    offset_list = [] 
    lang_tables_bytes = bytearray()
    string_blob = bytearray()
    
    for lang_idx in range(lang_count):
        col_idx = lang_idx + 2
        
        this_table_start = current_table_offset
        offset_list.append(this_table_start)
        current_table_offset += lang_table_size
        
        for row in data_rows:
            if col_idx < len(row):
                text = row[col_idx]
            else:
                text = ""
                
            text_bytes = text.encode('utf-8') + b'\x00'
            length = len(text_bytes)
            
            string_blob.extend(text_bytes)
            
            entry = struct.pack('<II', current_string_offset, length)
            lang_tables_bytes.extend(entry)
            
            current_string_offset += length
            
    # Magic 00 10 FD 12
    magic = bytes.fromhex("0010FD12")
    total_size = 15 + offset_list_size + len(lang_tables_bytes) + len(string_blob)
    
    header = bytearray()
    header.extend(magic)
    header.extend(struct.pack('<I', total_size - 14)) 
    header.extend(b'\x00\x00') # 0x08
    header.extend(b'\x01')     # 0x0A
    header.extend(struct.pack('B', lang_count)) # 0x0B
    header.extend(struct.pack('<H', str_count)) # 0x0C
    header.extend(b'\x00')     # 0x0E
    
    offset_bytes = bytearray()
    for off in offset_list:
        offset_bytes.extend(struct.pack('<I', off))
        
    try:
        with open(bin_path, 'wb') as f:
            f.write(header)
            f.write(offset_bytes)
            f.write(lang_tables_bytes)
            f.write(string_blob)
        print_success("Packing successful.")
        return True
    except Exception as e:
        print_error(f"Error writing BIN: {e}")
        return False

# --- Core Functionality ---

def fetch_printer_files():
    if not PARAMIKO_AVAILABLE:
        print_error("\nError: 'paramiko' module not installed. Run 'pip install paramiko' to use this feature.")
        return

    ip = get_printer_ip()
    if not ip: return

    username = "root"
    password = "OpenCentauri"
    remote_dir = "/app/resources"
    local_dir = os.path.dirname(os.path.abspath(__file__))
    
    print_info(f"Connecting to {ip}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        sftp = ssh.open_sftp()
        
        for filename in ["translation.csv", "translation.bin"]:
            remote_path = f"{remote_dir}/{filename}"
            local_path = os.path.join(local_dir, filename)
            try:
                sftp.get(remote_path, local_path)
                print_success(f"Downloaded: {filename}")
            except Exception as e:
                print_error(f"Failed to download {filename}: {e}")
        
        sftp.close()
        ssh.close()
        print_success("Download complete.")
        
        # Auto-extract texts after download
        extract_texts_from_csv()
        
    except Exception as e:
        print_error(f"Connection failed: {e}")

def extract_texts_from_csv():
    work_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(work_dir, "translation.csv")
    
    if not os.path.exists(csv_path):
        print_error(f"Error: {csv_path} not found. Fetch files first.")
        return

    print_info("\nExtracting texts from translation.csv...")
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            rows = list(reader)
    except Exception as e:
        print_error(f"Error reading CSV: {e}")
        return

    # Extract Chinese (Lang 1 -> Col 2)
    zh_path = os.path.join(work_dir, "chinese.txt")
    with open(zh_path, 'w', encoding='utf-8') as f:
        for row in rows[1:]: # Skip header
             f.write((row[2] if len(row) > 2 else "") + '\n')
    print_success(f"Generated: chinese.txt")

    # Extract English (Lang 2 -> Col 3) and Patch
    en_path = os.path.join(work_dir, "english.txt")
    
    # Patch logic
    patches = [
        "Camera connection error, time-lapse generation failed",
        "Clog detection recovering...",
        "Possible nozzle clog or filament tangle detected. Please check machine status."
    ]
    patch_cursor = 0
    
    with open(en_path, 'w', encoding='utf-8') as f:
        for row in rows[1:]:
            en_text = row[3] if len(row) > 3 else ""
            if not en_text.strip() and patch_cursor < len(patches):
                en_text = patches[patch_cursor]
                patch_cursor += 1
            f.write(en_text + '\n')
            
    print_success(f"Generated: english.txt (with {patch_cursor} patches)")

def auto_translate_file():
    if not TRANSLATOR_AVAILABLE:
        print_error("\nError: 'deep-translator' module not installed. Run 'pip install deep-translator' to use this feature.")
        return

    work_dir = os.path.dirname(os.path.abspath(__file__))
    source_file = os.path.join(work_dir, "english.txt")
    
    if not os.path.exists(source_file):
        print_error("english.txt not found. Please regenerate text files first (Option 2).")
        return

    print_header("\n--- Auto Translation (Google Translate) ---")
    target_lang = input("Enter target language code (e.g. 'pl' for Polish, 'es' for Spanish): ").strip()
    if not target_lang: return

    output_filename = input(f"Enter output filename (default: {target_lang}.txt): ").strip()
    if not output_filename:
        output_filename = f"{target_lang}.txt"
        
    output_path = os.path.join(work_dir, output_filename)
    
    print_info(f"Reading {source_file}...")
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f]

    print_info(f"Translating {len(lines)} lines to '{target_lang}'... This may take a moment.")
    
    translated_lines = []
    translator = GoogleTranslator(source='auto', target=target_lang)
    
    # Process in chunks to avoid generic errors or limits if possible, 
    # though deep_translator handles simple batching well.
    # We need to preserve empty lines.
    
    # Batch strategy: Collect non-empty indices
    indices_to_translate = []
    texts_to_translate = []
    
    for i, line in enumerate(lines):
        if line:
            indices_to_translate.append(i)
            texts_to_translate.append(line)
        else:
            # placeholders
            pass
            
    # Translate batch
    # Split big batch into smaller chunks (e.g. 50 lines) to be safe and show progress
    batch_size = 50
    total_batches = (len(texts_to_translate) + batch_size - 1) // batch_size
    
    translated_texts = []
    
    try:
        for b in range(total_batches):
            start = b * batch_size
            end = start + batch_size
            chunk = texts_to_translate[start:end]
            
            print_info(f"Translating batch {b+1}/{total_batches}...")
            # translate_batch method
            results = translator.translate_batch(chunk)
            translated_texts.extend(results)
            time.sleep(0.5) # gentle delay
            
    except Exception as e:
        print_error(f"Translation failed: {e}")
        return

    # Reassemble
    result_lines = [""] * len(lines)
    
    for i, idx in enumerate(indices_to_translate):
        if i < len(translated_texts):
            # Handle potential None return from translator
            trans = translated_texts[i]
            result_lines[idx] = trans if trans is not None else "[TRANSLATION FAILED]"
        else:
            result_lines[idx] = "[TRANSLATION ERROR]"

    # Write
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in result_lines:
            # Final safety check
            if line is None: line = ""
            f.write(line + '\n')
            
    print_success(f"\nSaved translation to: {output_filename}")
    print_info("You can now verify this file and use Option 3 to build the binary.")

def add_language():
    work_dir = os.path.dirname(os.path.abspath(__file__))
    base_csv = os.path.join(work_dir, "translation.csv")
    
    if not os.path.exists(base_csv):
        print_error("Error: translation.csv not found.")
        return

    lang_name = input("\nEnter new language name for header (e.g. Polski): ").strip()
    if not lang_name: return
    
    filename = input(f"Enter filename with translations (e.g. pl.txt): ").strip()
    file_path = os.path.join(work_dir, filename)
    
    if not os.path.exists(file_path):
        print_error(f"Error: {filename} not found.")
        return

    print_info(f"Reading {filename}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        new_lines = [l.strip() for l in f]

    # Read base CSV
    with open(base_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)

    header = rows[0]
    data = rows[1:]

    # Validate length
    if len(new_lines) < len(data):
        print_warning(f"Warning: {filename} has {len(new_lines)} lines, expected {len(data)}. Padding with empty strings.")
        new_lines.extend([""] * (len(data) - len(new_lines)))
    elif len(new_lines) > len(data):
         print_warning(f"Warning: {filename} has extra lines. Truncating.")
         new_lines = new_lines[:len(data)]

    # INSERT before the last column (结束列) instead of appending
    # The last column is typically a technical marker column
    print_info(f"\nCurrent header has {len(header)} columns")
    print_info(f"Last column name: '{header[-1]}'")
    
    # Insert new language BEFORE the last column
    header.insert(-1, lang_name)
    
    for i in range(len(data)):
        # Insert new translation BEFORE the last column
        data[i].insert(-1, new_lines[i])
    
    print_info(f"New header has {len(header)} columns")
    print_success(f"New language '{lang_name}' inserted before '{header[-1]}'")

    # Save to translation_updated.csv
    out_csv = os.path.join(work_dir, "translation_updated.csv")
    out_bin = os.path.join(work_dir, "translation_updated.bin")

    all_rows = [header] + data
    
    try:
        with open(out_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(all_rows)
        print_success(f"\nCreated: {out_csv}")
    except Exception as e:
        print_error(f"Error saving CSV: {e}")
        return

    # Build BIN
    if pack_csv_to_bin(out_csv, out_bin):
        print_success(f"Created: {out_bin}")
        print_success("\nSUCCESS! Now you can upload translation_updated.bin and .csv to the printer (Option 7).")

def replace_language():
    """Replace an existing language column with new translations"""
    work_dir = os.path.dirname(os.path.abspath(__file__))
    base_csv = os.path.join(work_dir, "translation.csv")
    
    if not os.path.exists(base_csv):
        print_error("Error: translation.csv not found.")
        return

    # Read CSV to show available languages
    with open(base_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)

    header = rows[0]
    data = rows[1:]

    # Show available languages (skip first 2 columns and last column)
    # Format: ID | Size | Chinese | English | ... | End
    print_header("\n=== Available Languages ===")
    
    # Map Chinese names to English for easier selection
    lang_map = {
        "简体中文": "Chinese (Simplified)",
        "英语": "English",
        "西班牙语": "Spanish",
        "法语": "French",
        "意大利语": "Italian",
        "俄语": "Russian",
        "德语": "German",
        "日语": "Japanese",
        "韩语": "Korean",
        "土耳其语": "Turkish",
        "乌克兰语": "Ukrainian"
    }
    
    languages = []
    for i, col_name in enumerate(header):
        # Skip: 字符串序号, 字号大小, and 结束列
        if i >= 2 and i < len(header) - 1:
            display_name = lang_map.get(col_name, col_name)
            languages.append((i, col_name, display_name))
            print_info(f"{len(languages)}. {display_name} ({col_name})")
    
    if not languages:
        print_error("No languages found to replace!")
        return
    
    # User selects which language to replace
    try:
        choice = int(input(f"\nWhich language to REPLACE (1-{len(languages)}): ").strip())
        if choice < 1 or choice > len(languages):
            print_error("Invalid choice.")
            return
        
        target_idx, original_name, display_name = languages[choice - 1]
        print_info(f"You selected: {display_name} (column {target_idx})")
        
    except ValueError:
        print_error("Invalid input.")
        return
    
    # Get new language name
    new_lang_name = input(f"\nEnter NEW language name to replace '{display_name}' (e.g., Polski): ").strip()
    if not new_lang_name:
        return
    
    # Get translation file
    filename = input(f"Enter filename with translations (e.g., pl.txt): ").strip()
    file_path = os.path.join(work_dir, filename)
    
    if not os.path.exists(file_path):
        print_error(f"Error: {filename} not found.")
        return

    print_info(f"Reading {filename}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        new_lines = [l.strip() for l in f]

    # Validate length
    if len(new_lines) < len(data):
        print_warning(f"Warning: {filename} has {len(new_lines)} lines, expected {len(data)}. Padding with empty strings.")
        new_lines.extend([""] * (len(data) - len(new_lines)))
    elif len(new_lines) > len(data):
         print_warning(f"Warning: {filename} has extra lines. Truncating.")
         new_lines = new_lines[:len(data)]

    # Replace the column
    header[target_idx] = new_lang_name
    for i in range(len(data)):
        # Safety check: some rows might be shorter than the header due to missing trailing tabs
        while len(data[i]) <= target_idx:
            data[i].append("")
        data[i][target_idx] = new_lines[i]
    
    print_success(f"\n✓ Replaced '{display_name}' with '{new_lang_name}'")

    # Save to translation_updated.csv
    out_csv = os.path.join(work_dir, "translation_updated.csv")
    out_bin = os.path.join(work_dir, "translation_updated.bin")

    all_rows = [header] + data
    
    try:
        with open(out_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(all_rows)
        print_success(f"Created: {out_csv}")
    except Exception as e:
        print_error(f"Error saving CSV: {e}")
        return

    # Build BIN
    if pack_csv_to_bin(out_csv, out_bin):
        print_success(f"Created: {out_bin}")
        print_success("\nSUCCESS! Now you can upload translation_updated.bin and .csv to the printer (Option 7).")

# --- Menu ---

def main():
    while True:
        print_header("\n=== ELEGOO Translation Tool by Czajo===")
        print_info("1. Fetch files from Printer - UI Files (BIN/CSV)")
        print_info("2. Regenerate chinese.txt / english.txt from local CSV")
        print_info("3. Replace Existing Language (Recommended) - Overwrites column")
        print_info("4. Add New Language (Manual) - Appends column (limit 12)")
        print_info("5. Generate Auto-Translation to target language (.txt)")
        print_info("6. Fetch files from Printer - Web Interface (JSON)")
        print_info("7. Translate Web Interface JSON")
        print_info("8. Upload to Printer - UI Files (translation.bin)")
        print_info("9. Upload to Printer - Web Files (network-en.json)")
        print_info("10. Patch Web Language Button (English → Your Language) 😎")
        print_info("11. Reboot Printer 🔄")
        print_info("12. List Printer Files (Diagnostic) 🔍")
        print_info("13. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            fetch_printer_files()
        elif choice == '2':
            extract_texts_from_csv()
        elif choice == '3':
            replace_language()
        elif choice == '4':
            add_language()
        elif choice == '5':
            auto_translate_file()
        elif choice == '6':
            fetch_web_files()
        elif choice == '7':
            translate_web_json()
        elif choice == '8':
            upload_ui_files()
        elif choice == '9':
            upload_web_files()
        elif choice == '10':
            patch_web_language_button()
        elif choice == '11':
            reboot_printer()
        elif choice == '12':
            list_printer_files()
        elif choice == '13':
            break
        else:
            print_error("Invalid option.")

# --- Web Interface Functions ---

def fetch_web_files():
    if not PARAMIKO_AVAILABLE:
        print_error("\nError: 'paramiko' module not installed.")
        return

    ip = get_printer_ip()
    if not ip: return

    username = "root"
    password = "OpenCentauri"
    remote_path = "/app/resources/www/assets/i18n/network-en.json"
    
    work_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(work_dir, "web_i18n")
    if not os.path.exists(web_dir):
        os.makedirs(web_dir)
        
    local_path = os.path.join(web_dir, "network-en.json")
    
    print_info(f"Connecting to {ip}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        sftp = ssh.open_sftp()
        
        try:
            sftp.get(remote_path, local_path)
            print_success(f"Downloaded: {local_path}")
        except Exception as e:
            print_error(f"Failed to download web json: {e}")
            
        sftp.close()
        ssh.close()
        
    except Exception as e:
        print_error(f"Connection failed: {e}")

def translate_web_json():
    if not TRANSLATOR_AVAILABLE:
        print_error("\nError: 'deep-translator' module not installed.")
        return
        
    work_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(work_dir, "web_i18n")
    source_file = os.path.join(web_dir, "network-en.json")
    
    if not os.path.exists(source_file):
        print_error("Error: web_i18n/network-en.json not found. Fetch it first (Option 5).")
        return
        
    import json
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print_error(f"Error parsing JSON: {e}")
        return
        
    print_info(f"Loaded {len(data)} keys from JSON.")
    
    print_header("\n--- Auto Translate Web JSON ---")
    print_info("This will translate the values in network-en.json and save a NEW file.")
    target_lang = input("Enter target language code (e.g. 'pl'): ").strip()
    if not target_lang: return
    
    translator = GoogleTranslator(source='auto', target=target_lang)
    
    # JSON structure is typically Key: Value. Nested?
    # Angular i18n files are often flat or nested.
    # We need a recursive translation function or simple iteration if flat.
    # Let's assume potentially nested.
    
    translated_count = 0
    total_count = 0
    
    def recursive_translate(obj):
        nonlocal translated_count, total_count
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                new_obj[k] = recursive_translate(v)
            return new_obj
        elif isinstance(obj, list):
            return [recursive_translate(x) for x in obj]
        elif isinstance(obj, str):
            total_count += 1
            if obj.strip():
                try:
                    res = translator.translate(obj)
                    if res:
                        translated_count += 1
                        print_info(f"Translated: {obj[:20]}... -> {res[:20]}...")
                        return res
                except Exception as e:
                    print_error(f"Error translating '{obj}': {e}")
            return obj
        else:
            return obj

    print_info("Starting translation... this might take a while.")
    
    # To speed up, we could batch texts, but JSON structure makes batching tricky 
    # without flattening and unflattening.
    # For a few hundred keys, sequential is okay-ish.
    
    new_data = recursive_translate(data)
    
    output_filename = f"network-en_patched_with_{target_lang}.json"
    output_path = os.path.join(web_dir, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)
        
    print_success(f"\nSaved translated JSON to: {output_path}")
    print_success(f"Translated {translated_count}/{total_count} strings.")
    print_info("You can now use Option 8 to upload this file to the printer.")

# --- Upload Functions ---

def patch_web_language_button():
    """Podmienia 'English' na wybrany język w przycisku wyboru języka"""
    if not PARAMIKO_AVAILABLE:
        print_error("\nError: 'paramiko' module not installed.")
        return
    
    work_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(work_dir, "web_i18n")
    
    print_header("\n--- Patch Web Language Button ---")
    print_info("This is a 'sneaky' mod that changes the button text while keeping the 'en' language code.")
    
    # Ask for target language name
    target_lang = input("\nEnter language name to display (e.g., Polski, Español, Français): ").strip()
    if not target_lang:
        print_error("No language name provided.")
        return
    
    # First, fetch the JS file from printer
    ip = get_printer_ip()
    if not ip: return
    
    confirm = input(f"This will change 'English' → '{target_lang}'. Continue? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print_warning("Patch cancelled.")
        return

    username = "root"
    password = "OpenCentauri"
    
    # The file that contains the language list
    remote_js = "/app/resources/www/624.931d12e23af9a62e6007.js"
    
    # Create temp directory
    if not os.path.exists(web_dir):
        os.makedirs(web_dir)
    
    local_js = os.path.join(web_dir, "624.931d12e23af9a62e6007.js")
    
    print_info(f"\nConnecting to {ip}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        sftp = ssh.open_sftp()
        
        # Download JS
        print_info("Downloading JavaScript file...")
        try:
            sftp.get(remote_js, local_js)
            print_success(f"Downloaded: {os.path.basename(local_js)}")
        except Exception as e:
            print_error(f"Failed to download: {e}")
            sftp.close()
            ssh.close()
            return
        
        sftp.close()
        ssh.close()
        
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return
    
    # Patch the file
    print_info("\nPatching JavaScript...")
    try:
        with open(local_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace English with target language
        original = 'new a("en","English")'
        patched = f'new a("en","{target_lang}")'
        
        if original in content:
            content = content.replace(original, patched)
            print_success(f"✓ Patched: 'English' → '{target_lang}'")
        else:
            print_warning("Warning: Original pattern not found. File may have been updated.") 
            ask = input("Continue anyway? (yes/no): ").strip().lower()
            if ask not in ['yes', 'y']:
                return
        
        # Save patched file
        patched_path = os.path.join(web_dir, "624.931d12e23af9a62e6007_patched.js")
        with open(patched_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print_success(f"Saved patched file: {os.path.basename(patched_path)}")
        
    except Exception as e:
        print_error(f"Patching failed: {e}")
        return
    
    # Upload patched file
    upload = input("\nUpload patched file to printer? (yes/no): ").strip().lower()
    if upload not in ['yes', 'y']:
        print_warning("Upload skipped. You can manually upload the patched file later.")
        return
    
    print_info(f"\nConnecting to {ip} for upload...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        sftp = ssh.open_sftp()
        
        # Backup
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_backup = f"/app/resources/www/624.931d12e23af9a62e6007.js.backup_{timestamp}"
        
        print_info("Creating backup...")
        try:
            stdin, stdout, stderr = ssh.exec_command(f"cp {remote_js} {remote_backup}")
            stdout.channel.recv_exit_status()
            print_success(f"Backed up: 624.931d12e23af9a62e6007.js.backup_{timestamp}")
        except Exception as e:
            print_warning(f"Warning: Could not backup: {e}")
        
        # Upload
        print_info("\nUploading patched file...")
        try:
            remote_temp = f"/app/resources/www/624.931d12e23af9a62e6007.js.tmp"
            sftp.put(patched_path, remote_temp)
            print_success("Uploaded to temporary location")
            
            # Rename
            stdin, stdout, stderr = ssh.exec_command(f"mv {remote_temp} {remote_js}")
            stdout.channel.recv_exit_status()
            print_success("Renamed to original filename")
            
            print_success(f"\n✓ SUCCESS! The language button now shows '{target_lang}' instead of 'English'!")
            print_info("Refresh your browser to see the change.")
            
        except Exception as e:
            print_error(f"Upload failed: {e}")
            
        sftp.close()
        ssh.close()
        
    except Exception as e:
        print_error(f"Connection failed: {e}")

def reboot_printer():
    """Restartuje drukarkę przez SSH"""
    if not PARAMIKO_AVAILABLE:
        print_error("\nError: 'paramiko' module not installed.")
        return
    
    print_header("\n--- Reboot Printer ---")
    ip = get_printer_ip()
    if not ip: return
    
    confirm = input("⚠️  This will RESTART the printer. Continue? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print_warning("Reboot cancelled.")
        return

    username = "root"
    password = "OpenCentauri"
    
    print_info(f"\nConnecting to {ip}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        
        print_info("Sending reboot command...")
        # Simplest command as per user feedback
        ssh.exec_command("reboot")
        
        print_success("\n✓ Reboot command sent!")
        print_info("The printer will restart in a few seconds.")
        print_info("Wait about 1-2 minutes before reconnecting.")
        
        ssh.close()
        
    except Exception as e:
        print_error(f"Connection failed: {e}")

def list_printer_files():
    """Wyświetla listę plików w /app/resources (diagnostyka)"""
    if not PARAMIKO_AVAILABLE:
        print_error("\nError: 'paramiko' module not installed.")
        return
    
    print_header("\n--- List Printer Files (Diagnostic) ---")
    ip = get_printer_ip()
    if not ip: return

    username = "root"
    password = "OpenCentauri"
    
    print_info(f"\nConnecting to {ip}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        
        print_header("\n=== Files in /app/resources ===")
        stdin, stdout, stderr = ssh.exec_command("ls -lah /app/resources")
        output = stdout.read().decode('utf-8')
        print(output)
        
        # Also check for any config files
        print_header("\n=== Looking for config files ===")
        stdin, stdout, stderr = ssh.exec_command("find /app -name '*.json' -o -name '*.conf' -o -name 'config*' | head -20")
        output = stdout.read().decode('utf-8')
        print(output if output.strip() else "No config files found in first 20 results.")
        
        ssh.close()
        
    except Exception as e:
        print_error(f"Connection failed: {e}")

def upload_ui_files():
    if not PARAMIKO_AVAILABLE:
        print_error("\nError: 'paramiko' module not installed.")
        return

    work_dir = os.path.dirname(os.path.abspath(__file__))
    local_bin = os.path.join(work_dir, "translation_updated.bin")
    local_csv = os.path.join(work_dir, "translation_updated.csv")
    
    if not os.path.exists(local_bin):
        print_error("Error: translation_updated.bin not found. Build it first (Option 3).")
        return
    
    print_header("\n--- Upload UI Translation Files to Printer ---")
    print_info("This will:")
    print_info("1. Connect to the printer via SSH")
    print_info("2. Backup existing translation.bin and translation.csv")
    print_info("3. Upload and rename your modified files")
    
    ip = get_printer_ip()
    if not ip: return
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print_warning("Upload cancelled.")
        return

    username = "root"
    password = "OpenCentauri"
    remote_dir = "/app/resources"
    
    print_info(f"\nConnecting to {ip}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        sftp = ssh.open_sftp()
        
        # Backup existing files
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print_info("Creating backups...")
        for filename in ["translation.bin", "translation.csv"]:
            remote_original = f"{remote_dir}/{filename}"
            remote_backup = f"{remote_dir}/{filename}.backup_{timestamp}"
            try:
                # Use SSH command to copy
                stdin, stdout, stderr = ssh.exec_command(f"cp {remote_original} {remote_backup}")
                stdout.channel.recv_exit_status()  # Wait for command
                print_success(f"Backed up: {filename} -> {filename}.backup_{timestamp}")
            except Exception as e:
                print_warning(f"Warning: Could not backup {filename}: {e}")
        
        # Upload new files with temp names first
        print_info("\nUploading new files...")
        try:
            # Upload BIN
            remote_temp_bin = f"{remote_dir}/translation_updated.bin.tmp"
            sftp.put(local_bin, remote_temp_bin)
            print_success(f"Uploaded: translation_updated.bin")
            
            # Upload CSV if exists
            if os.path.exists(local_csv):
                remote_temp_csv = f"{remote_dir}/translation_updated.csv.tmp"
                sftp.put(local_csv, remote_temp_csv)
                print_success(f"Uploaded: translation_updated.csv")
            
            # Rename files on server
            print_info("\nRenaming files on printer...")
            stdin, stdout, stderr = ssh.exec_command(f"mv {remote_temp_bin} {remote_dir}/translation.bin")
            stdout.channel.recv_exit_status()
            print_success("Renamed: translation_updated.bin -> translation.bin")
            
            if os.path.exists(local_csv):
                stdin, stdout, stderr = ssh.exec_command(f"mv {remote_temp_csv} {remote_dir}/translation.csv")
                stdout.channel.recv_exit_status()
                print_success("Renamed: translation_updated.csv -> translation.csv")
            
            print_success("\nSUCCESS! Files uploaded and replaced.")
            print_info("You may need to restart the printer for changes to take effect.")
            
        except Exception as e:
            print_error(f"Upload failed: {e}")
            
        sftp.close()
        ssh.close()
        
    except Exception as e:
        print_error(f"Connection failed: {e}")

def upload_web_files():
    if not PARAMIKO_AVAILABLE:
        print_error("\nError: 'paramiko' module not installed.")
        return

    work_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(work_dir, "web_i18n")
    
    # Find the translated file
    if not os.path.exists(web_dir):
        print_error("Error: web_i18n directory not found.")
        return
        
    # List available translated files
    import glob
    json_files = glob.glob(os.path.join(web_dir, "network-en_patched_with_*.json"))
    
    if not json_files:
        print_error("Error: No translated JSON files found. Translate first (Option 6).")
        return
    
    print_header("\n--- Upload Web Interface Translation Files to Printer ---")
    
    if len(json_files) == 1:
        local_file = json_files[0]
        print_info(f"Found: {os.path.basename(local_file)}")
    else:
        print_info("Multiple translated files found:")
        for i, f in enumerate(json_files, 1):
            print(f"{i}. {os.path.basename(f)}")
        choice = input("\nSelect file number: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(json_files):
                local_file = json_files[idx]
            else:
                print_error("Invalid selection.")
                return
        except ValueError:
            print_error("Invalid input.")
            return
    
    print_info("\nThis will:")
    print_info("1. Connect to the printer via SSH")
    print_info("2. Backup existing network-en.json")
    print_info("3. Upload your translated file as network-en.json")
    
    ip = get_printer_ip()
    if not ip: return
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print_warning("Upload cancelled.")
        return

    username = "root"
    password = "OpenCentauri"
    remote_path = "/app/resources/www/assets/i18n/network-en.json"
    
    print_info(f"\nConnecting to {ip}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        sftp = ssh.open_sftp()
        
        # Backup
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_backup = f"/app/resources/www/assets/i18n/network-en.json.backup_{timestamp}"
        
        print_info("Creating backup...")
        try:
            stdin, stdout, stderr = ssh.exec_command(f"cp {remote_path} {remote_backup}")
            stdout.channel.recv_exit_status()
            print_success(f"Backed up: network-en.json -> network-en.json.backup_{timestamp}")
        except Exception as e:
            print_warning(f"Warning: Could not backup: {e}")
        
        # Upload
        print_info("\nUploading translated file...")
        try:
            remote_temp = f"/app/resources/www/assets/i18n/network-en.json.tmp"
            sftp.put(local_file, remote_temp)
            print_success("Uploaded file to temporary location")
            
            # Rename
            stdin, stdout, stderr = ssh.exec_command(f"mv {remote_temp} {remote_path}")
            stdout.channel.recv_exit_status()
            print_success("Renamed to: network-en.json")
            
            print_success("\nSUCCESS! Web interface translation uploaded.")
            print_info("Refresh your browser to see changes.")
            
        except Exception as e:
            print_error(f"Upload failed: {e}")
            
        sftp.close()
        ssh.close()
        
    except Exception as e:
        print_error(f"Connection failed: {e}")

if __name__ == "__main__":
    main()
