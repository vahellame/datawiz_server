from contextlib import closing
import psycopg2
from psycopg2 import Binary
from psycopg2.extras import RealDictCursor


def str_to_binary(s: str) -> Binary:
    return Binary(bytes(s, encoding='utf-8'))


def binary_to_str(m: memoryview) -> str:
    return m.tobytes().decode(encoding='utf-8')


def execute_sql(sql_query, connection_params):
    with closing(psycopg2.connect(cursor_factory=RealDictCursor,
                                  dbname=connection_params["dbname"],
                                  user=connection_params["user"],
                                  password=connection_params["password"],
                                  host=connection_params["host"],
                                  port=connection_params["port"],
                                  )) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(sql_query)
            try:
                records = cursor.fetchall()
                result = []
                for record in records:
                    result.append(dict(record))
                return result
            except psycopg2.ProgrammingError:
                pass
