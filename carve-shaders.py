#!/usr/bin/env python3
# Carve Xbox 360 shader containers out of SM3/SWoS game files, AND
# diagnose container header to learn real format.
# Read only - no file modification.
#
#   python3 carve-shaders.py <folder-or-file> <out-folder> [--max N]
#
# XenosRecomp's strict container test (big-endian uint32 header, 9 words):
#   [0] flags  [1] virtualSize  [2] physicalSize  [3] fieldC
#   [4] constantTableOffset  [5] definitionTableOffset  [6] shaderOffset
#   [7] field1C  [8] field20
#   accept if (flags & 0xFFFFFF00)==0x102A1100 and field1C==0 and field20==0
#   and 0 < virtualSize+physicalSize <= bytesRemaining.
# Also carve 'loose' hits (magic but failing the strict test) using a
# best-effort length (up to the next magic, capped), so nothing is missed,
# & print the header fields of the first several hits.
import sys, os, struct, hashlib

def be32(b,o): return struct.unpack_from('>I', b, o)[0]
PREFIX = b'\x10\x2a\x11'

def scan(data):
    """Yield (offset, header9, strict_ok, dsz) for each aligned magic."""
    n=len(data); i=data.find(PREFIX)
    while i>=0:
        if i%4==0 and i+40<=n:
            fl=be32(data,i)
            if (fl & 0xFFFFFF00)==0x102A1100:
                hdr=[be32(data,i+o) for o in (0,4,8,0xC,0x10,0x14,0x18,0x1C,0x20)]
                dsz=hdr[1]+hdr[2]
                strict = (hdr[7]==0 and hdr[8]==0 and 0<dsz<=(n-i))
                yield i,hdr,strict,dsz
        i=data.find(PREFIX,i+1)

def main():
    if len(sys.argv)<3:
        print("usage: carve-shaders.py <folder-or-file> <out-folder> [--max N]"); sys.exit(1)
    src,out=sys.argv[1],sys.argv[2]
    mx=None
    if "--max" in sys.argv: mx=int(sys.argv[sys.argv.index("--max")+1])
    os.makedirs(out,exist_ok=True)
    files=[src] if os.path.isfile(src) else [os.path.join(dp,fn) for dp,_,fs in os.walk(src) for fn in fs]

    seen=set(); total=0; strict_total=0; loose_total=0; diag=[]
    for p in files:
        try: data=open(p,'rb').read()
        except: continue
        if PREFIX not in data: continue
        hits=list(scan(data))
        if not hits: continue
        offs=[h[0] for h in hits]
        for idx,(off,hdr,strict,dsz) in enumerate(hits):
            if len(diag)<24:
                diag.append((os.path.basename(p),off,hdr,strict,dsz))
            if strict:
                blob=data[off:off+dsz]; strict_total+=1
            else:
                # best-effort: up to next magic, capped at 64KB
                nxt=offs[idx+1] if idx+1<len(offs) else len(data)
                end=min(nxt, off+65536, len(data))
                blob=data[off:end]; loose_total+=1
            h=hashlib.sha1(blob).hexdigest()[:12]
            if h in seen: continue
            seen.add(h)
            tag="strict" if strict else "loose"
            base=os.path.basename(p).replace('.','_')
            name=f"{base}_{off:08x}_{tag}_{h}_{len(blob)}.bin"
            open(os.path.join(out,name),'wb').write(blob)
            total+=1
            if mx and total>=mx: break
        if mx and total>=mx: break

    print(f"wrote {total} distinct containers to {out}  (strict={strict_total}, loose={loose_total})")
    print("\n--- header diagnosis (first hits) ---")
    print(f"{'file':<22}{'offset':>10} | flags    virt     phys     fieldC   cTbl     dTbl     shOff    f1C      f20      | strict dsz")
    for fn,off,hdr,strict,dsz in diag:
        print(f"{fn:<22}{off:>10} | " + " ".join(f"{x:08x}" for x in hdr) + f" | {str(strict):<6} {dsz}")

if __name__=="__main__":
    main()
