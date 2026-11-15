#!/usr/bin/env python3
"""Check local Terralith/Terratonic 26.3 datapack ZIPs; no network needed."""
import argparse
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile

NAMES = ['01-terralith.zip', '02-terratonic.zip']


def version_compat(pack: dict):
    entry = pack.get('pack', {})
    # MC 26.3 datapack format is 121.0; formats may also be given as ranges.
    legacy = entry.get('pack_format')
    minimum = entry.get('min_format')
    maximum = entry.get('max_format')
    if minimum is not None and maximum is not None:
        try:
            a = int(minimum[0] if isinstance(minimum, list) else minimum)
            b = int(maximum[0] if isinstance(maximum, list) else maximum)
            return a <= 121 <= b
        except (TypeError, ValueError, IndexError):
            return None
    if isinstance(legacy, (int, float)):
        return int(legacy) == 121
    return None


def check(root: Path):
    problems = []
    for name in NAMES:
        path = root / name
        if not path.exists():
            problems.append(f'MISSING {path}')
            continue
        try:
            with ZipFile(path) as z:
                names = z.namelist()
                if 'pack.mcmeta' not in names:
                    problems.append(f'INVALID {name}: pack.mcmeta not at ZIP root')
                    continue
                if not any(s.startswith('data/') for s in names):
                    problems.append(f'INVALID {name}: no data/ root')
                if z.testzip() is not None:
                    problems.append(f'INVALID {name}: bad CRC')
                pack = json.loads(z.read('pack.mcmeta'))
                compatibility = version_compat(pack)
                print(f'{name}: {len(names)} entries, pack={pack.get("pack", {})}')
                if compatibility is False:
                    problems.append(f'INCOMPATIBLE? {name}: pack format excludes 26.3 (121)')
                elif compatibility is None:
                    print(f'WARNING {name}: format range cannot be established automatically')
        except (OSError, BadZipFile, ValueError, UnicodeDecodeError) as e:
            problems.append(f'INVALID {name}: {e}')
    for problem in problems:
        print(problem)
    if not problems:
        print('Basic ZIP verification OK; Minecraft registry load must still be tested.')
    return 1 if problems else 0


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('directory', type=Path)
    args = p.parse_args()
    raise SystemExit(check(args.directory))
