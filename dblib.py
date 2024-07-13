import psycopg2

class sqlConnection:
    def __init__(self, connectionParameters: dict):
        self.connectionParameters = connectionParameters
        self.connection = None
        self.cursor = None

    def initiate(self):
        self.connection = psycopg2.connect(**self.connectionParameters)
        self.cursor = self.connection.cursor()

    def resultFromQuery(self, query: str) -> list:
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def close(self):
        self.cursor.close()
        self.connection.close()