#!/usr/bin/env python3
import OpenImageIO as oiio
#import OpenEXR
#from PIL import Image
from os import listdir
import os
from os.path import isfile, join
from sys import argv
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

root = os.path.realpath(os.path.curdir)
result_count = 0

for inpath in argv[1:]:
    try:
        #inpath = '.'
        print(f'processing dir {inpath}')
        os.chdir(root)
        os.chdir(inpath)
        clip = 0.8
        feather_stops = 1
        absolute_exp = True
        
        files = [f for f in sorted(listdir('.')) if isfile(f) and re.search('\.tiff$', f)]
        if len(files) < 1:
            print('empty')
            continue
        composite = None
        lastexp = None
        emptycomp = True
        
        images = []
        
        for file in files:
            img_exif = open(file, 'rb')
            tags = exifread.process_file(img_exif)
            time = float(Fraction(str(tags['EXIF ExposureTime'])))
            iris = float(Fraction(str(tags['EXIF FNumber'])))
            iso = int(str(tags['EXIF ISOSpeedRatings']))
            exp = iris**-2*(time*iso)
            images.append((file, exp))

        # sort by exposure descending
        images.sort(key=lambda image: image[1], reverse=True)

        for file, exp in images:
            top = load(file)
            # ABSEV = absolute exposure value
            print(f'loaded {file} with ABSEV {round(math.log(exp,2))}')
        
            if emptycomp:
                # dividing by a value proportional to the camera's exposure settings places each image
                # where it should be relative to the others
                top /= exp
                composite = top
                emptycomp = False
            else:
                # always use the brighter image and then apply whatever is darker underneath
                if lastexp > exp:
                    # we divide composite by lastexp to place it at wherever
                    # it was exposed at, effectively undoing our previous division by the exposure value
                    mask = thing(composite*lastexp, clip, feather_stops)
                    top /= exp
                    composite = lerp(mask, composite, top)
                else:
                    # this should not happen
                    mask = thing(top, clip, feather_stops)
                    top /= exp
                    composite = lerp(mask, composite, top)
            lastexp = exp
        
        if not absolute_exp:
            high_exp = images[0][1] # exposure of first (brighest image)
            composite /= high_exp
        
        os.chdir(root)
        print(f'saving as result{result_count}.exr')
        write(composite, f'result{result_count}.exr')
        result_count += 1
        print(f'finished dir {inpath}')
    except KeyError as e:
        print(f"file doesn't have exif data!")
        continue

