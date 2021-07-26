import re
from pathlib import Path
from typing import Iterator, Tuple

_STEM = "{stem} ({id})"
_PATTERN = re.compile(r"^(.+) \((\d+)\)$")


class UniquePathIterator:
    def __init__(self, path: Path = Path(),
                 stem_template: str = _STEM,
                 pattern: re.Pattern = _PATTERN,
                 default_id: int = 0,
                 start_from_given_path: bool = True) -> None:

        self.stem_template = stem_template
        self.pattern = pattern
        self.default_id = default_id
        self.start_from_given_path = start_from_given_path
        self.path = path

        self._id: int
        self._path: Path

    def _stem_with_id(self, id: int) -> str:
        if id == self.default_id:
            return self._path.stem

        return self.stem_template.format(
            stem=self._path.stem, id=id)

    def path_with_id(self, id: int) -> Path:
        return self._path.with_stem(self._stem_with_id(id))

    @property
    def path(self) -> Path:
        return self.path_with_id(self._id)

    @path.setter
    def path(self, path: Path) -> None:
        _, self._start_id = self._path, self._id = self.get_path_and_id(path)

        if self.start_from_given_path:
            self._id = self._start_id - 1

    @property
    def id(self):
        return self._id

    @property
    def start_id(self):
        return self._start_id

    def _id_from_match(self, match: re.Match) -> int:
        return int(match.group(2))

    def _path_from_match(self, match: re.Match) -> Path:
        return Path(match.group(1))

    def get_path_and_id(self, path: Path) -> Tuple[Path, int]:
        match = self.pattern.match(path.stem)

        id = self.default_id
        if match is not None:
            id = self._id_from_match(match)
            path = self._path_from_match(match)

        return path, id

    def __iter__(self) -> Iterator[Path]:
        return self

    def __next__(self) -> Path:
        self._id += 1

        return self.path

