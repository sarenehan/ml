"""
Notes:
Using the command line tool:
https://www.sqlite.org/cli.html
to enter: sqlite3 machine_learning.db
to close out: .exit

With python:
https://docs.python.org/3.5/library/sqlite3.html
"""


import sqlite3
import pandas


class DatabaseSession(object):

    def __init__(self, **kwargs):
        self.conn = sqlite3.connect('machine_learning.db')

    def upload_from_csv(self, filename, table_name):
        df = pandas.read_csv(filename)
        df.to_sql(table_name, self.conn, if_exists='append', index=False)

    def query(self, query_text, fetch=True):
        return self.conn.execute(query_text).fetchall()

    def get_column(self, table_name):
        return self.query('PRAGMA table_info({})'.format(table_name))

    def count_column(self, table_name, column_name):
        return self.query("""
            select {}, count(*) from {}
            group by {}
            order by count(*) desc""".format(
            column_name,
            table_name, column_name))


DBSession = DatabaseSession()


def get_conn():
    conn = sqlite3.connect('machine_learning.db')
    yield conn
    conn.close()
