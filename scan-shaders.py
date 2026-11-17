#!/usr/bin/env python3
# Scan a game-data folder for Xbox 360 shader containers (magic 0x102A1100).
#
#   python3 scan-shaders.py /path/to/gamedata
#
import sys, os, struct

MAGIC = 0x102A1100  # (flags & 0xFFFFFF00) == this; standard Xbox 360 shader container

def count_in(path):
    try:
        with open(path, 'rb') as f:
            d = f.read()
    except Exception:
        return 0
    n = len(d)
    cnt = 0
    # containers are 4-byte aligned; flags is big-endian on 360
    for i in range(0, n - 4, 4):
        v = struct.unpack('>I', d[i:i+4])[0]
        if (v & 0xFFFFFF00) == MAGIC:
            cnt += 1
    return cnt

def main():
    if len(sys.argv) < 2:
        print("usage: scan-shaders.py <gamedata-folder>")
        sys.exit(1)
    root = sys.argv[1]
    hits = []
    total = 0
    scanned = 0
    for dp, _, files in os.walk(root):
        for fn in files:
            p = os.path.join(dp, fn)
            sz = os.path.getsize(p) if os.path.exists(p) else 0
            # skip the giant media files to stay fast; shaders live in data/pack files
            scanned += 1
            c = count_in(p)
            if c:
                hits.append((c, sz, os.path.relpath(p, root)))
                total += c
    hits.sort(reverse=True)
    print(f"scanned {scanned} files under {root}")
    print(f"files containing Xbox 360 shader containers: {len(hits)}")
    print(f"total shader containers found: {total}")
    print("top shader-bearing files (count, bytes, path):")
    for c, sz, rp in hits[:40]:
        print(f"  {c:6d}  {sz:>12,}  {rp}")
    if hits:
        # list just the shader-bearing files for a minimal upload
        print("\n--- minimal file list (shader-bearing only) ---")
        for c, sz, rp in hits:
            print(rp)

if __name__ == "__main__":
    main()
