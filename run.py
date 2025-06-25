from app import create_app, db
from flask_migrate import upgrade

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # db.create_all()  # Optional: use Flask-Migrate for better migrations
        upgrade()        # Applies Alembic migrations
    app.run(debug=True)
    

# from app import create_app, db
# app = create_app()

# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)

