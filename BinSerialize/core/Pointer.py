class Pointer():
    """ Context Manager to handle reading data located somewhere from a pointer
    """
    def __init__(self, fobj, offset_dtype, offset_mode):
        self.fobj = fobj
        self.offset_dtype = offset_dtype
        self.offset_mode = offset_mode

    def __enter__(self):
        self.return_location = self.fobj.tell()
        self.offset_dtype.deserialize(self.fobj)
        offset = self.offset_dtype.value
        if self.offset_mode == 'abs':
            self.fobj.seek(offset)
        elif self.offset_mode == 'rel':
            self.fobj.seek(self.return_location)
            self.fobj.seek(offset, 1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fobj.seek(self.return_location + self.offset_dtype.size)