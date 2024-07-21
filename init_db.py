from park import create_app, db

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()