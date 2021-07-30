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

    @property
    def cycle(self) -> float:
        return 2 * pi * self.sin_scale  # 2π is the period of sin

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


@dataclass
class FramePath:
    path: Path


@dataclass
class Renderer:
    animator: Animator

    duration: float = 0.  # in seconds
    fps: int = 60

    save_dir: Path = Path("animation_frames")
    downloads: Path = Path.home() / "Downloads"

    frame_paths: List[FramePath] = field(init=False, default_factory=list)
    not_found_frame_paths: List[FramePath] = field(
        init=False, default_factory=list)

    path_waiter: PathWaiter = PathWaiter(interval=0.25, timeout=5.)

    def frame_name(self, iteration: Optional[int] = None) -> str:
        if iteration is None:
            iteration = self.animator._iteration
        return f"{self.animator.name}_{iteration}.png"

    @property
    def number_of_frames(self) -> int:
        return int(self.duration * self.fps)

    def set_number_of_frames_via_duration(self, number_of_frames: int) -> None:
        # adding 0.1 so that no inaccuracies make a mistake
        self.duration = (number_of_frames + 0.1) / self.fps

    def clear_frame_paths(self) -> None:
        self.frame_paths.clear()
        self.not_found_frame_paths.clear()

    def download_frame(self) -> Path:
        path = self.downloads / self.frame_name()
        path = unique_path(path)

        self.animator.scene.capture(path.name)
        return path

    def move_frame(self, path: Path) -> Tuple[bool, Path]:
        return run(self.move_frame_async(path))

    async def move_frame_async(self, path: Path) -> Tuple[bool, Path]:
        self.path_waiter.path = path
        if await self.path_waiter.wait():
            new_path = unique_path(self.save_dir / self.frame_name())
            path.rename(new_path)
            return True, new_path

        return False, path

    async def _advance_and_save(self) -> None:
        # using one class, we take advantage of the fact that
        # this is only one instance, whose fields we can change
        frame_path = FramePath(self.download_frame())
        self.frame_paths.append(frame_path)

        self.animator.next_frame()
        success, path = await self.move_frame_async(frame_path.path)
        if success:
            frame_path.path = path
        else:
            self.not_found_frame_paths.append(frame_path)

    def create_frames(self) -> None:
        return run(self.create_frames_async())

    async def create_frames_async(self) -> None:
        self.clear_frame_paths()

        if not self.save_dir.exists():
            self.save_dir.mkdir()

        for _ in range(self.number_of_frames):
            await self._advance_and_save()

    async def _move_and_handle_frame_async(self,
                                           frame_path: FramePath) -> None:
        success, path = await self.move_frame_async(frame_path.path)
        if success:
            frame_path.path = path
        else:
            raise FileNotFoundError(
                f"frame path '{path}' does not exist,"
                " although it should be downloaded")

    def build_animation(self, ext: str = ".avi", codec: str = "DIVX") -> None:
        return run(self.build_animation_async(ext=ext, codec=codec))

    async def build_animation_async(self, ext: str = ".avi",
                                    codec: str = "DIVX") -> None:
        tasks = (self._move_and_handle_frame_async(path)
                 for path in self.not_found_frame_paths)
        await gather(*tasks)

        out = cv.VideoWriter(
            self.animator.name + ext, cv.VideoWriter_fourcc(*codec),
            self.fps, self.animator._shape())

        try:
            for frame_path in self.frame_paths:
                out.write(cv.imread(str(frame_path.path)))
        finally:
            out.release()

    def remove_frames(self):
        for frame_path in self.frame_paths:
            try:
                frame_path.path.unlink(missing_ok=False)
            except FileNotFoundError:
                warnings.warn(f"{frame_path.path} does not exist"
                              " so it won't be deleted")

        self.clear_frame_paths()


if __name__ == "__main__":
    print("setting up")
    scene = vp.canvas(width=3840, height=2160)

    animator = Animator(scene=scene)
    animator.init()

    renderer = Renderer(
        scene=scene,
        duration=1.,  # in seconds
        # fps=60,
    )
    # full cycle for every second of rendering.duration
    total_time_change = animator.cycle * renderer.duration
    animator.time_step = total_time_change / renderer.number_of_frames

    # remove the last frame as it must be
    # a frame before repeating the animation
    renderer.set_number_of_frames_via_duration(
        renderer.number_of_frames - 1)

    print("creating frames")
    start = time()
    renderer.create_frames()
    print("create_frames run time:", time() - start)
    print("building animation")
    renderer.build_animation()
    print("removing frames")
    renderer.remove_frames()
    print("done")

