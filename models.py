from app import db

class User(db.Model):
    """Regular user model"""

    # __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # Add this line

    def __repr__(self):
        return "<User %r>" % self.username

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email as id"""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


class List(db.Model):
    """Lists connected to users, containing products"""

    __tablename__ = "lists"

    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String, nullable=False)
    list_description = db.Column(db.String)
    list_category = db.Column(db.String)
    deadline = db.Column(db.Date)
    # list_items = db.Column(JSON)  # Assuming items will be stored as JSON

    def __repr__(self):
        return f"<List id={self.id}, list_name={self.list_name}, list_category={self.list_category}, deadline={self.deadline}>"

