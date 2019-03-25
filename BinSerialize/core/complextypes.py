import struct

from .dtype import dtype
from .stdtypes import _uint32
from .Pointer import Pointer
from .utils import instance_dtype


class _filesize(dtype, dict):
    def __init__(self, value_dtype=_uint32):
        dtype.__init__(self)
        int.__init__(self)
        self.value_dtype = instance_dtype(value_dtype)

        self.value = self

    def _deserialize(self, fobj):
        self['offset'] = fobj.tell()
        self.value_dtype.deserialize(fobj)
        self['data'] = self.value_dtype.value

    def _serialize(self, fobj, pointer_data):
        pointer_data.append(self)
        # write an empty header for now
        fobj.write(struct.pack(self.value_dtype.fmt, 0))


class _array(dtype, list):
    def __init__(self, array_dtype, length):
        dtype.__init__(self)
        list.__init__(self)
        self.array_dtype = instance_dtype(array_dtype)
        self.length = length

        self.value = self

    def _deserialize(self, fobj):
        for _ in range(self.length):
            self.array_dtype.deserialize(fobj)
            self.append(self.array_dtype.value)

    def _serialize(self, fobj, pointer_data):
        for val in self:
            fobj.write(struct.pack(self.array_dtype.fmt, val))


class _array_2d(dtype, list):
    def __init__(self, array_dtype, rows, columns):
        dtype.__init__(self)
        list.__init__(self)
        self.array_dtype = instance_dtype(array_dtype)
        self.rows = rows
        self.columns = columns

        self.value = self

    def _deserialize(self, fobj):
        for i in range(self.rows):
            self.append(list())
            for _ in range(self.columns):
                self.array_dtype.deserialize(fobj)
                self[i].append(self.array_dtype.value)

    def _serialize(self, fobj, pointer_data):
        for val in self:
            fobj.write(struct.pack(self.array_dtype.fmt, val))


class _list(dtype, list):
    def __init__(self, list_dtype, list_count_dtype=_uint32):
        dtype.__init__(self)
        list.__init__(self)
        self.list_dtype = instance_dtype(list_dtype)
        self.list_count_dtype = instance_dtype(list_count_dtype)

        self.value = self

    def _deserialize(self, fobj):
        count = struct.unpack(self.endianess + 'I', fobj.read(0x4))[0]
        for _ in range(count):
            self.list_dtype.deserialize(fobj)
            self.append(self.list_dtype.value)

    def _serialize(self, fobj, pointer_data):
        fobj.write(struct.pack(self.endianess + 'I', len(self.value)))
        for val in self.value:
            fobj.write(struct.pack(self.list_dtype.fmt, val))


class _pointer(dtype, dict):
    def __init__(self, data_dtype, offset_dtype=_uint32, offset_mode='abs'):
        dtype.__init__(self)
        dict.__init__(self)
        self.offset_dtype = instance_dtype(offset_dtype)
        self.data_dtype = instance_dtype(data_dtype)
        self.offset_mode = offset_mode

        self.value = self   # TODO: move into dtype.__init__?

    def _deserialize(self, fobj):
        self['offset'] = fobj.tell()
        with Pointer(fobj, self.offset_dtype, self.offset_mode):
            self.data_dtype.deserialize(fobj)
            if hasattr(self.data_dtype, 'value'):
                self['data'] = self.data_dtype.value
            else:
                self['data'] = self.data_dtype

    def _serialize(self, fobj, pointer_data):
        pointer_data.append(self)
        # write an empty header for now
        fobj.write(struct.pack(self.offset_dtype.fmt, 0))


class _switch(dtype):
    """ A data type to allow switching depending on a value that is read.

    Parameters
    ----------
    read_func : class
        A class which is a subclass of `dtype` which has a _deserialize method.
        This can be custom or a built-in.
    switch_data : dict
        Key: the value read by `read_func`
        Value: the data type to be used to read the subsequent data
    """
    def __init__(self, read_func, switch_data):
        dtype.__init__(self)
        self.type_read_func = instance_dtype(read_func)
        self.switch_data = dict(
            zip(switch_data.keys(),
                [instance_dtype(i) for i in switch_data.values()]))
        self.data_read_func = None

    def _deserialize(self, fobj):
        self.type_read_func.deserialize(fobj)
        switch_val = self.type_read_func.value
        if switch_val not in self.switch_data:
            raise TypeError(
                'Switch value {0} not found'.format(str(switch_val)))
        self.data_read_func = self.switch_data[switch_val]
        self.switch_data[switch_val].deserialize(fobj)
        self.value = self.data_read_func

    def _serialize(self, fobj, pointer_data):
        switch_val = None
        for key, value in self.switch_data.items():
            if value == self.value:
                switch_val = key
        if switch_val is None:
            raise TypeError(
                'Unknown data added. Please ensure the type has a'
                'corresponding key in the switch_data dictionary')
        self.type_read_func.value = switch_val
        self.type_read_func.serialize(fobj, pointer_data)
        self.value.serialize(fobj, pointer_data)


dtype.registered_funcs.update({'filesize': _filesize,
                               'array': _array,
                               'list': _list,
                               'pointer': _pointer,
                               'switch': _switch})
