from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_login import LoginManager
from models import Base  # Import the Base from models

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret-key-goes-here"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:////Users/oleksandrtuchkov/Documents/Code/wishlist/db.sqlite"
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
Session = sessionmaker(bind=engine)
session = Session()

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

# Create tables
Base.metadata.create_all(engine)

if __name__ == "__main__":
    from views import *

    app.run(debug=True)
