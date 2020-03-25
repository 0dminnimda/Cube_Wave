from vpython import *
from time import time as t
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
pass

#print(len(boxes), len(boxes[0]), len(boxes[0][0]))

#a = 0
#aa = pi*0.0005
#f = vec(0, -0.5, -1)
#scene.camera.pos *= 2 # = vec(0, 0, 6)
#scene.camera.axis *= 2
#scene.camera.axis
#print(scene.center)
#print(scene.autoscale)
#atrs = 'pos', 'axis'

a = 0
h = 0.5

while 1:
    #rate(200)

    for i in range(widt):
        for j in range(dept):
            d = mag(boxes[i][j].pos)**2
            boxes[i][j].height = (1 + h + sin((d+a)/30))*6

    a -= 0.225



    #a += aa
    #for i in atrs:
    #    print(scene.camera.__getattribute__(i), end="  ")
    #print()
    #ls = scene.center
    #scene.camera.pos = scene.camera.pos.rotate(pi*0.001, axis=vec(1, 1, 1))

    #scene.forward = f.rotate(a, axis=vec(0, 1, 0))

    #scene.camera.rotate(pi*0.001, axis=vec(0, 0, 1), origin=scene.center)
