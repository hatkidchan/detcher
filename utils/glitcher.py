from PIL import (
    Image, ImageDraw, ImageChops,
    ImageFilter, ImageEnhance,
    ImageFont, ImageColor
)
import numpy as np
from . import TimeMonitor
import zlib
import os
import json
import random


cwd = os.path.dirname(__file__)

mon = TimeMonitor()
font = ImageFont.truetype(os.path.join(cwd, "vcr.ttf"))
pal_file = os.path.join(cwd, "all-palettes.json")
palettes = json.load(open(pal_file, "r"))

HORIZ = "horiz"
VERT = "vert"
GRAYSCALE = "grayscale"
RGB = "RGB"
MULTIPLY = "multiply"
ADD = "add"
SUBTRACT = "subtract"
SCREEN = "screen"
DIFFERENCE = "difference"
L = "left"
C = "center"
R = "right"
PAL_BLACKANDWHITE = [
    [0, 0, 0],
    [255, 255, 255]
]


class Palettes(dict):
    def pick_random(self):
        return random.choice(list(self.values()))

    def find(self, query):
        for k, v in self.items():
            if query in k:
                return v
        return None

    def find_all(self, query):
        results = []
        for k, v in self.items():
            if query in k:
                results.append(v)
        return results


def LINEAR(v): return v


def SINEWAVE(v): return int(np.sin(v / 2) * 10)


def _shiftimg(im, ox, oy, crop=False):
    if crop:
        im2 = im.transform(im.size, 0, (1, 0, -ox, 0, 1, -oy))
    else:
        im2 = ImageChops.offset(im, ox, oy)
    return im2


def _shift_area_horiz(im, s, e, o):
    zone = im.crop((
        0, s,
        im.width, e
    ))
    zone = _shiftimg(zone, o, 0)
    im2 = im.copy()
    im2.paste(zone, (0, s))
    return im2


def _shift_area_vert(im, s, e, o):
    zone = im.crop((
        s, 0,
        e, im.height
    ))
    zone = _shiftimg(zone, 0, o)
    im2 = im.copy()
    im2.paste(zone, (s, 0))
    return im2


def _shift_auto_horiz(im, s, e, f):
    im2 = im.copy()
    for i in range(s, e + 1):
        zone = im.crop((0, i, im.width, i + 1))
        zone = _shiftimg(zone, int(f(i)), 0)
        im2.paste(zone, (0, i))
    return im2


def _shift_auto_vert(im, s, e, f):
    im2 = im.copy()
    for i in range(s, e + 1):
        zone = im.crop((i, 0, i + 1, im.height))
        zone = _shiftimg(zone, 0, int(f(i)))
        im2.paste(zone, (i, 0))
    return im2


def customConvert(silf, palette, dither=False):
    silf.load()
    palette.load()
    im = silf.im.convert("P", 1 if dither else 0, palette.im)
    return silf._new(im)


def flatten(array):
    result = []
    for v in array:
        if isinstance(v, list):
            result += flatten(v)
        else:
            result.append(v)
    return result


def _create_gray_noise(size, rng):
    noise_array = np.random.randint(*rng, size[::-1], dtype=np.uint8)
    mask = Image.fromarray(noise_array, 'L')
    return mask.convert('RGB')


def _create_rgb_noise(size, rngs):
    noise_array = np.random.randint(*rngs, size[::-1] + (3,), dtype=np.uint8)
    mask = Image.fromarray(noise_array, 'RGB')
    return mask


@mon
def shift_channels(image,
                   shift_r=(0, 0),
                   shift_g=(0, 0),
                   shift_b=(0, 0),
                   crop=False):
    if image.mode != "RGB":
        image = image.convert("RGB")
    r_chan, g_chan, b_chan = image.split()
    r_chan = _shiftimg(r_chan, *shift_r, crop=crop)
    g_chan = _shiftimg(g_chan, *shift_g, crop=crop)
    b_chan = _shiftimg(b_chan, *shift_b, crop=crop)
    return Image.merge("RGB", (r_chan, g_chan, b_chan))


@mon
def shift_area(image, mode=HORIZ, start=0, end=10, offset=20):
    if mode == HORIZ:
        return _shift_area_horiz(image,
                                 start, end, offset)
    if mode == VERT:
        return _shift_area_vert(image,
                                start, end, offset)


@mon
def shift_auto(image, mode=HORIZ, start=0, end=10, function=LINEAR):
    if mode == HORIZ:
        return _shift_auto_horiz(image,
                                 start, end, function)
    if mode == VERT:
        return _shift_auto_vert(image,
                                start, end, function)


@mon
def multiply_channels(image, r=1.0, g=1.0, b=1.0):
    r_chan, g_chan, b_chan = image.split()
    r_chan = ImageEnhance.Brightness(r_chan).enhance(r)
    g_chan = ImageEnhance.Brightness(g_chan).enhance(g)
    b_chan = ImageEnhance.Brightness(b_chan).enhance(b)
    return Image.merge("RGB", (r_chan, g_chan, b_chan))


@mon
def crt(image, step=(1, 1), values=(1.0, 0.5), fill=None):
    mask = Image.new('L', image.size, int(values[0] * 255))
    maskD = ImageDraw.Draw(mask)
    blank = Image.new('RGB', image.size, color=fill)
    for y in range(image.size[1]):
        if y % sum(step) < step[0]:
            maskD.line((0, y, image.size[0], y), fill=int(values[1] * 255))
    return Image.composite(image, blank, mask)


@mon
def overlay(image, offset=(0, 0), opacity=0.1, crop=False):
    shifted = _shiftimg(image, *offset, crop=crop)
    return Image.blend(shifted, image, opacity)


@mon
def grayscale(image, factor=0.0):
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)


@mon
def brightness(image, factor=1.0):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


@mon
def contrast(image, factor=1.0):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


@mon
def change_palette(image, palette=PAL_BLACKANDWHITE, dither=False):
    paletteImage = Image.new('P', (1, 1), None)
    if len(palette) > 256:
        raise ValueError("palette too big")
    for _ in range(256 - len(palette)):
        palette.append(palette[-1])
    paletteImage.putpalette(flatten(palette))
    return customConvert(image, paletteImage, dither=dither).convert('RGB')


multiply = mon(ImageChops.multiply)
add = mon(ImageChops.add)
subtract = mon(ImageChops.subtract)
screen = mon(ImageChops.screen)
difference = mon(ImageChops.difference)


@mon
def noise(image, minimal=0.5, maximal=1.0, palette=GRAYSCALE, mode=MULTIPLY):
    minimal, maximal = map(lambda v: int(v * 255), [minimal, maximal])
    if palette == GRAYSCALE:
        noise_image = _create_gray_noise(image.size, (minimal, maximal))
    if palette == RGB:
        if isinstance(minimal, (float, int)):
            minimal = (minimal,) * 3
        if isinstance(maximal, (float, int)):
            maximal = (maximal,) * 3
        noise_image = _create_rgb_noise(image.size, (minimal, maximal))
    if mode == MULTIPLY:
        return ImageChops.multiply(image, noise_image)
    if mode == ADD:
        return ImageChops.add(image, noise_image)
    if mode == SUBTRACT:
        return ImageChops.subtract(image, noise_image)
    if mode == SCREEN:
        return ImageChops.screen(image, noise_image)
    if mode == DIFFERENCE:
        return ImageChops.difference(image, noise_image)


@mon
def vhstext(image,
            pos=(0, 0),
            text="PLAY",
            fill=0xffffff,
            shadow=None,
            shadowradius=3,
            shadowfactor=5.0,
            size=12,
            align=C):
    image = image.convert("RGBA")
    fnt = font.font_variant(size=size)
    text_layer = Image.new("RGBA", image.size)
    shadow_layer = text_layer.copy()
    text_draw = ImageDraw.Draw(text_layer)

    if isinstance(fill, int):
        fill = "#%.6x" % fill
    if isinstance(shadow, int):
        shadow = "#%.6x" % shadow

    text_w, text_h = text_draw.textsize(text, font=fnt)
    if align == L:
        real_pos = (pos[0], pos[1])
    if align == C:
        real_pos = (pos[0] - text_w // 2, pos[1])
    if align == R:
        real_pos = (pos[0] - text_w, pos[1])
    text_draw.multiline_text(real_pos, text, fill=fill, font=fnt, align=align)

    if shadow is not None:
        radius = shadowradius
        fil = ImageFilter.BoxBlur(radius)
        shadow_bbox = (text_w + radius * 2, text_h + radius * 2)
        if align == L:
            outpos = (pos[0] - radius, pos[1] - radius)
        if align == C:
            outpos = (pos[0] - shadow_bbox[0] // 2, pos[1] - radius)
        if align == R:
            outpos = (pos[0] - shadow_bbox[0] + radius, pos[1] - radius)

        shadow_box = Image.new("RGBA", shadow_bbox)
        shadow_draw = ImageDraw.Draw(shadow_box)
        shadow_draw.multiline_text((
            radius, radius
        ), text, fill=shadow, font=fnt, align=align)
        shadow_box = shadow_box.filter(fil)
        chans = list(shadow_box.split())
        chans[3] = ImageEnhance.Brightness(chans[3]).enhance(shadowfactor)
        shadow_box = Image.merge("RGBA", chans)
        shadow_layer.paste(shadow_box, outpos)

    text_with_shadow = Image.alpha_composite(shadow_layer, text_layer)
    image = Image.alpha_composite(image, text_with_shadow)

    return image.convert("RGB")


def randrange(minv=1, maxv=10):
    return range(np.random.randint(minv, maxv))


def randXrange(image):
    start = np.random.randint(0, image.width)
    end = np.random.randint(start, image.width)
    return (start, end)


def randYrange(image):
    start = np.random.randint(0, image.height)
    end = np.random.randint(start, image.height)
    return (start, end)


exports = {}

for key in dir(np):
    value = getattr(np, key)
    if callable(value):
        exports[key] = value

exports.update(dict(
    shift_channels=shift_channels,
    shift_area=shift_area,
    shift_auto=shift_auto,
    multiply_channels=multiply_channels,
    crt=crt,
    overlay=overlay,
    grayscale=grayscale,
    brightness=brightness,
    contrast=contrast,
    noise=noise,
    vhstext=vhstext,

    multiply=multiply,
    add=add,
    subtract=subtract,
    screen=screen,
    difference=difference,
    getrgb=ImageColor.getrgb,
    change_palette=change_palette,

    np=np,
    random=random,
    Image=Image,
    ImageDraw=ImageDraw,
    ImageChops=ImageChops,
    ImageFilter=ImageFilter,
    ImageEnhance=ImageEnhance,

    randrange=randrange,
    randXrange=randXrange,
    randYrange=randYrange,

    HORIZ=HORIZ,
    VERT=VERT,
    GRAYSCALE=GRAYSCALE,
    RGB=RGB,
    MULTIPLY=MULTIPLY,
    ADD=ADD,
    SCREEN=SCREEN,
    DIFFERENCE=DIFFERENCE,
    SUBTRACT=SUBTRACT,
    L=L,
    C=C,
    R=R,

    palettes=Palettes(palettes),

    mon=mon
))
