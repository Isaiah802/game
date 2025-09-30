"""Migration utility: split legacy sounds into songs/ and sfx/ folders.

Usage:
    python migrate_sounds.py [--source PATH] [--assets PATH] [--dry-run] [--yes]

Behavior:
 - Detects legacy folder (defaults to <repo>/assets/sounds).
 - Creates <assets>/songs and <assets>/sfx if missing.
 - Moves files using extension/keyword heuristics:
     * music extensions: .mp3, .flac, .m4a
     * sfx extensions: .wav, .aiff
     * .ogg and others: classified by filename keywords (click, sfx, fx, beep, mouse)
 - Prints a summary. With --dry-run it only prints planned moves.
 - With --yes it proceeds without prompting.

This is a small helper to keep your repo organized when switching to the
new audio layout used by the project (assets/songs + assets/sfx).
"""

from __future__ import annotations
import argparse
import os
import shutil
from pathlib import Path
from typing import List, Tuple


MUSIC_EXTS = {'.mp3', '.flac', '.m4a', '.ogg'}
SFX_EXTS = {'.wav', '.aiff', '.aif'}
SFX_KEYWORDS = {'click', 'mouse', 'sfx', 'fx', 'beep', 'hit', 'pop', 'tap'}


def classify_file(name: str) -> str:
    """Return 'song' or 'sfx' for the filename."""
    p = Path(name)
    ext = p.suffix.lower()
    lower = p.name.lower()
    if ext in SFX_EXTS:
        return 'sfx'
    if ext in MUSIC_EXTS:
        # prefer songs for typical music extensions, but check for sfx keywords
        for kw in SFX_KEYWORDS:
            if kw in lower:
                return 'sfx'
        return 'song'
    # fallback: look for keywords
    for kw in SFX_KEYWORDS:
        if kw in lower:
            return 'sfx'
    # default to song
    return 'song'


def ensure_dir(p: Path):
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)


def unique_target(target: Path) -> Path:
    """If target exists, append a numeric suffix to find a unique name."""
    if not target.exists():
        return target
    base = target.stem
    ext = target.suffix
    parent = target.parent
    i = 1
    while True:
        candidate = parent / f"{base}_{i}{ext}"
        if not candidate.exists():
            return candidate
        i += 1


def migrate(source: Path, assets_base: Path, dry_run: bool = True) -> Tuple[List[Tuple[Path, Path]], List[str]]:
    """Return list of moves (src, dst) and list of skipped items.

    Does not perform moves when dry_run is True.
    """
    songs = assets_base / 'songs'
    sfx = assets_base / 'sfx'
    ensure_dir(songs)
    ensure_dir(sfx)

    moves: List[Tuple[Path, Path]] = []
    skipped: List[str] = []

    if not source.exists():
        return moves, [f"source folder not found: {source}"]

    for entry in sorted(source.iterdir()):
        if entry.is_dir():
            # skip directories (no recursion)
            skipped.append(f"directory: {entry}")
            continue
        if entry.name.startswith('.'):
            skipped.append(f"hidden: {entry.name}")
            continue
        kind = classify_file(entry.name)
        target_base = songs if kind == 'song' else sfx
        target = target_base / entry.name
        target = unique_target(target)
        moves.append((entry, target))

    # perform moves
    if not dry_run:
        for src, dst in moves:
            shutil.move(str(src), str(dst))

    return moves, skipped


def main(argv: List[str] | None = None):
    p = argparse.ArgumentParser(description='Migrate legacy sounds into songs/ and sfx/')
    p.add_argument('--source', '-s', help='legacy source folder (defaults to assets/sounds)')
    p.add_argument('--assets', '-a', help='assets base folder (defaults to assets)')
    p.add_argument('--dry-run', action='store_true', help='show planned moves but do not perform them')
    p.add_argument('--yes', action='store_true', help='do not prompt, assume yes')
    args = p.parse_args(argv)

    repo_dir = Path(__file__).resolve().parents[1]
    default_assets = repo_dir / 'assets'

    assets_base = Path(args.assets) if args.assets else default_assets
    if args.source:
        source = Path(args.source)
    else:
        legacy = assets_base / 'sounds'
        if legacy.exists():
            source = legacy
        else:
            # fall back to assets_base itself
            source = assets_base

    print(f"Source: {source}")
    print(f"Assets base: {assets_base}")
    dry_run = args.dry_run or True

    moves, skipped = migrate(source, assets_base, dry_run=dry_run)

    if not moves:
        print("No files to migrate.")
        for s in skipped:
            print('Skipped:', s)
        return 0

    print("Planned moves:")
    for src, dst in moves:
        print(f"  {src} -> {dst}")
    if skipped:
        print('\nSkipped items:')
        for s in skipped:
            print('  ', s)

    if dry_run:
        print('\nDry-run mode: no files were moved.')
        if args.yes:
            print('But --yes was given; performing moves now...')
        else:
            ans = input('Perform these moves? [y/N]: ')
            if ans.strip().lower() not in ('y', 'yes'):
                print('Aborted.')
                return 0

    # perform actual move
    for src, dst in moves:
        final_dst = unique_target(dst)
        print(f"Moving: {src} -> {final_dst}")
        shutil.move(str(src), str(final_dst))

    print('Migration complete.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
