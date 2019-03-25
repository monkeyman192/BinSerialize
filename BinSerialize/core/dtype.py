import struct


class dtype():
    endianess = '<'
    registered_funcs = dict()

    def __init__(self, endianess='<'):
        self.endianess = endianess
        self._value = None
        self._fmt = ''
        self.size = 0x0

# public methods

    def register(self, name, func):
        """ Register a new function to the dtype ecosystem.

        Parameters
        ----------
        name : str
            Name of the data type to be acessed at `dtype.name`
        func : class
            This must be a class that is a subclass of the `dtype` class.
            For proper functionality it needs to have the following methods:
            - `_deserialize(self, fobj)`:
                This method must assign the read data to `self.value`.
            - `_serialize(self, fobj, pointer_data)`:
                This method must write the data from `self.value` to fobj.
                `pointer_data` is a list which contains deferred data. If the
                custom data type has data referenced by pointers the actual
                data should be appended to this list in the form of a
                dictionary with the key being the location of the pointer, and
                the value being the instantiated datatype itself.
        """
        self.registered_funcs[name] = func()

    def deserialize(self, fobj):
        if hasattr(self, '_deserialize'):
            self._deserialize(fobj)
        else:
            self.value = struct.unpack(self.fmt, fobj.read(self.size))

    def serialize(self, fobj, pointer_data):
        if hasattr(self, '_serialize'):
            self._serialize(fobj, pointer_data)
        else:
            fobj.write(bytes(self))

    def set_value(self, value):
        self._value = value

# private methods

    def _set_value(self, value):
        if isinstance(self, type(value)):
            self._value = value
        else:
            self.set_value(value)

# properties

    @property
    def fmt(self):
        return self.endianess + self._fmt

    @fmt.setter
    def fmt(self, value):
        self._fmt = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._set_value(value)

# region class methods

    def __bytes__(self):
        return struct.pack(self.fmt, self.value)

    def __getattr__(self, name):
        if name in self.registered_funcs:
            return self.registered_funcs[name]
        raise AttributeError("Attribute '{0}' not found".format(name))
