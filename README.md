# Graphical Diff Tool

So I am trying to build a un-signed firmware for a Samsung Chromebook and
was curious about what was different in the firmware blobs. So I hack this
little took together.

## Requirements

- python
- pygame

## Usage

Run it something like so

    python main.py test-files/nv_image-snow.bin test-files/original-rom.bin

Use the left and right keys to jump left and right a 'block' and use 'enter'
to drop into a finer grained detail view. Use arrow keys again and press 
'enter' again to see the smallest level of detail.

## Copyright 

By Ivan Kocienski (c) 2016 / BSD license.

