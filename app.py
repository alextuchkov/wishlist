from flask import Flask, render_template, request
import models
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.config["SECRET_KEY"] = "secret-key-goes-here"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
Session = sessionmaker(bind=engine)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    """Regular user model"""

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
        return str(self.id)

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


class List(db.Model):
    """Lists connected to users, containing products"""

    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String, nullable=False)
    list_description = db.Column(db.String)
    list_category = db.Column(db.String)
    deadline = db.Column(db.Date)
    # list_items = db.Column(JSON)  # Assuming items will be stored as JSON

    def __repr__(self):
        return f"<List id={self.id}, list_name={self.list_name}, list_category={self.list_category}, deadline={self.deadline}>"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        generated_password_hash = generate_password_hash(request.form.get("password"))
        new_user = User(
            username=request.form.get("username"),
            email=request.form.get("email"),
            password_hash=generated_password_hash,
        )
        session = Session()
        session.add(new_user)
        session.commit()
        session.close()
    return render_template("auth.html")


# @app.route('/signin', methothd=["GET", "POST"])
# def signin():
#     if request.method == "POST":
#         email=request.form.get("email")
#         checkked_pass = check_password_hash(request.form.get("password"))
#     return render_template('auth.html')


# @app.route("/profile/")
# def profile():
#     return render_template("profile.html")


@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        new_list = List(
            list_name=request.form.get("list_name"),
            list_description=request.form.get("description"),
            list_category=request.form.get("category"),
            deadline=request.form.get("deadline"),
        )

        session = Session()
        session.add(new_list)
        session.commit()
        session.close()

    return render_template("create.html")


@app.route("/edit")
def edit():
    return render_template("edit.html")


@app.route("/list")
def list():
    return render_template("list.html")


@app.route("/user/<int:id>")
def user_detail(id):
    user = User.query.filter_by(id=id).first()

    return render_template("profile.html", user=user)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
