import os
from math import cos, pi, sin, tau

import vpython as vp
from vpython import vec
# from vpython import canvas, mag, vec, box

if os.name == "posix":
    scene = vp.canvas(width=950, height=1870)
else:
    scene = vp.canvas(width=1500, height=690)

width = 16
depth = 16

scale = 1
centering_shift = (
    - vec(width, 0, depth) / 2  # move the center of the shape to the origin
    + vec(1, 0, 1) / 2  # shift to the exact center from the center of the box
)

box_size = vec(1, 1, 1)
box_size /= 1.1  # each box is slightly separated from the others
box_size /= scale

boxes = []
for i in range(width):
    boxes.append([])
    for j in range(depth):
        box = vp.box(size=box_size)
        box.pos = (vec(i, 0, j) + centering_shift) / scale
        box.rotate(pi*0.25, axis=vec(0, 1, 0), origin=vec(0, 0, 0))
        box.rotate(pi*0.2, axis=vec(1, 0, 0), origin=vec(0, 0, 0))
        boxes[i].append(box)

time = 0
min_height = 0.5
sin_scale = 30
time_change = -0.225
height_multiplier = 6

while 1:
    vp.rate(45)
    for line_of_boxes in boxes:
        for box in line_of_boxes:
            ang = (box.pos.mag**2 + time) / sin_scale
            box.height = (
                1 + sin(ang)  # from 0 to 2
                + min_height
            ) * height_multiplier / scale

    time += time_change
