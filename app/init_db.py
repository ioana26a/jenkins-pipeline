
import os
import time
import mysql.connector
from mysql.connector import Error

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
    """Inițializează baza de date cu tabelul și date de test."""
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
            print("✓ Tabel 'users' creat cu succes")
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
                print("✓ 5 rânduri de test inseriate cu succes")
            else:
                print(f"ℹ Baza de date conține deja {count} înregistrări")
            # Afișează înregistrările
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            print("\n📊 Înregistrări în baza de date:")
            print("-" * 80)
            for row in rows:
                print(
                    f"ID: {row[0]}, Nume: {row[1]}, Email: {row[2]}, "
                    f"Vârstă: {row[3]}, Oraș: {row[4]}"
                )
            print("-" * 80)
            connection.close()
            print("\n✓ Inițializare bază de date completă!")
        else:
            print("✗ Nu s-a putut conecta la baza de date")
    except Error as e:
        print(f"✗ Eroare la inițializare: {e}")


if __name__ == '__main__':
    print("Așteptare 10 secunde pentru pornirea MariaDB...")
    time.sleep(10)
    init_database()
