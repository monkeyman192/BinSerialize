from collections import OrderedDict as Odict
import struct
import inspect

from .core import dtype
from .core.complextypes import _filesize


class BinSerialize():
    def __init__(self):
        self._structure = Odict()
        self._pointer_data = list()

    def serialize(self, fname):
        if isinstance(fname, str):
            with open(fname, 'wb') as fobj:
                for val in self._structure.values():
                    val.serialize(fobj, self._pointer_data)
                self._serialize_pointer_data(fobj)
        else:
            for val in self._structure.values():
                val.serialize(fname, self._pointer_data)
            self._serialize_pointer_data(fname)

    def _serialize_pointer_data(self, fobj):
        filesize_data = None
        for pointer_data in self._pointer_data:
            # If it is filesize data leave it until the end
            if isinstance(pointer_data, _filesize):
                filesize_data = pointer_data
                continue
            # get the location of the end of the file
            data_loc = fobj.tell()
            # serialize the data the pointer points to
            pointer_data.data_dtype.serialize(fobj, self._pointer_data)
            fobj.seek(pointer_data['offset'])
            if pointer_data.offset_mode == 'abs':
                offset = struct.pack(pointer_data.offset_dtype.fmt, data_loc)
            elif pointer_data.offset_mode == 'rel':
                offset = struct.pack(pointer_data.offset_dtype.fmt,
                                     data_loc - pointer_data['offset'])
            fobj.write(offset)
            fobj.seek(0, 2)
        if filesize_data is not None:
            # write the file size data
            # First, get the file size by going to the end of the stream and
            # getting the location
            fobj.seek(0, 2)
            size = fobj.tell()
            # Then write this size into the required location
            fobj.seek(filesize_data['offset'])
            fobj.write(struct.pack(filesize_data.value_dtype.fmt, size))

    def deserialize(self, fname):
        if isinstance(fname, str):
            with open(fname, 'rb') as fobj:
                for val in self._structure.values():
                    val.deserialize(fobj)
        else:
            for val in self._structure.values():
                val.deserialize(fname)

    def __bytes__(self):
        _bytes = b''
        for val in self._structure.values():
            _bytes += bytes(val)
        return _bytes

    def __setattr__(self, name, value):
        if inspect.isclass(value):
            # If the type is uninstantiated we instantiate it
            if issubclass(value, dtype):
                # add to the structure
                if name[0] == '_':
                    self._structure[name] = value()
                else:
                    raise NameError('Cannot add a typed attribute publically')
            # If it is already instantiated just pass directly
        elif isinstance(value, dtype):
            # add to the structure
            if name[0] == '_':
                self._structure[name] = value
            else:
                raise NameError('Cannot add a typed attribute publically')
        # always add to the instance dictionary too
        self.__dict__[name] = value
        # check to see if the value for the actual variable is being set
        priv_name = '_{0}'.format(name)
        if priv_name in self._structure:
            self._structure[priv_name]._value = value

    def __getattr__(self, name):
        priv_name = '_{0}'.format(name)
        if priv_name in self._structure:
            return self._structure['_{0}'.format(name)].value
        raise AttributeError("Attribute '{0}' not found".format(name))
