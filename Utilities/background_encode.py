# Encodes a background from a PNG to BIN
# Colors 0-7 in the palette are represented by black, red, green, yellow, blue, magenta, cyan, and white
# Colors 8-255 are currently unsupported

from PIL import Image
import sys
from os import path

if len(sys.argv) < 2:
    print('Usage: python background_encode.py [source].png')
    sys.exit(0)
    
fname = sys.argv[1]
if not path.isfile(fname):
    print('Error: file', fname, 'does not exist')
    sys.exit(0)
    
ss_img = Image.open(fname, 'r')
ss = list(ss_img.getdata())
ss2 = []

for i in range(96*64):
    ind = 4*int(ss[i][2] > 127) + 2*int(ss[i][1] > 127) + int(ss[i][0] > 127)
    ss2 += [ind]

fname2 = fname[:-3] + 'bin'
fp = open(fname2, 'wb+')
fp.write(bytes(ss2))
fp.close()