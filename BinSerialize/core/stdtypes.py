from .dtype import dtype


class _bool(dtype):
    def __init__(self):
        dtype.__init__(self)
        self.fmt = '?'
        self.size = 0x1

    def _set_value(self, value):
        self._value = value[0]


class _int16(dtype):
    def __init__(self):
        dtype.__init__(self)
        self.fmt = 'h'
        self.size = 0x2

    def _set_value(self, value):
        self._value = value[0]


class _uint16(dtype):
    def __init__(self):
        dtype.__init__(self)
        self.fmt = 'H'
        self.size = 0x2

    def _set_value(self, value):
        self._value = value[0]


class _int32(dtype):
    def __init__(self):
        dtype.__init__(self)
        self.fmt = 'i'
        self.size = 0x4

    def _set_value(self, value):
        self._value = value[0]


class _uint32(dtype):
    def __init__(self):
        dtype.__init__(self)
        self.fmt = 'I'
        self.size = 0x4

    def _set_value(self, value):
        self._value = value[0]


class _int64(dtype):
    def __init__(self):
        dtype.__init__(self)
        self.fmt = 'q'
        self.size = 0x8

    def _set_value(self, value):
        self._value = value[0]


class _uint64(dtype):
    def __init__(self):
        dtype.__init__(self)
        self.fmt = 'Q'
        self.size = 0x8

    def _set_value(self, value):
        self._value = value[0]


class _float32(dtype):
    def __init__(self):
        dtype.__init__(self)
        self.fmt = 'f'
        self.size = 0x4

    def _set_value(self, value):
        self._value = value[0]


class _float64(dtype):
    def __init__(self):
        dtype.__init__(self)
        self.fmt = 'd'
        self.size = 0x8

    def _set_value(self, value):
        self._value = value[0]


dtype.registered_funcs.update({'bool': _bool,
                               'int16': _int16,
                               'uint16': _uint16,
                               'int32': _int32,
                               'uint32': _uint32,
                               'int64': _int64,
                               'uint64': _uint64,
                               'float32': _float32,
                               'float64': _float64})
