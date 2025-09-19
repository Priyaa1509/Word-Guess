import os
from datetime import date
from app import app, db, User, Word

def init_db():
    """
    Initializes and populates the database.

    This function performs the following steps:
    1. Establishes an application context required for all database operations.
    2. Creates all tables defined in the SQLAlchemy models (User and Word).
    3. Populates the database with a list of initial words if they don't already exist.
    4. Creates an admin user with a default or environment-specified username and password.
    """
    # Establishes the application context to work with Flask-SQLAlchemy.
    with app.app_context():
        # Creates all database tables according to the models (User and Word).
        db.create_all()
        print("Database tables created.")

        # Add initial 20 words if they don't exist
        initial_words = [
            "APPLE", "BAKER", "CRANE", "DREAM", "EAGLE",
            "FLAME", "GRAPE", "HOUSE", "IVORY", "JUMPY",
            "KNIFE", "LEMON", "MOUSE", "NIGHT", "OCEAN",
            "PLANT", "QUEEN", "RIVER", "SHARK", "TIGER"
        ]

        words_added_count = 0
        for word_text in initial_words:
            if not Word.query.filter_by(text=word_text).first():
                word = Word(text=word_text)
                db.session.add(word)
                words_added_count += 1
        
        db.session.commit()
        print(f"Added {words_added_count} new words to the database.")

        # Create an admin user if they don't already exist
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin').upper()
        admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')

        if not User.query.filter_by(username=admin_username).first():
            admin_user = User(username=admin_username, is_admin=True)
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            print(f"Created admin user: '{admin_username}' with password: '{admin_password}'")
        else:
            print(f"Admin user '{admin_username}' already exists.")

if __name__ == '__main__':
    # This block ensures the function is called only when the script is executed directly.
    init_db()
    print("Database initialization and population process complete.")
