from psycopg2 import connect

class SqlConnection:
    def __init__(self, connectionParameters: dict):
        self.connectionParameters = connectionParameters
        self.connection = None
        self.cursor = None

    def initiate(self):
        self.connection = connect(**self.connectionParameters)
        self.cursor = self.connection.cursor()

    def resultFromQuery(self, query: str) -> list[tuple]:
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def execQuery(self, query: str) -> list[tuple]:
        self.cursor.execute(query)
        return self.connection.commit()
    
    def close(self):
        self.cursor.close()
        self.connection.close()