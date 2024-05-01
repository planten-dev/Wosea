class Version:
    major: int
    minor: int
    patch: int

    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch

    def newer_than(self, other: "Version") -> bool:
        if self.major > other.major:
            return True
        if self.minor > other.minor:
            return True
        if self.patch > other.patch:
            return True
        return False


class Updater:
    @staticmethod
    def check_for_update() -> Version | None:
        # TODO:
        return None

    @staticmethod
    def update(version: Version) -> bool:
        # TODO
        return False
