import sqlite3
from api import DATABASE_PATH

def init_database(path):
    conn = sqlite3.connect(path)
    print("Opened database successfully")

    conn.execute('''CREATE TABLE classification_requests
                (id_request INTEGER PRIMARY KEY,
                request_timestamp TEXT NOT NULL,
                predicted_class INTEGER,
                response_status TEXT NOT NULL,
                error_message TEXT);''')

    conn.execute('''CREATE TABLE classification_request_params
            (id_request_param INTEGER PRIMARY KEY,
            id_request INTEGER,
            param_name TEXT NOT NULL,
            param_value TEXT NOT NULL,
            FOREIGN KEY(id_request) REFERENCES classification_requests(id_request))''')

    print("Tables created successfully")
    return


if __name__ == '__main__':
    init_database(DATABASE_PATH)
