from flask_migrate import Migrate
from app import app, db
from flask_script import Manager

# Create the Migrate instance
migrate = Migrate(app, db)

# Create the Manager instance
manager = Manager(app)

# Add the Migrate command to the manager
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
