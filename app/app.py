import os
import time
import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify
from flask_cors import CORS

FLASK_ENV = os.getenv('FLASK_ENV', 'development')

app = Flask(__name__)
CORS(app)

# Configurația bazei de date
db_config = {
    'host': os.environ.get('DB_HOST', 'mariadb-db'),
    'user': os.environ.get('DB_USER', 'appuser'),
    'password': os.environ.get('DB_PASSWORD', 'apppass'),
    'database': os.environ.get('DB_NAME', 'appdb'),
}


def get_db_connection():
    """Crează o conexiune la baza de date."""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Eroare la conectare la baza de date: {e}")
        return None


def init_database():
    """Inițializează baza de date cu date de test."""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            # Crează tabelul dacă nu există
            create_table_query = (
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100),
                    age INT,
                    city VARCHAR(100)
                )
                """
            )
            cursor.execute(create_table_query)
            # Verifică dacă tabelul are date
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            # Dacă nu are date, inserează date de test
            if count == 0:
                insert_query = (
                    """
        INSERT INTO users (name, email, age, city) VALUES
            ('Ion Popescu', 'ion.popescu@email.com', 28, 'București'),
            ('Maria Ionescu', 'maria.ionescu@email.com', 32, 'Cluj-Napoca'),
            ('Alexandru Mihai', 'alex.mihai@email.com', 25, 'Timișoara'),
            ('Ana Georgescu', 'ana.georgescu@email.com', 30, 'Brașov'),
            ('Vasile Stoian', 'vasile.stoian@email.com', 35, 'Iași')
                    """
                )
                cursor.execute(insert_query)
                connection.commit()
                print("Baza de date inițializată cu date de test")
            connection.close()
    except Error as e:
        print(f"Eroare la inițializare: {e}")


@app.route('/api/data', methods=['GET'])
def get_data():
    """API endpoint pentru a extrage date din baza de date."""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify(
                {'error': 'Nu se poate conecta la baza de date'}
                ), 500
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users LIMIT 10")
        data = cursor.fetchall()
        connection.close()
        return jsonify(data), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/data/<int:limit>', methods=['GET'])
def get_data_limit(limit):
    """API endpoint pentru a extrage un număr limitat de rânduri."""
    try:
        if limit > 1000 or limit < 1:
            limit = 10
        connection = get_db_connection()
        if not connection:
            return jsonify(
                {'error': 'Nu se poate conecta la baza de date'}
                ), 500
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM users LIMIT {limit}")
        data = cursor.fetchall()
        connection.close()
        return jsonify(data), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        connection = get_db_connection()
        if connection:
            connection.close()
            return jsonify(
                {'status': 'healthy', 'database': 'connected'}
                ), 200
        return jsonify(
            {'status': 'unhealthy', 'database': 'disconnected'}
            ), 500
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.route('/', methods=['GET'])
def home():
    """Endpoint principal."""
    if FLASK_ENV == 'prod':
        env_text = 'PRODUCTION ENVIRONMENT'
    else:
        env_text = 'DEVELOPMENT ENVIRONMENT'
    return jsonify({'message': (
        f'Flask API running on port 5000 - {env_text}'
    )}), 200


if __name__ == '__main__':
    print("Inițializare bază de date...")
    time.sleep(5)  # Așteptă ca MariaDB să se pornească
    init_database()
    print("Pornire Flask server pe port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
