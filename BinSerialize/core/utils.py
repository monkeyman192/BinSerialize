from .dtype import dtype
import inspect


def instance_dtype(value):
    """ Return an instanced version of a child class of dtype. """
    if inspect.isclass(value):
        try:
            return value()
        except TypeError:
            raise TypeError('Data type with arguments must be specified '
                            'already instantiated.')
    elif isinstance(value, dtype):
        return value
    # if neither of these conditions are met then simply return the original
    # value
    return value
