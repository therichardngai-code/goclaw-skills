---
name: zip
version: 1.0.0
author: Richard Ng
license: MIT
description: "Use this skill whenever the user wants to work with ZIP archive files. This includes: reading or listing contents of .zip files, extracting files from archives, creating new .zip archives from files or directories, inspecting file sizes and compression ratios, extracting specific files or folders from an archive, searching for files inside archives by name or pattern, comparing contents of two archives, adding or removing files from existing archives, password-protecting archives, and batch-extracting multiple archives. Trigger when the user mentions '.zip', 'archive', 'compress', 'extract', 'unzip', or references a ZIP file by name or path. Do NOT use for .tar, .gz, .7z, .rar, or other non-ZIP archive formats unless converting to/from ZIP."
---

# ZIP Archive Tool

Single unified script: `python {baseDir}/scripts/zip-tool.py <command> [args...]`

Security is built-in — all extractions automatically run zip bomb detection, path traversal prevention, dangerous extension blocking, symlink rejection, and size limits. No unsafe mode exists.

## Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `list` | `zip-tool.py list archive.zip` | List contents with size & compression stats |
| `extract` | `zip-tool.py extract archive.zip output_dir/ [pattern]` | Extract files (security always on) |
| `search` | `zip-tool.py search archive.zip name "*.csv"` | Search by filename glob |
| `search` | `zip-tool.py search archive.zip content "keyword"` | Search text files by content |
| `validate` | `zip-tool.py validate archive.zip` | Check archive integrity |
| `create` | `zip-tool.py create source_dir/ output.zip` | Create from directory |
| `create` | `zip-tool.py create --files output.zip f1 f2` | Create from individual files |
| `read` | `zip-tool.py read archive.zip path/inside/file.txt` | Read file without extracting |

## Security Limits (Auto-Enforced)

| Protection | Limit |
|------------|-------|
| Zip bomb | Compression ratio >100:1 blocked |
| Path traversal | `..` components rejected |
| Dangerous files | 24 executable extensions blocked |
| Symlinks | Rejected |
| Per-file size | 100 MB max |
| Total size | 500 MB max |
| File count | 10,000 max |

## Password-Protected Archives (AES)

Not handled by zip-tool.py. Use `pyzipper` directly:

```python
import pyzipper

# Create encrypted
with pyzipper.AESZipFile("secure.zip", "w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
    zf.setpassword(b"password")
    zf.write("secret.txt")

# Read encrypted
with pyzipper.AESZipFile("secure.zip", "r") as zf:
    zf.setpassword(b"password")
    zf.extractall("output")
```
