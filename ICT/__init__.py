from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
import os
from .filters import init_filters

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    init_filters(app)  

    upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'profile_pics')
    os.makedirs(upload_dir, exist_ok=True)

    from ICT.routes import main
    app.register_blueprint(main)

    from ICT.models import User

    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@forum.com').first()
        if not admin:
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(
                username='admin',
                email='admin@forum.com',
                password=hashed_password,
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

    return app

# Context processor for all templates
@login_manager.user_loader
def load_user(user_id):
    from ICT.models import User  # Import here to avoid circular imports
    return User.query.get(int(user_id))