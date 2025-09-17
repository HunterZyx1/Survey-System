from app import create_app
from app.extensions import db
from app.api.models import User

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")
    
    # Check if admin user already exists
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        # Create admin user
        admin_user = User(username='admin', email='admin@example.com', is_admin=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists!")