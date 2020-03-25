from vpython import *
from time import time as t
from math import sin, cos, tau
import os

if os.name == "posix":
    canvas(width=950, height=1870)
else:
    canvas(width=1500, height=690)

widt = 16
dept = 16
a = 2

boxes = []
for i in range(widt):
    boxes += []
    for j in range(dept):
        v = vec(i-widt/2+0.5, 0, j-dept/2+0.5)*a
        boxes += [box(pos=v)]
