# About
Simple and lightweight web application where you can create wishlists and share them with you friends.

# How to install
'''bash
pip install Flask
pip install Flask-Login
pip install Flask-Migrate
pip install SQLAlchemy
pip install werkzeug
'''


# Migrations
If you want to run migrations, you'll need to use:
'''
flask db migrate -m "message"
flask db upgrade
'''