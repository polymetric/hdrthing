import OpenImageIO as oiio
import OpenEXR
from PIL import Image
from PIL.TiffTags import TAGS
from os import listdir
from os.path import isfile, join
import re
import exifread
from fractions import Fraction
import math

def clamp(x, l, h):
    return max(l, min(h, x))

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def oiio_map(x, in_min, in_max, out_min, out_max):
    print(f'map x: {x}, in_min: {in_min}, in_max: {in_max}, out_min: {out_min}, out_max: {out_max}')
    return add(div(mul(sub(x, in_min), out_max - out_min), in_max - in_min), out_min)

def oiio_lerp(x, out_min, out_max):
    print('lerp')
    return add(mul(x, sub(out_max, out_min)), out_min)

def thing(base, clip, feather_stops):
    print('thing')
    return oiio_clamp(oiio_map(base, clip/(2**feather_stops), clip, 0, 1), 0, 1)

def add(a, b):
    print('add')
    return oiio.ImageBufAlgo.add(a, b)

def sub(a, b):
    print('sub')
    return oiio.ImageBufAlgo.sub(a, b)

def mul(a, b):
    print('mul')
    return oiio.ImageBufAlgo.mul(a, b)

def div(a, b):
    print('div')
    return oiio.ImageBufAlgo.div(a, b)

def oiio_clamp(x, a, b):
    print('clamp')
    return oiio.ImageBufAlgo.clamp(x, a, b)

inpath = '.'
clip = 0.8
feather_stops = 1

files = [f for f in sorted(listdir(inpath)) if isfile(join(inpath, f)) and re.search('\.tiff$', f)]
composite = oiio.ImageBuf(files[0])
oiio.ImageBufAlgo.zero(composite)

exp = 1
exps = []
i=0

for file in files:
#   img_exif = open(file, 'rb')
#   tags = exifread.process_file(img_exif)
#   time = float(Fraction(str(tags['EXIF ExposureTime'])))
#   iris = float(Fraction(str(tags['EXIF FNumber'])))
#   iso = int(str(tags['EXIF ISOSpeedRatings']))
#   exp = iris**2/(time*iso)
    exps.append(exp)
    exp /= 2

    image = oiio.ImageBuf(file)
    print(f'opened {file}')

    mask = thing(image, clip, feather_stops)
    mask.write(f"beef{i}.exr")
    image = mul(image, exp)
    i+=1

    composite = oiio_lerp(mask, image, composite)
    

exps.sort(reverse=True)
high_exp = exps[0]

#composite = oiio.ImageBufAlgo.div(composite, high_exp)
composite.write('gamer.exr')

