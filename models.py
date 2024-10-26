from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(120), nullable=False, default='default.jpg')
    
    # Add created_at field
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    
    posts = db.relationship("Post", backref="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"
    
    @property
    def full_name(self):
        """Return full name of the user."""
        return f"{self.first_name} {self.last_name}"
    
    

class Post(db.Model):
    """Blog post."""
    
    __tablename__ = "post"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
def connect_db(app):
    db.app = app
    db.init_app(app)