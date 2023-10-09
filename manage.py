from flask_migrate import Migrate, MigrateCommand
from app import app, db

# Create the Migrate instance
migrate = Migrate(app, db)

# Add the Migrate command to the app
app.cli.add_command('db', MigrateCommand)

if __name__ == '__main__':
    app.run()