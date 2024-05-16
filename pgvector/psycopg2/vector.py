import numpy as np
from psycopg2.extensions import adapt, new_type, register_adapter, register_type
from ..utils import from_db, to_db


class VectorAdapter(object):
    def __init__(self, value):
        self._value = value

    def getquoted(self):
        return adapt(to_db(self._value)).getquoted()


def cast_vector(value, cur):
    return from_db(value)


def register_vector_info(oid):
    vector = new_type((oid,), 'VECTOR', cast_vector)
    register_type(vector)
    register_adapter(np.ndarray, VectorAdapter)
