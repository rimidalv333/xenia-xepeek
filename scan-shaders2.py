#!/usr/bin/env python3
# Fast scan of a game-data folder for Xbox 360 shader containers.
# Prints progress; uses bulk byte search (not a per-byte Python loop).
# Reads only, moves/changes nothing.
#
#   python3 scan-shaders2.py /path/to/gamedata
#
import sys, os, struct

# Xbox 360 shader container: a uint32 'flags' where (flags & 0xFFFFFF00)==0x102A1100.
# Big-endian on 360, so the bytes are 10 2A 11 xx. We search for the 3-byte prefix
# 10 2A 11 on 4-byte boundaries.
PREFIX = b'\x10\x2a\x11'

def count_in(path, filesize):
    found = 0
    try:
        with open(path, 'rb') as f:
            # read in 8MB chunks, keep 3-byte overlap across chunk edges
            overlap = b''
            base = 0
            while True:
                chunk = f.read(8 << 20)
                if not chunk:
                    break
                buf = overlap + chunk
                start = 0
                while True:
                    j = buf.find(PREFIX, start)
                    if j < 0:
                        break
                    # absolute offset of this match
                    abspos = base - len(overlap) + j
                    # must be on a 4-byte boundary (container flags is aligned)
                    if abspos % 4 == 0:
                        found += 1
                    start = j + 1
                overlap = buf[-3:]
                base += len(chunk)
    except Exception:
        return 0
    return found

def human(n):
    for u in ('B','KB','MB','GB'):
        if n < 1024: return f"{n:.0f}{u}"
        n /= 1024
    return f"{n:.0f}TB"

def main():
    if len(sys.argv) < 2:
        print("usage: scan-shaders2.py <gamedata-folder>")
        sys.exit(1)
    root = sys.argv[1]
    allfiles = []
    for dp, _, files in os.walk(root):
        for fn in files:
            p = os.path.join(dp, fn)
            try: sz = os.path.getsize(p)
            except OSError: sz = 0
            allfiles.append((p, sz))
    print(f"found {len(allfiles)} files under {root}; scanning...", flush=True)
    hits = []
    total = 0
    for i, (p, sz) in enumerate(allfiles, 1):
        c = count_in(p, sz)
        if c:
            hits.append((c, sz, os.path.relpath(p, root)))
            total += c
        if i % 50 == 0 or i == len(allfiles):
            print(f"  [{i}/{len(allfiles)}] scanned, shaders so far: {total}", flush=True)
    hits.sort(reverse=True)
    print("\n================ RESULT ================", flush=True)
    print(f"files containing Xbox 360 shader containers: {len(hits)}")
    print(f"total shader containers found: {total}")
    print("shader-bearing files (count, size, path):")
    for c, sz, rp in hits:
        print(f"  {c:6d}  {human(sz):>8}  {rp}")
    print("========================================", flush=True)

if __name__ == "__main__":
    main()
