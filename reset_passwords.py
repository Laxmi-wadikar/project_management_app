from app import db
from app.models import User
from werkzeug.security import generate_password_hash

users_data = {
    "alice": "alice123",
    "bob": "bob123",
    "carol": "carol123",
    "dave": "dave123",
    "eve": "eve123",
    "frank": "frank123",
    "grace": "grace123",
    "heidi": "heidi123",
    "ivan": "ivan123",
    "judy": "judy123",
    "mallory": "mallory123",
    "oscar": "oscar123",
    "peggy": "peggy123",
    "trent": "trent123",
    "victor": "victor123",
    "walter": "walter123",
    "xena": "xena123",
    "yvonne": "yvonne123",
    "zach": "zach123",
    "zoe": "zoe123"
}

for username, password in users_data.items():
    user = User(
        username=username,
        password=generate_password_hash(password),
        role='employee',
        email=f'{username}@example.com',
        department='General'
    )
    db.session.add(user)

db.session.commit()
print("✅ All users created with hashed passwords.")
