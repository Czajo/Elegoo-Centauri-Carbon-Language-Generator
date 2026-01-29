# ELEGOO Translation Tool by Czajo

**🌐 Language / Język:** [🇵🇱 Polski (Polish)](README.md) | [🇬🇧 English](README_EN.md)

---

Tool for translating the interface of ELEGOO Centauri Carbon 3D printers. Enables downloading, editing, translating, and uploading translation files for both the touchscreen interface (UI) and the web interface of the printer.

## 📋 Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Detailed Option Descriptions](#detailed-option-descriptions)
- [File Structure](#file-structure)
- [Troubleshooting](#troubleshooting)
- [Technical Information](#technical-information)
- [Security](#security)
- [Author](#author)

## 🚀 Features

- ✅ Download translation files from printer via SSH
- ✅ Automatic translation using Google Translate
- ✅ Manual translation editing
- ✅ Replace existing languages
- ✅ Add new languages
- ✅ Convert between CSV and BIN formats
- ✅ Translate web interface (JSON)
- ✅ Modify language selection button in web interface
- ✅ Upload files back to printer
- ✅ Reboot printer via SSH
- ✅ Diagnostic tools
- ✅ Colored messages for better readability
- ✅ Automatic printer IP address saving

## 📦 Requirements

### System Requirements

- Python 3.6 or newer
- Operating system: Windows, Linux, macOS
- Network connection to ELEGOO printer

### Required Python Libraries
- `paramiko` - for SSH connections to printer
- `deep-translator` - for automatic translation
- `colorama` - for colored messages (optional, but recommended)

### Printer Requirements
- ELEGOO printer with installed open firmware **OpenCentauri** ([documentation](https://docs.opencentauri.cc))
- Printer with SSH enabled
- Default SSH credentials:
  - **Username:** `root`
  - **Password:** `OpenCentauri`
- Printer IP address on local network

## 🔧 Installation

### 1. Clone or download the repository

```bash
git clone <repository-url>
cd generator
```

### 2. Install required libraries

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install paramiko scp deep-translator colorama
```

### 3. Run the script

```bash
python translation_tool.py
```

## ⚙️ Configuration

### Saving Printer IP Address

On first use, the tool will ask for the printer IP address. This address will be automatically saved in the `.printer_config.txt` file in the working directory and will be used as the default value on subsequent runs.

You can also manually edit the `.printer_config.txt` file and enter the printer IP address there.

### Checking Printer IP Address

1. Check network settings in the printer menu
2. Or use option **12. List Printer Files (Diagnostic)** in the tool to check the connection

## 📖 Usage

### Basic Workflow

1. **Download files from printer** (Option 1)
2. **Generate text files** (Option 2)
3. **Translate automatically** (Option 5) or **edit manually**
4. **Replace language** (Option 3) or **add new language** (Option 4)
5. **Upload files to printer** (Option 8)
6. **Reboot printer** (Option 11) - optional

### Example: Adding Polish Translation

```bash
# 1. Run the tool
python translation_tool.py

# 2. Select option 1 - Download files from printer
# 3. Select option 2 - Generate text files
# 4. Select option 5 - Automatic translation
#    - Enter language code: pl
#    - Confirm default filename: pl.txt
# 5. Check and correct pl.txt file (optional)
# 6. Select option 3 - Replace existing language
#    - Select language to replace (e.g., English)
#    - Enter language name: Polski
#    - Enter filename: pl.txt
# 7. Select option 8 - Upload files to printer
# 8. Select option 11 - Reboot printer
```

## 📚 Detailed Option Descriptions

### 1. Fetch files from Printer - UI Files (BIN/CSV)

**Function:** Downloads `translation.csv` and `translation.bin` files from printer via SSH.

**What it does:**
- Connects to printer via SSH
- Downloads files from `/app/resources/` directory
- Automatically calls option 2 (generate text files)

**Requirements:**
- `paramiko` library installed
- Printer available on network
- Correct SSH credentials

**Output files:**
- `translation.csv` - CSV file with translations
- `translation.bin` - binary file with translations
- `chinese.txt` - extracted Chinese texts
- `english.txt` - extracted English texts

---

### 2. Regenerate chinese.txt / english.txt from local CSV

**Function:** Extracts texts from local `translation.csv` file to text files.

**What it does:**
- Reads local `translation.csv` file
- Extracts Chinese texts to `chinese.txt`
- Extracts English texts to `english.txt`
- Automatically fills empty English texts (patches)

**Requirements:**
- `translation.csv` file in working directory

**Output files:**
- `chinese.txt` - one line = one text
- `english.txt` - one line = one text (with automatic fixes and addition of missing translations based on Chinese)

---

### 3. Replace Existing Language (Recommended) - Overwrites column

**Function:** Replaces existing language column with new translations. **Recommended method** for updating translations.

**What it does:**
- Displays list of available languages in CSV file
- Allows selecting language to replace
- Loads new translations from `.txt` file
- Replaces selected column with new translations
- Generates `translation_updated.csv` and `translation_updated.bin` files

**Steps:**
1. Select language to replace from list
2. Enter new language name (e.g., "Polski")
3. Enter translation filename (e.g., "pl.txt")
4. Tool automatically adjusts number of lines

**Requirements:**
- `translation.csv` file in working directory
- Translation file (e.g., `pl.txt`) in working directory

**Output files:**
- `translation_updated.csv` - updated CSV file
- `translation_updated.bin` - updated binary file

**Notes:**
- If translation file has fewer lines, empty lines will be added automatically
- If file has more lines, excess will be truncated
- Original CSV structure is preserved

---

### 4. Add New Language (Manual) - Appends column (limit 12)

**Function:** Adds new language column to CSV file. **⚠️ EXPERIMENTAL - Firmware does not display new languages in menu!**

**What it does:**
- Adds new language column before last technical column
- Loads translations from `.txt` file
- Generates updated CSV and BIN files

**Steps:**
1. Enter new language name (e.g., "Polski")
2. Enter translation filename (e.g., "pl.txt")

**Requirements:**
- `translation.csv` file in working directory
- Translation file in working directory
- Less than 12 languages in CSV file

**Output files:**
- `translation_updated.csv` - with new language column
- `translation_updated.bin` - updated binary file

**Notes:**
- ⚠️ **EXPERIMENTAL:** Despite adding language to BIN file, firmware does not display it in language selection menu
- New language is added before last column (technical column)
- If language limit is exceeded, use option 3 (replacement)
- **Recommended:** Use option 3 (replace existing language) instead of adding new

---

### 5. Generate Auto-Translation to target language (.txt)

**Function:** Automatically translates `english.txt` file to selected language using Google Translate.

**What it does:**
- Reads `english.txt` file
- Translates all lines to selected language
- Saves result to `.txt` file
- Shows translation progress in batches

**Steps:**
1. Enter target language code (e.g., `pl` for Polish, `es` for Spanish)
2. Enter output filename (default: `{code}.txt`)

**Requirements:**
- `deep-translator` library installed
- `english.txt` file in working directory
- Internet connection (for Google Translate)

**Output files:**
- `{code}.txt` - translated file (e.g., `pl.txt`)

**Supported language codes:**
- `pl` - Polish
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `ru` - Russian
- `ja` - Japanese
- `ko` - Korean
- `tr` - Turkish
- `uk` - Ukrainian
- And many others (according to Google Translate)

**Notes:**
- Translation may take several minutes (depending on number of lines)
- Empty lines are preserved
- Translation is done in batches of 50 lines
- After automatic translation **always check and correct** translations manually!

---

### 6. Fetch files from Printer - Web Interface (JSON)

**Function:** Downloads web interface translation file (`network-en.json`) from printer.

**What it does:**
- Connects to printer via SSH
- Downloads `/app/resources/www/assets/i18n/network-en.json` file
- Saves to `web_i18n/` directory

**Requirements:**
- `paramiko` library installed
- Printer available on network

**Output files:**
- `web_i18n/network-en.json` - JSON file with web interface translations

---

### 7. Translate Web Interface JSON

**Function:** Automatically translates web interface JSON file to selected language.

**What it does:**
- Reads `web_i18n/network-en.json` file
- Recursively translates all text values
- Saves translated JSON file

**Steps:**
1. Enter target language code (e.g., `pl`)

**Requirements:**
- `deep-translator` library installed
- `web_i18n/network-en.json` file (downloaded with option 6)
- Internet connection

**Output files:**
- `web_i18n/network-en_patched_with_{code}.json` - translated JSON file

**Notes:**
- Translation may take a long time (depending on number of keys)
- JSON structure is preserved (supports nested objects and arrays)
- After automatic translation **always check and correct** translations manually!

---

### 8. Upload to Printer - UI Files (translation.bin)

**Function:** Uploads updated UI translation files to printer.

**What it does:**
- Creates backups of original files on printer
- Uploads `translation_updated.bin` and `translation_updated.csv` files
- Replaces original files on printer

**Requirements:**
- `paramiko` library installed
- `translation_updated.bin` file in working directory
- Printer available on network

**Steps:**
1. Confirm file upload (type `yes`)

**Security:**
- Automatic backup creation before upload
- Backups have timestamp in filename
- Files are uploaded via temporary names (safe upload)

**Notes:**
- After upload, printer restart may be required (Option 11)
- Changes are visible after printer restart

---

### 9. Upload to Printer - Web Files (network-en.json)

**Function:** Uploads translated web interface JSON file to printer.

**What it does:**
- Creates backup of original JSON file
- Uploads translated JSON file
- Replaces original file on printer

**Requirements:**
- `paramiko` library installed
- Translated JSON file in `web_i18n/` directory
  - **Filename:** `network-en_patched_with_{code}.json` - **required for automatic and manual translation!**
  - Script searches for files matching pattern `network-en_patched_with_*.json`
- Printer available on network

**Steps:**
1. If multiple files exist, select file to upload
2. Confirm file upload (type `yes`)

**Notes about filename:**
- **Automatic translation (Option 7):** Script automatically creates file named `network-en_patched_with_{code}.json`
- **Manual translation:** File **must** have name matching pattern `network-en_patched_with_*.json` (e.g., `network-en_patched_with_pl.json`, `network-en_patched_with_manual.json`)
- Script only searches for files matching this pattern in `web_i18n/` directory

**Security:**
- Automatic backup creation
- Backup has timestamp in filename

**Notes:**
- Changes are visible after refreshing page in browser
- Printer restart is not required

---

### 10. Patch Web Language Button (English → Your Language) 😎

**Function:** Modifies language selection button in web interface, changing "English" text to selected language while keeping language code `en`.

**What it does:**
- Downloads JavaScript file from printer
- Finds and replaces "English" text in language button
- Uploads modified file back to printer

**Steps:**
1. Enter language name to display (e.g., "Polski", "Español")
2. Confirm modification (type `yes`)
3. Confirm file upload (type `yes`)

**Requirements:**
- `paramiko` library installed
- Printer available on network

**Output files:**
- `web_i18n/624.931d12e23af9a62e6007.js` - original file
- `web_i18n/624.931d12e23af9a62e6007_patched.js` - modified file

**Notes:**
- This is a "sneaky mod" - only changes displayed text, language code remains `en`
- Changes are visible after refreshing page in browser
- Automatic backup creation before modification
- If pattern is not found, tool will ask if you want to continue

---

### 11. Reboot Printer 🔄

**Function:** Restarts printer via SSH.

**What it does:**
- Connects to printer via SSH
- Sends `reboot` command
- Informs about waiting time

**Requirements:**
- `paramiko` library installed
- Printer available on network

**Steps:**
1. Confirm reboot (type `yes`)

**Notes:**
- ⚠️ **WARNING:** This will cause immediate printer restart
- After restart, wait 1-2 minutes before reconnecting
- If printer is printing, restart will interrupt printing!

---

### 12. List Printer Files (Diagnostic) 🔍

**Function:** Displays list of files in `/app/resources` directory on printer (diagnostic tool).

**What it does:**
- Connects to printer via SSH
- Displays list of files in `/app/resources`
- Searches for configuration files (`.json`, `.conf`, `config*`)

**Requirements:**
- `paramiko` library installed
- Printer available on network

**Usage:**
- Useful for problem diagnostics
- Helps check if files were uploaded correctly
- Allows viewing directory structure on printer

---

### 13. Exit

**Function:** Closes the tool.

---

## 📁 File Structure

### Source Files
```
generator/
├── translation_tool.py      # Main script
├── requirements.txt         # Dependencies list
├── README.md               # This documentation (Polish)
├── README_EN.md            # This documentation (English)
└── .printer_config.txt     # Saved printer IP address (created automatically)
```

### Generated Files During Work

#### UI Files (touchscreen interface)
```
generator/
├── translation.csv              # Original CSV file from printer
├── translation.bin             # Original binary file from printer
├── translation_updated.csv      # Updated CSV file
├── translation_updated.bin      # Updated binary file
├── chinese.txt                  # Extracted Chinese texts
├── english.txt                  # Extracted English texts
├── pl.txt                       # Example: Polish translations
└── {language_code}.txt            # Other translation files
```

#### Web Files (web interface)
```
generator/
└── web_i18n/
    ├── network-en.json                          # Original JSON file
    ├── network-en_patched_with_{code}.json      # Translated JSON file
    ├── 624.931d12e23af9a62e6007.js            # Original JavaScript file
    └── 624.931d12e23af9a62e6007_patched.js     # Modified JavaScript file
```

### Backup Files on Printer

Backups are automatically created on printer in the following locations:
- `/app/resources/translation.bin.backup_{timestamp}`
- `/app/resources/translation.csv.backup_{timestamp}`
- `/app/resources/www/assets/i18n/network-en.json.backup_{timestamp}`
- `/app/resources/www/624.931d12e23af9a62e6007.js.backup_{timestamp}`

## ⚠️ Known Bugs and Limitations

### Bug: New Languages Not Displayed in Printer Menu

**Problem:** Despite adding new language to BIN file (option 3 - replacement or option 4 - addition), printer firmware does not display it in language selection menu.

**Details:**
- Language is correctly added to `translation.bin` file
- File was correctly uploaded to printer
- Language selection menu in printer interface does not show new language
- This is a firmware limitation, not a tool limitation

**Workaround:** Use option 3 (replace existing language) instead of adding new. Replace a language you don't use (e.g., Spanish, French) with your translation.

---

### Bug: Language Name in Menu Remains Unchanged After Replacement

**Problem:** After replacing language (option 3), the language selection menu still displays the original name of the replaced language.

**Example:**
- You replace "Italian" language with Polish translation
- You enter new name: "Polski"
- After upload and restart, you still see "Italian" instead of "Polski" in language selection menu

**Details:**
- Translations work correctly (display after selecting language)
- Problem only affects language name in selection menu
- This is a firmware limitation, not a tool limitation

**Workaround:** Use option 10 (Patch Web Language Button) for web interface to change displayed language name. For touchscreen interface there is currently no solution.

---

### Limitation: Option 4 (Add New Language) is Experimental

**Problem:** Option 4 allows adding new language to BIN file, but firmware does not recognize it in language selection menu.

**Details:**
- Language is correctly added to BIN file structure
- OpenCentauri firmware has hardcoded language list in menu
- New languages are not included in this list

**Recommendation:** Always use option 3 (replace existing language) instead of option 4.

## 🔧 Troubleshooting

### Problem: "paramiko module not installed"

**Solution:**
```bash
pip install paramiko
```

### Problem: "deep-translator module not installed"

**Solution:**
```bash
pip install deep-translator
```

### Problem: "Connection failed"

**Possible causes:**
1. Incorrect printer IP address
2. Printer is not turned on or not available on network
3. Firewall blocking SSH connection
4. Incorrect SSH credentials

**Solution:**
1. Check printer IP address in network settings
2. Make sure printer is turned on and connected to same network
3. Check firewall settings
4. Check if default credentials are correct (root/OpenCentauri)

### Problem: "translation.csv not found"

**Solution:**
1. First use option 1 to download files from printer
2. Make sure `translation.csv` file is in working directory

### Problem: "Translation failed"

**Possible causes:**
1. No internet connection
2. Google Translate blocked requests (rate limiting)
3. Incorrect language code

**Solution:**
1. Check internet connection
2. Wait a few minutes and try again
3. Check if language code is correct (e.g., `pl`, `es`, `fr`)

### Problem: Translation file has wrong number of lines

**Solution:**
- Tool automatically adjusts number of lines:
  - If file has fewer lines, empty lines will be added
  - If file has more lines, excess will be truncated
- Make sure `english.txt` file has correct number of lines (use option 2)

### Problem: Colors don't work in terminal

**Solution:**
```bash
pip install colorama
```

Tool will work without colors, but with less readability.

### Problem: Changes not visible after upload

**Solution:**
1. Restart printer (Option 11)
2. For web interface: refresh page in browser (Ctrl+F5)
3. Check if files were uploaded correctly (Option 12)

## 🔬 Technical Information

### BIN File Generation

**How CSV → BIN conversion works:**

1. **Automatic calculation:** All values are automatically calculated based on CSV file content:
   - Number of languages: automatically detected from CSV header
   - Number of strings: automatically detected from number of data rows
   - Length of each text: automatically calculated after UTF-8 encoding
   - File offsets: dynamically calculated based on actual text lengths

2. **Text length:**
   - ✅ **No length limit** - texts can be arbitrarily long
   - ✅ **Everything is dynamic** - BIN file adjusts to translation lengths
   - ✅ **UTF-8 encoding** - supports all Unicode characters (Polish characters, emoji, etc.)
   - ✅ **Automatic calculation** - length of each text is measured after UTF-8 encoding

3. **Generation process:**
   - Each text from CSV is encoded as UTF-8
   - Null byte (`\x00`) is added to the end of each text
   - Text length (in bytes) is saved in language table
   - Offset (position) of text in file is automatically calculated
   - All texts are saved sequentially in "String Blob"
   - Total file size is automatically calculated

4. **Example:**
   ```
   Text: "Hello" (5 characters)
   → UTF-8: 48 65 6C 6C 6F (5 bytes)
   → With null byte: 48 65 6C 6C 6F 00 (6 bytes)
   → Length saved in table: 6 bytes
   ```

5. **What is automatically calculated:**
   - ✅ Length of each text (in UTF-8 bytes)
   - ✅ Position (offset) of each text in file
   - ✅ Language table positions
   - ✅ Total BIN file size
   - ✅ Number of languages and strings

**Note:** You don't need to worry about translation length - the tool automatically handles all calculations. You can use texts of any length, even if they are significantly longer than originals.

### BIN File Format

The `translation.bin` file has the following structure:

```
[Header - 15 bytes]
- Magic: 00 10 FD 12 (4 bytes)
- Total size - 14 (4 bytes, little-endian) - automatically calculated
- Reserved: 00 00 (2 bytes)
- Version: 01 (1 byte)
- Language count (1 byte) - detected from CSV
- String count (2 bytes, little-endian) - detected from CSV
- Reserved: 00 (1 byte)

[Offset List]
- 4 bytes per language (offset to language table) - automatically calculated

[Language Tables]
- 8 bytes per string (offset + length) - automatically calculated for each text

[String Blob]
- UTF-8 strings terminated with null byte
- Length of each text is dynamic (no limits)
```

### CSV File Format

The `translation.csv` file is a TSV (Tab-Separated Values) file:
- Column 0: String ID
- Column 1: Font size (Aux)
- Column 2+: Translations for each language
- Last column: Technical column (结束列)

### JSON File Format (Web)

The `network-en.json` file is a standard JSON file with web interface translations. May contain nested objects and arrays.

### SSH Protocol

The tool uses SSH protocol for communication with printer:
- Port: 22 (default)
- Username: `root`
- Password: `OpenCentauri`
- Protocol: SSH2

### Google Translate API

The tool uses `deep-translator` library, which uses Google Translate API:
- Limit: ~5000 characters per request
- Rate limiting: automatically handled by library
- Batch processing: translation in batches of 50 lines

## 🔒 Security

### ⚠️ Warnings

1. **SSH Credentials:** The tool uses default printer credentials. If you changed the password, you must modify the script.

2. **Backups:** The tool automatically creates backups before modifying files on printer. However, manual backup creation is always recommended before starting work.

3. **Printer Restart:** Option 11 immediately restarts the printer. Make sure you are not printing at that moment!

4. **File Modification:** Modifying printer system files may cause problems. Use the tool at your own risk.

### Security Recommendations

1. **Test on unused printer:** If possible, test changes on a printer that is not used for production.

2. **Keep backups:** Before uploading changes, always keep backups of original files.

3. **Check translations:** Always check automatic translations before uploading to printer.

4. **Local network:** Use the tool only on trusted local network.

## 👤 Author

**Czajo**

Tool created for translating the interface of ELEGOO Centauri Carbon 3D printers.

## 📝 License

The tool is provided for personal use. Use at your own risk.

---

## 🎨 Message Colors

The tool uses colored messages for better readability:

- 🔴 **Red** - Errors
- 🟢 **Green** - Success
- 🟡 **Yellow** - Warnings
- 🔵 **Cyan** - Information
- 🔵 **Blue (bold)** - Headers

---

## 📞 Support

In case of problems:
1. Check [Troubleshooting](#troubleshooting) section
2. Check if all required libraries are installed
3. Check connection to printer and internet
4. Check error logs in terminal

---

**Good luck with translation! 🚀**
