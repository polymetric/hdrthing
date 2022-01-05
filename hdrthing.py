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

#TODO replace with something other than OIIO
def load(file):
    return oiio.ImageInput.open(file).read_image(format="float")

#TODO replace with something other than OIIO
def write(array, file):
    oiio.ImageBuf(array).write(file)

def randwrite(a: oiio.ImageBuf, op: str):
    global t
    write(a, f'{t}.exr')
    print(f'{t}: {op}')
    t = t + 1

t=0

inpath = '.'
clip = 0.8
feather_stops = 1

files = [f for f in sorted(listdir(inpath)) if isfile(join(inpath, f)) and re.search('\.tiff$', f)]
composite = None
emptycomp = True
lastexp = None

exps = []
i = 0
exp = 1

for file in files:
    i += 1
#   img_exif = open(file, 'rb')
#   tags = exifread.process_file(img_exif)
#   time = float(Fraction(str(tags['EXIF ExposureTime'])))
#   iris = float(Fraction(str(tags['EXIF FNumber'])))
#   iso = int(str(tags['EXIF ISOSpeedRatings']))
#   exp = iris**2/(time*iso)
    exp /= 2
    exps.append(exp)

    top = load(file)
    top
    print(f'loaded {file} with EV {math.log(exp,2):.0f}')
#   randwrite(top * exp, 'top')

    if emptycomp:
        top /= exp
        composite = top
        emptycomp = False
    else:
        # always use the brighter image and then apply whatever is darker underneath
        if lastexp > exp:
            mask = thing(composite*lastexp, clip, feather_stops)
#           randwrite(composite, 'comp')
#           randwrite(composite/lastexp, 'comp/lastexp')
#           randwrite(top, 'top')
#           randwrite(mask, 'desc mask')
            top /= exp
            composite = lerp(mask, composite, top)
        else:
            mask = thing(top, clip, feather_stops)
#           randwrite(mask, 'asc mask')
            top /= exp
            composite = lerp(mask, top, composite)
    lastexp = exp

#exps.sort(reverse=True)
#high_exp = exps[0]

#composite = oiio.ImageBufAlgo.div(composite, high_exp)
write(composite, 'gamer.exr')

