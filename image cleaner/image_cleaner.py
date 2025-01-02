# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 12:55:47 2020

@author: SamBennett
"""

from PIL import Image, ImageChops

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

im = Image.open("test_2.png")
im = trim(im)
im.show()

im = Image.open("test.png")
im = trim(im)
im.show()