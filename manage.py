#!/usr/bin/env python3

# PURPOSE
#
# Provides local machine access to do system-administrative actions:
#  - Use SQLAlchemy and alembic to perform git-controlled database migrations:
#        ./manage.py db <alembic-command>

import os

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app_init import app, db
import models

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
