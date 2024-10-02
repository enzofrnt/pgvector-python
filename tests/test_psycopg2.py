import numpy as np
from pgvector.psycopg2 import register_vector, SparseVector
import psycopg2
from psycopg2.extras import DictCursor, RealDictCursor, NamedTupleCursor

conn = psycopg2.connect(dbname='pgvector_python_test')
conn.autocommit = True

cur = conn.cursor()
cur.execute('CREATE EXTENSION IF NOT EXISTS vector')
cur.execute('DROP TABLE IF EXISTS psycopg2_items')
cur.execute('CREATE TABLE psycopg2_items (id bigserial PRIMARY KEY, embedding vector(3), half_embedding halfvec(3), binary_embedding bit(3), sparse_embedding sparsevec(3))')

register_vector(cur, globally=False)


class TestPsycopg2:
    def setup_method(self, test_method):
        cur.execute('DELETE FROM psycopg2_items')

    def test_vector(self):
        embedding = np.array([1.5, 2, 3])
        cur.execute('INSERT INTO psycopg2_items (embedding) VALUES (%s), (NULL)', (embedding,))

        cur.execute('SELECT embedding FROM psycopg2_items ORDER BY id')
        res = cur.fetchall()
        assert np.array_equal(res[0][0], embedding)
        assert res[0][0].dtype == np.float32
        assert res[1][0] is None

    def test_halfvec(self):
        embedding = [1.5, 2, 3]
        cur.execute('INSERT INTO psycopg2_items (half_embedding) VALUES (%s), (NULL)', (embedding,))

        cur.execute('SELECT half_embedding FROM psycopg2_items ORDER BY id')
        res = cur.fetchall()
        assert res[0][0].to_list() == [1.5, 2, 3]
        assert res[1][0] is None

    def test_bit(self):
        embedding = '101'
        cur.execute('INSERT INTO psycopg2_items (binary_embedding) VALUES (%s), (NULL)', (embedding,))

        cur.execute('SELECT binary_embedding FROM psycopg2_items ORDER BY id')
        res = cur.fetchall()
        assert res[0][0] == '101'
        assert res[1][0] is None

    def test_sparsevec(self):
        embedding = SparseVector([1.5, 2, 3])
        cur.execute('INSERT INTO psycopg2_items (sparse_embedding) VALUES (%s), (NULL)', (embedding,))

        cur.execute('SELECT sparse_embedding FROM psycopg2_items ORDER BY id')
        res = cur.fetchall()
        assert res[0][0].to_list() == [1.5, 2, 3]
        assert res[1][0] is None

    def test_cursor_factory(self):
        for cursor_factory in [DictCursor, RealDictCursor, NamedTupleCursor]:
            conn = psycopg2.connect(dbname='pgvector_python_test')
            cur = conn.cursor(cursor_factory=cursor_factory)
            register_vector(cur, globally=False)
            conn.close()

    def test_cursor_factory_connection(self):
        for cursor_factory in [DictCursor, RealDictCursor, NamedTupleCursor]:
            conn = psycopg2.connect(dbname='pgvector_python_test', cursor_factory=cursor_factory)
            register_vector(conn, globally=False)
            conn.close()
