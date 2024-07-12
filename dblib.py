import psycopg2

class sqlConnection:
    def __init__(self, connectionParameters):
        self.connectionParameters = connectionParameters
        self.connection = None
        self.cursor = None

    def initiate(self):
        try:
            self.connection = psycopg2.connect(**self.connectionParameters)
            self.cursor = self.connection.cursor()
            return None
        
        except Exception as e:
            return e

    def resultFromQuery(self, query) -> list:
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def close(self):
        self.cursor.close()
        self.connection.close()