# xenia-xepeek
XEPACK file reverse engineering tools

Inspec X360 game data & XEPACK file headers to identify compression formats, signatures and potential shader containers.
Scan game-dat directories for X360 shader-container signatures (0x102A1100) and reports matching files and occurrence counts.
Second iteration provides chunk-based reading and bulk byte searching for improved performance. Requires Python3 without external dependencies.

Software under the GNU General Public License v3.0 (GPL-3.0). You are free to use, modify, redistribute and share.
See GNU GPL v3.0 for the full license terms.
