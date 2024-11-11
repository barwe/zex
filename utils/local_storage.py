from zex import fs, xlist, xio


class LocalStorage:

    def __init__(self, fp: str, fk=None) -> None:
        self.filepath = fp
        self.fk = fk
        self.data = []

    def _read(self):
        if fs.exists(self.filepath):
            self.data = xio.read_json(self.filepath)
        else:
            self.data = []

    def _write(self):
        xio.write_json(self.data, self.filepath)

    def add(self, item, index=-1):
        self._read()
        if not self.has(item[self.fk]):
            self.data.insert(index, item)
        self._write()

    def remove(self, val):
        self._read()
        index = xlist.index(self.data, lambda d: d[self.fk] == val)
        self.data.pop(index)
        self._write()

    def get(self, val):
        self._read()
        return xlist.get(self.data, lambda d: d[self.fk] == val)

    def has(self, val):
        self._read()
        index = xlist.index(self.data, lambda d: d[self.fk] == val)
        return index > -1
