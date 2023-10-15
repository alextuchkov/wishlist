from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    authenticated = Column(Boolean, default=False)
    active = Column(Boolean, default=False)
    about_me = Column(String(256))

    def __repr__(self):
        return f"<User {self.username}>"

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return self.authenticated

    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)

    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)


class List(Base):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(256))
    deadline = Column(Date)
    owner = Column(Integer, ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<List id={self.id}, name={self.name}, description={self.description}, deadline={self.deadline}>"
