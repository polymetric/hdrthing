import OpenImageIO as oiio
import OpenEXR
from PIL import Image
from PIL.TiffTags import TAGS
from os import listdir
from os.path import isfile, join
import re
import exifread
from fractions import Fraction

def clamp(x, l, h):
    return max(l, min(h, x))

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def thing(p, clip, feather_stops):
    return clamp(map(p, clip/(2^feather_stops), clip, 1, 0), 0, 1)

inpath = '.'
clip = 0.8
feather_stops = 1

composite = oiio.ImageBufAlgo.zero(oiio.ROI(0,512,0,512,0,1,0,3))

for file in [f for f in listdir(inpath) if isfile(join(inpath, f)) and re.search('\.tiff$', f)]:
    img_input = oiio.ImageInput.open(file)
    image = img_input.read_image(format="float")

    img_exif = open(file, 'rb')
    tags = exifread.process_file(img_exif)
    time = float(Fraction(str(tags['EXIF ExposureTime'])))
    iris = float(Fraction(str(tags['EXIF FNumber'])))
    iso = int(str(tags['EXIF ISOSpeedRatings']))
    exp = iris**2/(time*iso)

    for column in image:
        for pixel in column:
            for c in pixel:
                # multiply the brighness of each pixel
                # based on how close it is to clipping
                c *= thing(c, clip, feather_stops)
    image = ImageBuf(image)
    image = oiio.ImageBufAlgo.div(image, exp)
    composite = oiio.ImageBufAlgo.add(composite, image)

images.sort(key=lambda image: image[0])
base_exp = images[0][0]

composite = oiio.ImageBufAlgo.mul(composite, base_exp*2**10) # temp add 10 stops for debug
composite.write('gamer.exr')

