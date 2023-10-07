from flask import Flask, render_template, request
import models
from models import User, List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.config["SECRET_KEY"] = "secret-key-goes-here"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
Session = sessionmaker(bind=engine)

db = SQLAlchemy(app)

# db.init_app(app)


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
    user = db.get_or_404(User, id)
    return render_template("profile.html", user=user)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
