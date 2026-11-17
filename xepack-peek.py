#!/usr/bin/env python3
# Peek at a .XEPACK header to identify the format. Reads only.
#   python3 xepack-peek.py /path/to/file.XEPACK
import sys, struct
p = sys.argv[1]
d = open(p, 'rb').read(256)
sz = __import__('os').path.getsize(p)
print(f"file: {p}  ({sz:,} bytes)")
print("first 32 bytes (hex):", d[:32].hex(' '))
print("first 32 bytes (ascii):", ''.join(chr(b) if 32<=b<127 else '.' for b in d[:32]))
# format sniff
sigs = {
  b'PK\x03\x04': "ZIP (deflate) standard zip - extractable",
  b'PK\x05\x06': "ZIP (empty/eocd)",
  b'\x0f\xf5\x12\xee': "XCompress/LZX (Xbox 360 XMemCompress) - needs xbdecompress",
  b'\xff\xff\xff\xff': "possibly XCompress wrapper",
}
head4 = d[:4]
for sig, name in sigs.items():
    if d.startswith(sig):
        print("=> FORMAT:", name); break
else:
    # heuristics
    if d[:3] == b'\x10\x2a\x11':
        print("=> starts with a shader container magic — pack may be UNCOMPRESSED (raw concat)")
    else:
        print("=> unknown/custom header.")
        # check if it looks like plain text table of contents
# also: is there a readable filename table near the start?
printable = sum(1 for b in d if 32<=b<127)
print(f"printable ratio in first 256B: {printable/len(d):.0%} "
      f"({'potent. readable header/TOC' if printable>128 else 'mostly binary'})")
