# Encodes a spritesheet from a PNG to BIN
# Colors 0-7 in the palette are represented by black, red, green, yellow, blue, magenta, cyan, and white
# Colors 8-15 are currently unsupported

from PIL import Image
import sys
from os import path

if len(sys.argv) < 2:
    print('Usage: python spritesheet_encode.py [source].png')
    sys.exit(0)
    
fname = sys.argv[1]
if not path.isfile(fname):
    print('Error: file', fname, 'does not exist')
    sys.exit(0)
    
ss_img = Image.open(fname, 'r')
ss = list(ss_img.getdata())
ss2 = []

for i in range(48*64):
    ind1 = 4*int(ss[2*i][2] > 127) + 2*int(ss[2*i][1] > 127) + int(ss[2*i][0] > 127)
    ind2 = 4*int(ss[2*i+1][2] > 127) + 2*int(ss[2*i+1][1] > 127) + int(ss[2*i+1][0] > 127)
    ss2 += [ind1*16+ind2]

fname2 = fname[:-3] + 'bin'
fp = open(fname2, 'wb+')
fp.write(bytes(ss2))
fp.close()