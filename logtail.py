#!/usr/bin/env python3
"""LogTail — cross-platform log reader with follow and text filters."""
import argparse
import sys
import time
from pathlib import Path

def matches(line, include, exclude, ignore_case):
    text = line.lower() if ignore_case else line
    if include:
        needle = include.lower() if ignore_case else include
        if needle not in text:
            return False
    if exclude:
        needle = exclude.lower() if ignore_case else exclude
        if needle in text:
            return False
    return True

def emit(line, args, source):
    if matches(line, args.match, args.exclude, args.ignore_case):
        prefix = f"[{source}] " if args.multiple else ""
        print(prefix + line, end="" if line.endswith("\n") else "\n", flush=True)

def read_initial(path, args):
    try:
        with path.open("r", encoding=args.encoding, errors="replace") as file:
            if args.lines:
                for line in file.readlines()[-args.lines:]:
                    emit(line, args, path.name)
            else:
                for line in file:
                    emit(line, args, path.name)
    except OSError as error:
        print(f"{path}: {error}", file=sys.stderr)

def follow(paths, args):
    states = {}
    for path in paths:
        try:
            file = path.open("r", encoding=args.encoding, errors="replace")
            if not args.from_start:
                file.seek(0, 2)
            stat = path.stat()
            states[path] = (file, stat.st_ino)
        except OSError as error:
            print(f"{path}: {error}", file=sys.stderr)
    if not states:
        raise SystemExit("No readable files.")
    try:
        while True:
            changed = False
            for path, (file, inode) in list(states.items()):
                try:
                    stat = path.stat()
                    if stat.st_ino != inode or stat.st_size < file.tell():
                        file.close()
                        file = path.open("r", encoding=args.encoding, errors="replace")
                        states[path] = (file, stat.st_ino)
                    line = file.readline()
                    while line:
                        emit(line, args, path.name)
                        changed = True
                        line = file.readline()
                except OSError:
                    continue
            time.sleep(0.25 if changed else args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        for file, _ in states.values():
            file.close()

def main():
    parser = argparse.ArgumentParser(description="Read and follow text logs.")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("-n", "--lines", type=int, default=40, help="Show last N lines")
    parser.add_argument("-f", "--follow", action="store_true", help="Watch appended lines")
    parser.add_argument("--from-start", action="store_true", help="Start at beginning with --follow")
    parser.add_argument("-m", "--match", help="Only show lines containing this text")
    parser.add_argument("-x", "--exclude", help="Hide lines containing this text")
    parser.add_argument("-i", "--ignore-case", action="store_true")
    parser.add_argument("--encoding", default="utf-8")
    parser.add_argument("--interval", type=float, default=0.5, help="Polling interval")
    args = parser.parse_args()
    if args.lines < 0 or args.interval <= 0:
        raise SystemExit("lines must be >= 0 and interval > 0.")
    if args.follow:
        follow(args.files, args)
    else:
        args.multiple = len(args.files) > 1
        for path in args.files:
            read_initial(path, args)

if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        raise SystemExit(0)
