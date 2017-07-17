import os

class Path:
    def __init__(self, path):
        self._path = path

    def set(self):
        if not os.path.isdir(self._path):
            try:
                os.makedirs(self._path)
            except:
                return False
        return True