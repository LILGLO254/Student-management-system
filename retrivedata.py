from database import create_connection
from werkzeug.security import generate_password_hash


users = [
    ("gloria","gloriaanyango825@gmail.com","gloria778","student"),
    ("Admin","roseakinyi@gmail.com","admin123","admin")
]


def seed_users():
    connection = create_connection()
    if connection is None:
        raise RuntimeError("Could not connect to the student management database.")

    inserted = 0
    
    try:
        cursor = connection.cursor()
        for username, email, password, role in users:
            cursor.execute(
                "INSERT IGNORE INTO users (username, email, password, role) "
                "VALUES (%s, %s, %s, %s)",
                (username, email, generate_password_hash(password), role),
            )
            inserted += cursor.rowcount
        connection.commit()
        cursor.close()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    print(f"Inserted {inserted} user(s); existing users were left unchanged.")


if __name__ == "__main__":
    seed_users()