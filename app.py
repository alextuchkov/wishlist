from flask import Flask, render_template, request, flash, url_for, redirect
import models
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user,
)
from datetime import datetime


app = Flask(__name__)


app.config["SECRET_KEY"] = "secret-key-goes-here"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:////Users/oleksandrtuchkov/Documents/Code/wishlist/db.sqlite"
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
Session = sessionmaker(bind=engine)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
session = Session()

login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model):
    """Regular user model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=False)
    about_me = db.Column(db.String(256))

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


class List(db.Model):
    """Lists connected to users, containing products"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(256))
    deadline = db.Column(db.Date)
    owner = db.Column(
        db.Integer, db.ForeignKey("user.id", name="list_owner"), nullable=False
    )

    def __repr__(self):
        return f"<List id={self.id}, list_name={self.list_name}, list_category={self.list_category}, deadline={self.deadline}>"


@app.route("/")
def index():
    return render_template("index.html")


@login_manager.user_loader
def user_loader(user_id):
    # return User.query.get(user_id)
    with app.app_context():
        return db.session.get(User, user_id)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        generated_password_hash = generate_password_hash(request.form.get("password"))
        new_user = User(
            username=request.form.get("username"),
            email=request.form.get("email"),
            password_hash=generated_password_hash,
            active=True,
        )
        session.add(new_user)
        session.commit()
        session.close()
        return redirect(url_for("signin"))
    return render_template("auth.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if a valid user with the provided email exists
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            user.authenticated = True
            db.session.commit()  # Commit the change to the user
            login_user(user, remember=True)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid login credentials", "error")

    # Render the login template for both GET and unsuccessful POST requests
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        deadline_date = datetime.strptime(
            request.form.get("deadline"), "%Y-%m-%d"
        ).date()

        new_list = List(
            name=request.form.get("list_name"),
            description=request.form.get("description"),
            deadline=deadline_date,
            owner=current_user.id,
        )

        session.add(new_list)
        session.commit()
        session.close()

    return render_template("create.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    list_item = session.query(List).filter_by(id=id).first()

    if request.method == "POST":
        deadline_date = datetime.strptime(
            request.form.get("deadline"), "%Y-%m-%d"
        ).date()

        list_item.name = request.form.get("name")
        list_item.description = request.form.get("description")
        list_item.deadline = deadline_date

        try:
            session.commit()
            flash("List details updated successfully.", "success")
        except Exception as e:
            session.rollback()
            flash(f"An error occurred while updating list details: {str(e)}", "error")

        return redirect(url_for("edit", id=list_item.id))  # Corrected redirect

    return render_template("edit.html", list=list_item)


@app.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete(id):
    list_item = session.query(List).filter_by(id=id).first()
    if list_item:
        try:
            session.delete(list_item)
            session.commit()
            flash("List item deleted successfully.", "success")
        except Exception as e:
            session.rollback()
            flash(f"An error occurred while deleting the list item: {str(e)}", "error")
    else:
        flash("List item not found.", "error")

    return redirect(
        url_for("dashboard")
    )  # Redirect to the dashboard or another appropriate page


@app.route("/list/<int:id>")
def list(id):
    list_item = session.query(List).filter_by(id=id).first()
    return render_template("list.html", list=list_item)


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """Opens dashboard page for logged in user"""
    lists = session.query(List).filter_by(owner=current_user.id).all()
    if request.method == "POST":
        user = session.query(User).filter_by(id=current_user.id).first()
        if user:
            user.username = request.form.get("username")
            user.email = request.form.get("email")
            user.about_me = request.form.get("about-me")

            try:
                session.commit()
                flash("User details updated successfully.", "success")
            except Exception as e:
                session.rollback()
                flash(
                    f"An error occurred while updating user details: {str(e)}", "error"
                )
        else:
            flash("User not found.", "error")

        return redirect(url_for("dashboard"))

    return render_template("dashboard.html", lists=lists)


@app.route("/profile/<int:id>")
def profile(id):
    user = User.query.filter_by(id=id).first()
    lists = session.query(List).filter_by(owner=user.id).all()
    return render_template("profile.html", user=user, lists=lists)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
