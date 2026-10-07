#!/usr/bin/env python3
"""
Standalone USA Contact Parser
- Extracts emails + USA NANP phones from file or folder inputs
- Outputs to parsed_output/emails/ + parsed_output/phones/ + invalids.log + stats.json
- Stdlib only, zero dependencies, cross-platform (Windows & Linux)
Usage:
  python parser.py --input ./dump.txt --output ./parsed_output
  python parser.py --input ./raw_dumps --output ./parsed_output --recursive --extensions txt,csv,log,json,eml
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

EMAIL_STRICT_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Loose token to catch invalid attempts like user@@bad..com, test@.com
EMAIL_LOOSE_RE = re.compile(r"[^\s,;<>\"']+@[^\s,;<>\"']+")

PHONE_STRICT_RE = re.compile(r"""
    (?<!\d)
    (?:\+?1[\s.\-]?)?          # optional country
    (?:\(?\d{3}\)?[\s.\-]?)?   # optional area (allows 7-digit to be caught as invalid)
    \d{3}[\s.\-]?              # prefix
    \d{4}                      # line
    (?!\d)
    """, re.VERBOSE | re.ASCII)

# Loose contiguous digits to catch invalids like 12345
PHONE_LOOSE_DIGITS_RE = re.compile(r"(?<!\d)\d{5,15}(?!\d)", re.ASCII)
EXT_RE = re.compile(r"\b(?:ext\.?|x)\s*\d{1,5}\b", re.IGNORECASE)

_LEADING_STRIP = ' \t\r\n<([{\'"'
_TRAILING_STRIP = ' \t\r\n>)]}\'\".,;:!?'

DEFAULT_EXTENSIONS = ["txt", "csv", "log", "json", "eml"]


def normalize_email(raw: str, strip_plus: bool = False):
    """Return (normalized_email|None, reason|None)."""
    if raw is None:
        return None, "empty"
    s = str(raw).strip()
    # strip surrounding wrappers, then trailing sentence punctuation
    s = s.lstrip(_LEADING_STRIP).rstrip(_TRAILING_STRIP)
    # remove trailing dot(s) that came from sentence end but preserve internal
    # (already handled by rstrip above, keep for clarity)
    if not s:
        return None, "empty"
    if len(s) > 254:
        return None, "too-long"
    if s.count("@") != 1:
        return None, "bad-email-multiple-at" if "@" in s else "bad-email-no-at"
    local, domain = s.split("@", 1)
    if strip_plus and "+" in local:
        local = local.split("+", 1)[0]
        s = f"{local}@{domain}"
    if not local or not domain:
        return None, "bad-email-empty-part"
    if len(local) > 64:
        return None, "bad-email-local-too-long"
    if ".." in local or ".." in domain:
        return None, "bad-email-consecutive-dots"
    if local.startswith(".") or local.endswith("."):
        return None, "bad-email-dot-edge"
    # allowed chars check for local (strict set)
    if not re.fullmatch(r"[A-Za-z0-9._%+-]+", local):
        return None, "bad-email-local-chars"
    # domain labels
    labels = domain.split(".")
    if len(labels) < 2:
        return None, "bad-email-no-tld"
    for lab in labels:
        if not lab:
            return None, "bad-email-empty-label"
        if len(lab) > 63:
            return None, "bad-email-label-too-long"
        if lab.startswith("-") or lab.endswith("-"):
            return None, "bad-email-hyphen-edge"
        if lab.startswith(".") or lab.endswith("."):
            return None, "bad-email-dot-edge"
        if not re.fullmatch(r"[A-Za-z0-9-]+", lab):
            return None, "bad-email-domain-chars"
    tld = labels[-1]
    if len(tld) < 2:
        return None, "bad-email-tld-too-short"
    if tld.isdigit():
        return None, "bad-email-tld-numeric"
    # require at least one alpha in TLD
    if not re.search(r"[A-Za-z]", tld):
        return None, "bad-email-tld-no-alpha"
    normalized = f"{local}@{domain}".lower()
    return normalized, None


def normalize_phone(raw: str, allow_555: bool = False):
    """Return (dict|None, reason|None). Dict has e164, national, digits10."""
    if raw is None:
        return None, "empty"
    digits = re.sub(r"\D", "", str(raw))
    if len(digits) == 11 and digits.startswith("1"):
        digits10 = digits[1:]
    elif len(digits) == 10:
        digits10 = digits
    else:
        return None, f"bad-length-got-{len(digits)}"
    # all same digit
    if len(set(digits10)) == 1:
        return None, "bad-nanp-same-digit"
    npa = digits10[0:3]
    nxx = digits10[3:6]
    line = digits10[6:10]
    if npa[0] in "01":
        return None, "bad-nanp-area-0-1"
    if nxx[0] in "01":
        return None, "bad-nanp-office-0-1"
    if npa[1:] == "11":
        return None, "bad-nanp-area-n11"
    if nxx[1:] == "11":
        return None, "bad-nanp-office-n11"
    if npa == "555" and not allow_555:
        return None, "fictional-range-area-555"
    # fictional 555-0100..555-0199 (central office 555 + line 01xx)
    if nxx == "555" and line.startswith("01") and not allow_555:
        return None, "fictional-range-555-01xx"
    e164 = f"+1{digits10}"
    national = f"({npa}) {nxx}-{line}"
    return {"e164": e164, "national": national, "digits10": digits10}, None


def format_phone(phone_or_str: str | dict) -> str | None:
    """Backward-compatible formatter returning national form if possible."""
    if isinstance(phone_or_str, dict):
        return phone_or_str.get("national")
    if not phone_or_str:
        return phone_or_str
    norm, _ = normalize_phone(str(phone_or_str), allow_555=True)
    if norm:
        return norm["national"]
    # fallback to old behavior: strip leading 1, format if 10 digits
    digits = re.sub(r"\D", "", str(phone_or_str))
    if digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone_or_str


def _email_spans(line: str):
    spans = []
    for m in EMAIL_LOOSE_RE.finditer(line):
        spans.append((m.start(), m.end()))
    return spans


def _overlaps_email(span, email_spans):
    s, e = span
    for es, ee in email_spans:
        if not (e <= es or s >= ee):
            return True
    return False


def extract_emails_from_line(line: str, strip_plus: bool = False):
    """Yield (raw, normalized|None, reason|None, span)."""
    seen_spans = set()
    # First strict matches (high confidence)
    for m in EMAIL_STRICT_RE.finditer(line):
        raw = m.group(0)
        norm, reason = normalize_email(raw, strip_plus=strip_plus)
        seen_spans.add((m.start(), m.end()))
        yield raw, norm, reason, (m.start(), m.end())
    # Then loose to catch invalids not already covered
    for m in EMAIL_LOOSE_RE.finditer(line):
        span = (m.start(), m.end())
        # skip if overlaps strict
        overlapped = False
        for ss, se in seen_spans:
            if not (span[1] <= ss or span[0] >= se):
                overlapped = True
                break
        if overlapped:
            continue
        raw = m.group(0)
        # skip obvious non-emails that are too long or no dot in domain part
        # still validate to log reason
        norm, reason = normalize_email(raw, strip_plus=strip_plus)
        # Only yield if it looks like an email attempt (contains @ and len reasonable)
        # to avoid noise; always yield invalids for visibility
        if norm is None:
            # filter pure noise: must contain @ and at least 3 chars
            if "@" in raw and 3 <= len(raw) <= 320:
                yield raw, None, reason, span
        else:
            yield raw, norm, None, span


def extract_phones_from_line(line: str, allow_555: bool = False, min_digits: int = 5):
    """Yield (raw, norm_dict|None, reason|None, span)."""
    # Remove extensions for matching but keep original spans approximate
    # We match on cleaned line to avoid ext digits polluting, but report raw from cleaned
    cleaned = EXT_RE.sub(" ", line)
    email_spans = _email_spans(cleaned)
    covered = []

    for m in PHONE_STRICT_RE.finditer(cleaned):
        raw = m.group(0).strip()
        if not raw:
            continue
        span = (m.start(), m.end())
        # skip phones inside email tokens (e.g. user12345@example.com)
        if _overlaps_email(span, email_spans):
            continue
        # skip if directly attached to letters (likely ID, not phone)
        if span[0] > 0 and cleaned[span[0]-1].isalpha():
            continue
        if span[1] < len(cleaned) and cleaned[span[1]].isalpha():
            continue
        # Check digit count vs min_digits
        digit_count = len(re.sub(r"\D", "", raw))
        if digit_count < min_digits:
            continue
        # skip if this span overlaps a previous strict match (regex shouldn't overlap, but guard)
        norm, reason = normalize_phone(raw, allow_555=allow_555)
        covered.append(span)
        yield raw, norm, reason, span

    # Loose contiguous digits for invalids like 12345
    for m in PHONE_LOOSE_DIGITS_RE.finditer(cleaned):
        span = (m.start(), m.end())
        # skip if inside email
        if _overlaps_email(span, email_spans):
            continue
        # skip digits embedded in alphanumeric tokens (usernames, IDs)
        if span[0] > 0 and cleaned[span[0]-1].isalpha():
            continue
        if span[1] < len(cleaned) and cleaned[span[1]].isalpha():
            continue
        # skip if overlaps strict
        overlapped = False
        for cs, ce in covered:
            if not (span[1] <= cs or span[0] >= ce):
                overlapped = True
                break
        if overlapped:
            continue
        raw = m.group(0)
        digit_count = len(raw)
        if digit_count < min_digits:
            continue
        # skip if part of longer alphanumeric that looks like ID? Keep it - will be logged as bad-length unless 10 digits
        # Avoid matching numbers that are clearly years with context? Keep simple: log them
        # If 10 digits, try normalize (could be valid contiguous without separators missed by strict? strict should have caught, but double-check)
        norm, reason = normalize_phone(raw, allow_555=allow_555)
        # Only yield invalids for loose to avoid duplicates; if valid and not already covered, yield as valid
        # To reduce noise, only yield loose if len is 5-11 or it has phone-like context (spaces/dashes nearby)? For now yield all >=min_digits
        # But skip 5-6 digit numbers that are likely zip+4 fragments unless they have separators (contiguous here has no separators) -> still log as invalid per spec example 12345
        yield raw, norm, reason, span


def scan_inputs(input_path: Path, recursive: bool, extensions: list[str], output_root: Path | None = None):
    """Return sorted list of file Paths to scan, excluding output_root if inside input."""
    exts = set(e.lower().lstrip(".") for e in extensions if e.strip())
    if not input_path.exists():
        return None
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        pattern = "**/*" if recursive else "*"
        files = []
        resolved_out = output_root.resolve() if output_root else None
        for p in input_path.glob(pattern):
            if p.is_file():
                if resolved_out:
                    try:
                        if p.resolve().is_relative_to(resolved_out):
                            continue
                    except (ValueError, AttributeError):
                        if str(p.resolve()).startswith(str(resolved_out)):
                            continue
                # if no extensions filter, include all? Default to exts; if ext empty, include all
                if not exts:
                    files.append(p)
                elif p.suffix.lower().lstrip(".") in exts:
                    files.append(p)
                # also include files with no suffix but likely text? Skip unless exts empty
        return sorted(files)
    return None


def parse_file(path: Path, strip_plus: bool, allow_555: bool, min_digits: int,
               email_order_start: int, phone_order_start: int):
    """
    Parse single file, return:
      emails_found: list of (normalized, raw, line_no)
      phones_found: list of (norm_dict, raw, line_no)
      invalids: list of dict
      file_stats: dict
    """
    emails_found = []
    phones_found = []
    invalids = []
    lines = 0
    email_candidates = 0
    phone_candidates = 0

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line_no, line in enumerate(f, start=1):
            lines += 1
            if not line.strip():
                continue
            # GUARD: prevent quadratic regex stall on pathological single-line blobs (e.g. minified dumps)
            if len(line) > 65536:
                invalids.append({
                    "type": "line-too-long",
                    "reason": f"line-length-{len(line)}-exceeds-65536-skipped",
                    "source_file": str(path),
                    "line_no": line_no,
                    "raw": line[:200],
                })
                continue
            # FAST-PATH: skip email regexes when no '@' (both require '@'); identical behavior
            if "@" in line:
                # emails
                for raw, norm, reason, _span in extract_emails_from_line(line, strip_plus=strip_plus):
                    email_candidates += 1
                    if norm:
                        emails_found.append((norm, raw, line_no))
                    else:
                        invalids.append({
                            "type": "email",
                            "reason": reason or "bad-email",
                            "source_file": str(path),
                            "line_no": line_no,
                            "raw": raw[:200],
                        })
            # FAST-PATH: skip phone regexes when no ASCII digit (both require digits); identical behavior
            has_digit = False
            for _d in "0123456789":
                if _d in line:
                    has_digit = True
                    break
            if has_digit:
                # phones
                for raw, norm, reason, _span in extract_phones_from_line(line, allow_555=allow_555, min_digits=min_digits):
                    phone_candidates += 1
                    if norm:
                        phones_found.append((norm, raw, line_no))
                    else:
                        invalids.append({
                            "type": "phone",
                            "reason": reason or "bad-phone",
                            "source_file": str(path),
                            "line_no": line_no,
                            "raw": raw[:200],
                        })

    file_stats = {
        "path": str(path),
        "lines": lines,
        "email_candidates": email_candidates,
        "phone_candidates": phone_candidates,
        "valid_email_occurrences": len(emails_found),
        "valid_phone_occurrences": len(phones_found),
        "invalids": len(invalids),
    }
    return emails_found, phones_found, invalids, file_stats


def atomic_write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    os.replace(tmp, path)


def atomic_write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Standalone USA email + phone parser")
    p.add_argument("--input", required=True, help="Input file or directory")
    p.add_argument("--output", default="./parsed_output", help="Output root directory")
    p.add_argument("--recursive", action="store_true", help="Recurse into subdirectories when input is a directory")
    p.add_argument("--extensions", default="txt,csv,log,json,eml", help="Comma-separated extensions to scan when input is dir")
    p.add_argument("--allow-555", action="store_true", help="Allow fictional 555 numbers")
    p.add_argument("--strip-plus", action="store_true", help="Strip +tag from emails (user+tag@x -> user@x)")
    p.add_argument("--min-digits", type=int, default=5, help="Minimum digits to consider a phone candidate (default 5)")
    p.add_argument("--quiet", action="store_true", help="Suppress console summary")
    p.add_argument("--limit-preview", type=int, default=20, help="How many samples to preview in console")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    start = time.time()
    input_path = Path(args.input)
    output_root = Path(args.output)
    extensions = [e.strip() for e in args.extensions.split(",") if e.strip()]

    files = scan_inputs(input_path, args.recursive, extensions, output_root=output_root)
    if files is None:
        print(f"Input path not found: {input_path}", file=sys.stderr)
        return 2
    if len(files) == 0:
        print(f"No files matched in: {input_path} (recursive={args.recursive}, extensions={extensions})", file=sys.stderr)
        # still create empty outputs with stats
        files = []

    # Global dedupe maps
    emails_map = {}  # normalized -> {email, source_file, line_no, first_seen}
    phones_map = {}  # e164 -> {e164, national, digits10, source_file, line_no, first_seen}
    all_invalids = []
    per_file_stats = []

    email_order = 0
    phone_order = 0
    total_email_candidates = 0
    total_phone_candidates = 0
    total_valid_email_occ = 0
    total_valid_phone_occ = 0

    for fp in files:
        try:
            emails_found, phones_found, invalids, fstats = parse_file(
                fp, strip_plus=args.strip_plus, allow_555=args.allow_555,
                min_digits=args.min_digits,
                email_order_start=email_order, phone_order_start=phone_order
            )
        except Exception as e:
            # Log file-level error as invalid entry, continue
            all_invalids.append({
                "type": "file-error",
                "reason": f"read-error: {e}",
                "source_file": str(fp),
                "line_no": 0,
                "raw": "",
            })
            per_file_stats.append({
                "path": str(fp),
                "lines": 0,
                "email_candidates": 0,
                "phone_candidates": 0,
                "valid_email_occurrences": 0,
                "valid_phone_occurrences": 0,
                "invalids": 1,
                "error": str(e),
            })
            continue

        per_file_stats.append(fstats)
        total_email_candidates += fstats["email_candidates"]
        total_phone_candidates += fstats["phone_candidates"]
        total_valid_email_occ += fstats["valid_email_occurrences"]
        total_valid_phone_occ += fstats["valid_phone_occurrences"]
        all_invalids.extend(invalids)

        for norm, raw, line_no in emails_found:
            if norm not in emails_map:
                emails_map[norm] = {
                    "email": norm,
                    "source_file": str(fp),
                    "line_no": line_no,
                    "first_seen": email_order,
                }
                email_order += 1
        for norm_dict, raw, line_no in phones_found:
            e164 = norm_dict["e164"]
            if e164 not in phones_map:
                phones_map[e164] = {
                    "e164": e164,
                    "national": norm_dict["national"],
                    "digits10": norm_dict["digits10"],
                    "source_file": str(fp),
                    "line_no": line_no,
                    "first_seen": phone_order,
                }
                phone_order += 1

    # Sorted outputs for determinism
    sorted_emails = sorted(emails_map.values(), key=lambda x: x["email"])
    sorted_phones = sorted(phones_map.values(), key=lambda x: x["e164"])

    # Prepare output dirs
    emails_dir = output_root / "emails"
    phones_dir = output_root / "phones"
    emails_dir.mkdir(parents=True, exist_ok=True)
    phones_dir.mkdir(parents=True, exist_ok=True)

    # emails.txt
    emails_txt = "".join(e["email"] + "\n" for e in sorted_emails)
    atomic_write_text(emails_dir / "emails.txt", emails_txt)
    # emails.json
    atomic_write_json(emails_dir / "emails.json", sorted_emails)

    # phones_e164.txt + phones_national.txt (1:1 same order)
    e164_txt = "".join(p["e164"] + "\n" for p in sorted_phones)
    national_txt = "".join(p["national"] + "\n" for p in sorted_phones)
    atomic_write_text(phones_dir / "phones_e164.txt", e164_txt)
    atomic_write_text(phones_dir / "phones_national.txt", national_txt)
    atomic_write_json(phones_dir / "phones.json", sorted_phones)

    # invalids.log
    log_lines = []
    for inv in all_invalids:
        # greppable: [type:reason] source:line: raw
        raw_snip = inv.get("raw", "").replace("\n", " ").replace("\r", " ")[:200]
        log_lines.append(f"[{inv.get('type')}:{inv.get('reason')}] {inv.get('source_file')}:{inv.get('line_no')}: raw='{raw_snip}'")
    atomic_write_text(output_root / "invalids.log", "".join(l + "\n" for l in log_lines))

    elapsed = time.time() - start
    stats = {
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "input": str(input_path),
        "output": str(output_root),
        "args": {
            "recursive": args.recursive,
            "extensions": extensions,
            "allow_555": args.allow_555,
            "strip_plus": args.strip_plus,
            "min_digits": args.min_digits,
        },
        "files_scanned": len(files),
        "files": per_file_stats,
        "totals": {
            "lines": sum(f.get("lines", 0) for f in per_file_stats),
            "email_candidates": total_email_candidates,
            "phone_candidates": total_phone_candidates,
            "unique_emails": len(sorted_emails),
            "unique_phones": len(sorted_phones),
            "invalids": len(all_invalids),
            "duplicate_emails_removed": total_valid_email_occ - len(sorted_emails),
            "duplicate_phones_removed": total_valid_phone_occ - len(sorted_phones),
        },
        "elapsed_seconds": round(elapsed, 3),
    }
    atomic_write_json(output_root / "stats.json", stats)

    if not args.quiet:
        print(f"Files scanned: {len(files)}")
        print(f"Unique emails: {len(sorted_emails)} (candidates {total_email_candidates}, dupes removed {stats['totals']['duplicate_emails_removed']})")
        print(f"Unique phones: {len(sorted_phones)} (candidates {total_phone_candidates}, dupes removed {stats['totals']['duplicate_phones_removed']})")
        print(f"Invalids: {len(all_invalids)}")
        print(f"Output: {output_root.resolve()}")
        print(f"  - {emails_dir / 'emails.txt'}")
        print(f"  - {emails_dir / 'emails.json'}")
        print(f"  - {phones_dir / 'phones_e164.txt'}")
        print(f"  - {phones_dir / 'phones_national.txt'}")
        print(f"  - {phones_dir / 'phones.json'}")
        print(f"  - {output_root / 'invalids.log'}")
        print(f"  - {output_root / 'stats.json'}")
        print(f"Elapsed: {elapsed:.2f}s")
        lim = max(0, args.limit_preview or 0)
        if lim and sorted_emails:
            print(f"\nEmails preview (first {min(lim, len(sorted_emails))}):")
            for e in sorted_emails[:lim]:
                print(f"  {e['email']}  ({e['source_file']}:{e['line_no']})")
        if lim and sorted_phones:
            print(f"\nPhones preview (first {min(lim, len(sorted_phones))}):")
            for p in sorted_phones[:lim]:
                print(f"  {p['e164']}  {p['national']}  ({p['source_file']}:{p['line_no']})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
