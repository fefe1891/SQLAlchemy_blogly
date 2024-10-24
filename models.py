from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(120), nullable=False, default='default.jpg')
    
    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"
    
    @property
    def full_name(self):
        """Return full name of the user."""
        return f"{self.first_name} {self.last_name}"
    
    
def connect_db(app):
    db.app = app
    db.init_app(app)