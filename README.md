# Standalone USA Contact Parser

A high-performance, zero-dependency, cross-platform CLI tool for extracting, normalizing, and deduplicating USA phone numbers (NANP) and email addresses from messy text dumps, logs, CSVs, and JSON files.

Runs seamlessly on **Windows**, **Linux**, and **macOS** using Python standard library only (Python 3.9+).

---

## Features

- **Zero External Dependencies**: Pure Python standard library (`argparse`, `json`, `re`, `pathlib`).
- **Cross-Platform**: Tested on Windows and Linux with uniform UTF-8 output and standard newline handling.
- **NANP Phone Extraction & Validation**:
  - Validates North American Numbering Plan area codes (NPA: 2–9) and exchange codes (NXX: 2–9).
  - Rejects invalid formats including N11 service codes (`211`, `311`, `411`, `911`, etc.) and repeating digit patterns.
  - Strips leading country code (`+1` or `1`) and phone extension markers (`ext`, `x`).
  - Outputs matching dual formats: **E.164** (`+1XXXXXXXXXX`) and **National** (`(XXX) XXX-XXXX`).
  - Flags fictional `555-0100`–`555-0199` numbers (with `--allow-555` override).
- **Email Extraction & RFC Normalization**:
  - Trims surrounding punctuation, lowercases addresses, validates local/domain lengths and TLD rules.
  - Rejects malformed tokens (`user@@domain`, double dots, invalid TLDs).
  - Optional `--strip-plus` flag to normalize sub-addressed emails (`user+tag@example.com` → `user@example.com`).
- **Global Deduplication & Provenance**:
  - Tracks first occurrence (`source_file`, `line_no`, `first_seen`).
  - Generates sorted `.txt` plain lists and structured `.json` collections.
- **Safety & Performance**:
  - Fast-path checks before executing regex operations.
  - Built-in guard against pathological giant lines (>65k chars) to prevent quadratic regex slowdowns on minified dumps.
  - Automatic exclusion of output folders to prevent self-ingestion on recursive scans.
  - Atomic file writes using temporary files.

---

## Output Structure

When executing against an input file or folder, the parser generates:

```
parsed_output/
├── emails/
│   ├── emails.txt              # Sorted, lowercased, globally deduped emails (1 per line)
│   └── emails.json             # JSON array with provenance (email, source_file, line_no, first_seen)
├── phones/
│   ├── phones_e164.txt         # Sorted E.164 numbers: +1XXXXXXXXXX (1 per line)
│   ├── phones_national.txt     # Formatted national numbers: (XXX) XXX-XXXX (1:1 line mapped to E.164)
│   └── phones.json             # JSON array with e164, national, digits10, source_file, line_no
├── invalids.log                # Line-by-line log of rejected candidates with reasons
└── stats.json                  # Run summary, elapsed time, files scanned, duplicate and invalid counts
```

---

## Quick Start

### 1. Direct Script Execution (No Installation Required)

#### Windows (PowerShell / Command Prompt)

```powershell
# Parse a single file
python parser.py --input dump.txt --output ./parsed_output

# Parse an entire directory recursively
python parser.py --input ./data_dumps --output ./parsed_output --recursive

# Custom extensions, stripping email plus tags, allowing 555 numbers
python parser.py --input ./data_dumps --output ./parsed_output --recursive --extensions txt,csv,log,json --strip-plus --allow-555
```

#### Linux / macOS (Bash / Zsh)

```bash
# Make executable
chmod +x parser.py

# Run directly
./parser.py --input dump.txt --output ./parsed_output

# Recursive scan with preview limit
./parser.py --input /path/to/dumps --output ./parsed_output --recursive --limit-preview 20
```

---

### 2. Install as a System / Virtualenv CLI Tool (Optional)

Install locally into your Python environment:

```bash
pip install .
```

Then run anywhere using the command:

```bash
contact-parser --input /path/to/data --output ./parsed_output --recursive
```

---

## CLI Options

| Option | Default | Description |
|---|---|---|
| `--input PATH` | *(Required)* | Path to input file or directory to scan. |
| `--output PATH` | `./parsed_output` | Destination directory for parsed output files. |
| `--recursive` | `False` | Recursively scan subdirectories when `--input` is a folder. |
| `--extensions EXTS` | `txt,csv,log,json,eml` | Comma-separated file extensions to include in directory scans. |
| `--allow-555` | `False` | Allow fictional 555 numbers (e.g. `555-0100`–`555-0199`). |
| `--strip-plus` | `False` | Strip `+tag` from email local-parts (`user+tag@domain` → `user@domain`). |
| `--min-digits N` | `5` | Minimum digits to consider candidate for phone parsing. |
| `--quiet` | `False` | Suppress console summary output. |
| `--limit-preview N` | `20` | Number of sample hits to preview in the terminal (0 to disable). |

---

## License

MIT License.
