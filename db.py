import mysql.connector

def get_db_connection():
    print("Connecting to the database...")
    try:
        conn = mysql.connector.connect(
            host="localhost",        
            user="root",             
            password="root",
            database="aula_virtual",
            port=3306,
        )
        print("Connection established.")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")

if __name__ == "__main__":
    connection = get_db_connection()
    print("Connection object:", connection)
