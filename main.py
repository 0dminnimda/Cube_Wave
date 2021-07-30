import warnings
from asyncio import gather, run
from dataclasses import dataclass, field
from math import pi, sin
from pathlib import Path
from time import sleep, time
from typing import Iterable, Iterator, List, Optional, Tuple

import cv2 as cv
import numpy as np
import vpython as vp
from vpython import vec

from async_waiters import PathWaiter
from unique_paths import unique_path


@dataclass
class Animator:
    scene: vp.canvas = vp.canvas()

    width: int = 16
    depth: int = 16

    scale: float = 1.
    min_height: float = 0.5
    sin_scale: float = 30.
    height_multiplier: float = 6.

    boxes: List[List[vp.box]] = field(init=False, default_factory=list)
    box_size: vec = vec(1, 1, 1) / 1.1  # division for the gap between boxes

    time: float = field(default=0., init=False)
    time_step: float = -0.225
    rate: Optional[float] = None
    _iteration: int = field(default=0, init=False)

    name: str = "cube_wave_animation"
    wait_for_rendering_at_every_step: bool = True

    def _shape(self):
        return self.scene.width, self.scene.height

    def init(self) -> None:
        self.scene.select()
        self.scene.title = self.name

        centering_shift = (
            # center of the shape to the origin
            - vec(self.width, 0, self.depth) / 2

            + vec(1, 0, 1) / 2)  # shift to the exact center

        self.box_size /= self.scale

        self.boxes = np.array(
            [[vp.box() for _ in range(self.depth)] for _ in range(self.width)],
            dtype=type(vp.box))

        for (i, j), box in np.ndenumerate(self.boxes):
            box.size = self.box_size
            box.pos = (vec(i, 1.5, j) + centering_shift) / self.scale
            box.rotate(pi*0.25, axis=vec(0, 1, 0), origin=vec(0, 0, 0))
            box.rotate(pi*0.2, axis=vec(1, 0, 0), origin=vec(0, 0, 0))

        self.scene.range = 16

    def next_frame(self) -> None:
        self._iteration += 1
        if self.rate is not None:
            vp.rate(self.rate)

        for line_of_boxes in self.boxes:
            for box in line_of_boxes:
                ang = (box.pos.mag**2 + self.time) / self.sin_scale
                box.height = (
                    1 + sin(ang)  # from 0 to 2
                    + self.min_height
                ) * self.height_multiplier / self.scale

        self.time += self.time_step

        if self.wait_for_rendering_at_every_step:
            self.scene.waitfor("draw_complete")

