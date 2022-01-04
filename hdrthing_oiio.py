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
#   print(f'map x: {x}, in_min: {in_min}, in_max: {in_max}, out_min: {out_min}, out_max: {out_max}')
    return add(div(mul(sub(x, in_min), out_max - out_min), in_max - in_min), out_min)

#def oiio_map(x, in_min, in_max, out_min, out_max):
##   print(f'map x: {x}, in_min: {in_min}, in_max: {in_max}, out_min: {out_min}, out_max: {out_max}')
#    return add(div(mul(sub(x, in_min), sub(out_max, out_min), in_max, in_min)), out_min)

def oiio_lerp(x, out_min, out_max):
#   randwrite(x, 'lerp_mask')
#   randwrite(out_min, 'lerp_a')
#   randwrite(out_max, 'lerp_b')
#   print('lerp')
    return add(mul(x, sub(out_max, out_min)), out_min)

def thing(base, clip, feather_stops):
#   print('thing')
    # could optimize with contrast_remap function
    return oiio_clamp(oiio_map(base, clip/(2**feather_stops), clip, 1, 0), 0, 1)

def add(a, b):
#   print('add')
    return oiio.ImageBufAlgo.add(a, b)

def sub(a, b):
#   print('sub')
    return oiio.ImageBufAlgo.sub(a, b)

def mul(a, b):
#   print('mul')
    return oiio.ImageBufAlgo.mul(a, b)

def div(a, b):
#   print('div')
    return oiio.ImageBufAlgo.div(a, b)

def oiio_clamp(x, a, b):
#   print('clamp')
    randwrite(x, 'clamp_x')
    return oiio.ImageBufAlgo.clamp(x, a, b)

def randwrite(a: oiio.ImageBuf, op: str):
    global t
    a.write(f'{t}.exr')
    print(f'{t}: {op}')
    t = t + 1

t=0

inpath = '.'
clip = 0.8
feather_stops = 1

files = [f for f in sorted(listdir(inpath)) if isfile(join(inpath, f)) and re.search('\.tiff$', f)]
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

    temp = oiio.ImageBuf(file)
    image = oiio.ImageBuf()
    image.copy(temp, oiio.FLOAT)
    print(f'opened {file}')
    
    if emptycomp:
        composite = oiio.ImageBuf()
        composite.copy(image, oiio.FLOAT)
        emptycomp = False
    else:
        mask = thing(image, clip, feather_stops)
#       mask.write(f'mask{i}.exr')
#       image = mul(image, 1/exp)

        composite = mul(composite, 0.5)
        composite = oiio_lerp(mask, composite, image)
    randwrite(composite, 'inter')
    

#exps.sort(reverse=True)
#high_exp = exps[0]

#composite = oiio.ImageBufAlgo.div(composite, high_exp)
composite.write('gamer.exr')

