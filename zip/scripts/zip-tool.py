"""
Unified ZIP archive tool with built-in security protections.

Commands:
  list     <archive.zip>                           List contents with size & compression stats
  extract  <archive.zip> <output_dir> [pattern]    Extract with security checks (always on)
  search   <archive.zip> name <pattern>            Search files by name glob
  search   <archive.zip> content <keyword>         Search text files by content keyword
  validate <archive.zip>                           Check archive integrity
  create   <source_dir> <output.zip>               Create archive from directory
  create   --files <output.zip> <file1> <file2>    Create archive from individual files
  read     <archive.zip> <path/inside>             Read file content without extracting

Security protections are built-in for all extract operations — zip bomb detection,
path traversal prevention, dangerous extension blocking, symlink rejection, size limits.
"""
import zipfile
import fnmatch
import sys
import os
from pathlib import Path


# ============================================================
# Security configuration (applies to all extract operations)
# ============================================================
MAX_TOTAL_SIZE = 500 * 1024 * 1024       # 500 MB total decompressed
MAX_FILE_SIZE = 100 * 1024 * 1024        # 100 MB per individual file
MAX_FILE_COUNT = 10_000                   # max files to extract
MAX_COMPRESSION_RATIO = 100               # ratio above this = zip bomb suspect

BLOCKED_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.ps1', '.scr', '.vbs', '.vbe',
    '.js', '.jse', '.wsf', '.wsh', '.msi', '.com', '.pif',
    '.hta', '.cpl', '.inf', '.reg', '.rgs', '.sct', '.shb',
    '.lnk', '.dll', '.sys', '.drv',
}

TEXT_EXTENSIONS = {
    ".txt", ".csv", ".json", ".xml", ".html", ".md", ".log",
    ".yml", ".yaml", ".toml", ".ini", ".cfg",
}


# ============================================================
# Shared helpers
# ============================================================
def require_valid_zip(zip_path: str) -> None:
    """Exit with error if file doesn't exist or isn't a valid ZIP."""
    if not os.path.exists(zip_path):
        print(f"Error: File not found: {zip_path}")
        sys.exit(1)
    if not zipfile.is_zipfile(zip_path):
        print(f"Error: Not a valid ZIP file: {zip_path}")
        sys.exit(1)


# ============================================================
# list — show archive contents with compression stats
# ============================================================
def cmd_list(zip_path: str) -> None:
    require_valid_zip(zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        total_size = 0
        total_compressed = 0
        file_count = 0

        print(f"Archive: {zip_path}")
        print(f"{'Filename':<60s} {'Size':>12s} {'Compressed':>12s} {'Ratio':>7s}")
        print("-" * 95)

        for info in zf.infolist():
            if info.is_dir():
                continue
            file_count += 1
            total_size += info.file_size
            total_compressed += info.compress_size
            ratio = (1 - info.compress_size / info.file_size) * 100 if info.file_size > 0 else 0
            print(f"{info.filename:<60s} {info.file_size:>12,d} {info.compress_size:>12,d} {ratio:>6.1f}%")

        print("-" * 95)
        overall = (1 - total_compressed / total_size) * 100 if total_size > 0 else 0
        print(f"{'TOTAL':<60s} {total_size:>12,d} {total_compressed:>12,d} {overall:>6.1f}%")
        print(f"\nFiles: {file_count}")


# ============================================================
# extract — always runs security checks, no bypass option
# ============================================================
def cmd_extract(zip_path: str, output_dir: str, pattern: str = None) -> None:
    require_valid_zip(zip_path)

    # --- Pre-flight security validation ---
    with zipfile.ZipFile(zip_path, "r") as zf:
        bad = zf.testzip()
        if bad is not None:
            print(f"FAIL: Corrupted file in archive: {bad}")
            sys.exit(1)

        infos = [i for i in zf.infolist() if not i.is_dir()]

        if len(infos) > MAX_FILE_COUNT:
            print(f"BLOCKED: Too many files ({len(infos):,}). Max: {MAX_FILE_COUNT:,}")
            sys.exit(1)

        total_decompressed = sum(i.file_size for i in infos)
        if total_decompressed > MAX_TOTAL_SIZE:
            print(f"BLOCKED: Total size {total_decompressed:,} bytes exceeds {MAX_TOTAL_SIZE:,}")
            sys.exit(1)

        for info in infos:
            if info.compress_size > 0 and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
                ratio = info.file_size / info.compress_size
                print(f"BLOCKED: Zip bomb suspect — {info.filename} (ratio {ratio:.0f}:1)")
                sys.exit(1)
            if info.file_size > MAX_FILE_SIZE:
                print(f"BLOCKED: Oversized — {info.filename} ({info.file_size:,} bytes)")
                sys.exit(1)

    # --- Extract with per-file safety ---
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    extracted = blocked = errors = 0

    with zipfile.ZipFile(zip_path, "r") as zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        if pattern:
            infos = [i for i in infos if fnmatch.fnmatch(i.filename, pattern)]
            if not infos:
                print(f"No files matching pattern: {pattern}")
                sys.exit(1)

        for info in infos:
            # Path traversal check
            target = (output / info.filename).resolve()
            if not str(target).startswith(str(output)) or any(p == '..' for p in Path(info.filename).parts):
                print(f"  BLOCKED [path-traversal]: {info.filename}")
                blocked += 1
                continue

            # Dangerous extension check
            ext = os.path.splitext(info.filename)[1].lower()
            if ext in BLOCKED_EXTENSIONS:
                print(f"  BLOCKED [dangerous-ext]: {info.filename}")
                blocked += 1
                continue

            # Symlink check
            unix_attrs = info.external_attr >> 16
            if unix_attrs != 0 and (unix_attrs & 0o170000) == 0o120000:
                print(f"  BLOCKED [symlink]: {info.filename}")
                blocked += 1
                continue

            # Safe to extract
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                data = zf.read(info.filename)
                with open(target, "wb") as f:
                    f.write(data)
                extracted += 1
                print(f"  OK: {info.filename} ({info.file_size:,} bytes)")
            except Exception as e:
                print(f"  ERROR: {info.filename} — {e}")
                errors += 1

    print(f"\nDone: {extracted} extracted, {blocked} blocked, {errors} errors")


# ============================================================
# search — find files by name pattern or content keyword
# ============================================================
def cmd_search(zip_path: str, mode: str, query: str) -> None:
    require_valid_zip(zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        if mode == "name":
            matches = [n for n in zf.namelist() if fnmatch.fnmatch(n, query)]
            if matches:
                print(f"Files matching '{query}':")
                for m in matches:
                    info = zf.getinfo(m)
                    print(f"  {m} ({info.file_size:,} bytes)")
                print(f"\n{len(matches)} match(es)")
            else:
                print(f"No files matching: {query}")

        elif mode == "content":
            matches = []
            for name in zf.namelist():
                ext = os.path.splitext(name)[1].lower()
                if ext not in TEXT_EXTENSIONS:
                    continue
                try:
                    content = zf.read(name).decode("utf-8", errors="ignore")
                    if query.lower() in content.lower():
                        matches.append(name)
                except Exception:
                    continue
            if matches:
                print(f"Files containing '{query}':")
                for m in matches:
                    print(f"  {m}")
                print(f"\n{len(matches)} match(es)")
            else:
                print(f"No text files containing: {query}")
        else:
            print(f"Unknown search mode: {mode}. Use 'name' or 'content'.")
            sys.exit(1)


# ============================================================
# validate — check archive integrity
# ============================================================
def cmd_validate(zip_path: str) -> None:
    require_valid_zip(zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        bad = zf.testzip()
        count = len([i for i in zf.infolist() if not i.is_dir()])
        if bad is None:
            print(f"PASS: Archive valid ({count} files)")
        else:
            print(f"FAIL: Corrupted file: {bad}")
            sys.exit(1)


# ============================================================
# create — build archive from directory or file list
# ============================================================
def cmd_create(args: list) -> None:
    if args[0] == "--files":
        if len(args) < 3:
            print("Usage: zip-tool.py create --files <output.zip> <file1> <file2> ...")
            sys.exit(1)
        output_zip = args[1]
        file_paths = args[2:]
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for fp in file_paths:
                if not os.path.exists(fp):
                    print(f"  Warning: Skipping missing: {fp}")
                    continue
                zf.write(fp, os.path.basename(fp))
                print(f"  Added: {os.path.basename(fp)}")
        print(f"\nCreated: {output_zip} ({os.path.getsize(output_zip):,} bytes)")
    else:
        if len(args) < 2:
            print("Usage: zip-tool.py create <source_dir> <output.zip>")
            sys.exit(1)
        source = Path(args[0])
        output_zip = args[1]
        if not source.is_dir():
            print(f"Error: Directory not found: {args[0]}")
            sys.exit(1)
        count = 0
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for fp in sorted(source.rglob("*")):
                if fp.is_file():
                    arcname = fp.relative_to(source)
                    zf.write(fp, arcname)
                    count += 1
                    print(f"  Added: {arcname}")
        print(f"\nCreated: {output_zip} ({os.path.getsize(output_zip):,} bytes, {count} files)")


# ============================================================
# read — read single file content without extracting to disk
# ============================================================
def cmd_read(zip_path: str, inner_path: str) -> None:
    require_valid_zip(zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        if inner_path not in zf.namelist():
            print(f"Error: '{inner_path}' not found in archive")
            print(f"Available files: {', '.join(zf.namelist()[:20])}")
            sys.exit(1)
        try:
            content = zf.read(inner_path).decode("utf-8", errors="replace")
            print(content)
        except Exception as e:
            print(f"Error reading {inner_path}: {e}")
            sys.exit(1)


# ============================================================
# Main dispatcher
# ============================================================
USAGE = """Usage: python zip-tool.py <command> [args...]

Commands:
  list     <archive.zip>                           List contents
  extract  <archive.zip> <output_dir> [pattern]    Extract (security built-in)
  search   <archive.zip> name|content <query>      Search inside archive
  validate <archive.zip>                           Check integrity
  create   <source_dir> <output.zip>               Create from directory
  create   --files <output.zip> <file1> ...        Create from files
  read     <archive.zip> <path/inside>             Read file without extracting"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "list" and len(args) >= 1:
        cmd_list(args[0])
    elif command == "extract" and len(args) >= 2:
        cmd_extract(args[0], args[1], args[2] if len(args) > 2 else None)
    elif command == "search" and len(args) >= 3:
        cmd_search(args[0], args[1], args[2])
    elif command == "validate" and len(args) >= 1:
        cmd_validate(args[0])
    elif command == "create" and len(args) >= 1:
        cmd_create(args)
    elif command == "read" and len(args) >= 2:
        cmd_read(args[0], args[1])
    else:
        print(USAGE)
        sys.exit(1)
