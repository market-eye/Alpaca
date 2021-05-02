import psycopg2
from psycopg2 import Error

class PostgresDB():
    def __init__(self, db, user, pwd, host, port):
        self.conn = psycopg2.connect(database=db, user=user, password=pwd, host=host, port=port)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def execute(self, statement):
        try:
            self.cur.execute(statement)
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL:", error)

    def fetch(self, statement):
        try:
            self.cur.execute(statement)
            rows = self.cur.fetchall()
            for row in rows:
                print(row)
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL:", error)

    def close(self):
        self.cur.close()
        self.conn.close()
