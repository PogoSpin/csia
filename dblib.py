from psycopg2 import connect

class SqlConnection:
    counter = 0

    def __init__(self, connectionParameters: dict, logQueries: bool = False):
        self.connectionParameters = connectionParameters
        self.connection = None
        self.cursor = None

        self.logQueries = logQueries

    def initiate(self):
        self.connection = connect(**self.connectionParameters)
        self.cursor = self.connection.cursor()

    def resultFromQuery(self, query: str) -> list[tuple]:
        self.cursor.execute(query)
        if self.logQueries:
            print(SqlConnection.counter, query)
            SqlConnection.counter += 1
        
        return self.cursor.fetchall()

    def execQuery(self, query: str) -> None:
        self.cursor.execute(query)
        self.connection.commit()
        if self.logQueries:
            print(SqlConnection.counter, query)
            SqlConnection.counter += 1
    
    def close(self) -> None:
        self.cursor.close()
        self.connection.close()