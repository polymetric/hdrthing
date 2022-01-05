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

inpath = '.'
clip = 0.8
feather_stops = 1
absolute_exp = True

files = [f for f in sorted(listdir(inpath)) if isfile(join(inpath, f)) and re.search('\.tiff$', f)]
composite = None
lastexp = None
emptycomp = True

exps = []

for file in files:
    img_exif = open(file, 'rb')
    tags = exifread.process_file(img_exif)
    time = float(Fraction(str(tags['EXIF ExposureTime'])))
    iris = float(Fraction(str(tags['EXIF FNumber'])))
    iso = int(str(tags['EXIF ISOSpeedRatings']))
    exp = iris**-2*(time*iso)
    exps.append(exp)

    top = load(file)
    # ABSEV = absolute exposure value
    print(f'loaded {file} with ABSEV {math.log(exp,2):.0f}')

    if emptycomp:
        top /= exp
        composite = top
        emptycomp = False
    else:
        # always use the brighter image and then apply whatever is darker underneath
        if lastexp > exp:
            # we divide composite by lastexp to place it at wherever
            mask = thing(composite*lastexp, clip, feather_stops)
            top /= exp
            composite = lerp(mask, composite, top)
        else:
            mask = thing(top, clip, feather_stops)
            top /= exp
            composite = lerp(mask, composite, top)
    lastexp = exp

if not absolute_exp:
    exps.sort(reverse=True)
    high_exp = exps[0]
    composite /= high_exp

write(composite, 'gamer.exr')

