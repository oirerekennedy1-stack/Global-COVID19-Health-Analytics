import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="dev_user",
        password="DevPassword123!",
        database="sandbox_db"
    )
    if connection.is_connected():
        cursor = connection.cursor()
        query = "SELECT test_name, AVG(numerical_value) FROM lab_results GROUP BY test_name;"
        cursor.execute(query)
        records = cursor.fetchall()
        
        print("\n=== HOSPITAL CLINICAL METRICS (PYTHON) ===")
        for row in records:
            print(f"Test: {row[0]} | Average: {row[1]:.2f}")
            
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
