from vpython import *
from math import sin, cos, tau, pi
import os

if os.name == "posix":
    scene = canvas(width=950, height=1870)
else:
    scene = canvas(width=1500, height=690)

widt = 16
dept = 16
a = 1.1

boxes = []
for i in range(widt):
    boxes.append([])
    for j in range(dept):
        v = vec(i-widt/2+0.5, 0, j-dept/2+0.5)*a
        boxes[i].append(box(pos=v))
        boxes[i][j].rotate(pi*0.25, axis=vec(0, 1, 0), origin=vec(0, 0, 0))
        boxes[i][j].rotate(pi*0.2, axis=vec(1, 0, 0), origin=vec(0, 0, 0))

a = 0
h = 0.5

while 1:
    for i in range(widt):
        for j in range(dept):
            d = mag(boxes[i][j].pos)**2
            boxes[i][j].height = (1 + h + sin((d+a)/30))*6

    a -= 0.225
