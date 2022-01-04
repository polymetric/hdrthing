import OpenImageIO as oiio
#import OpenEXR
#from PIL import Image
from os import listdir
from os.path import isfile, join
import re
import exifread
from fractions import Fraction
import math
import numpy as np

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def lerp(x, a, b):
    return x*(b-a)+a

def thing(base, clip, feather_stops):
    return np.clip(map(base, clip/(2**feather_stops), clip, 0, 1), 0, 1)

def load(file):
    return oiio.ImageInput.open(file).read_image(format="float")

def write(array, file):
    oiio.ImageBuf(array).write(file)

def randwrite(a, op):
    global t
    #write(a, f'{t}.exr')
    #print(f'{t}: {op}')
    t += 1

t=0

inpath = '.'
clip = 0.8
feather_stops = 0.1

files = [f for f in sorted(listdir(inpath)) if isfile(join(inpath, f)) and re.search('\.tiff$', f)]
composite = None
emptycomp = True

#exps = []
i = 0

for file in files:
    i = i + 1
#   img_exif = open(file, 'rb')
#   tags = exifread.process_file(img_exif)
#   time = float(Fraction(str(tags['EXIF ExposureTime'])))
#   iris = float(Fraction(str(tags['EXIF FNumber'])))
#   iso = int(str(tags['EXIF ISOSpeedRatings']))
#   exp = iris**2/(time*iso)
#   exps.append(exp)

    top = load(file)
    print(f'loaded {file}')

    if emptycomp:
        composite = top
        emptycomp = False
    else:
        mask = thing(composite, clip, feather_stops)
        randwrite(mask, 'mask')
        composite *= 0.5
        randwrite(composite, 'base')
        randwrite(top, 'top')
        composite = map(mask, 0, 1, composite, top)
        randwrite(composite, 'result')

    


#exps.sort(reverse=True)
#high_exp = exps[0]

#composite = oiio.ImageBufAlgo.div(composite, high_exp)
write(composite, 'gamer.exr')
oiio.ImageBuf(composite)

