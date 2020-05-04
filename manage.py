#!/usr/bin/env python3

# PURPOSE
#
# Provides local machine access to do system-administrative actions:
#  - Use SQLAlchemy and alembic to perform git-controlled database migrations:
#        python manage.py db revision --autogenerate -m "An explanatory message"
#        python manage.py db upgrade
#  - Seed the database:
#        python manage.py seed_db
#
# HOW TO USE
#
# If you need to make a change to a model, generate an upgrade script with the
# "db revision" command above, then modify/commit the resulting script in
# /migrations/
#
# As part of the deploy process, you should run the "db upgrade" command above,
# then the "seed_db" command above. These two commands are automatically called
# in the heroku deploy because they are referenced in ./Procfile

import os

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app_init import app, db
from models import User, Customer, Employee, Store, UnitType, ItemType

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def seed_db():
    try:
        # Obviously get rid of these before moving to production
        if User.query.count() == 0:
                db.session.add(Customer(67417, "hunter2", "Test", "Customer"))
                db.session.add(Employee(67416, "hunter3", "Test", "User"))

        test_customer = Customer.query.filter_by(loyalty_id=67417).first()
        if not test_customer.phone or test_customer.phone == "+1-111-555-1212":
            test_customer.phone = "+12128675309"
        if not test_customer.email:
            test_customer.email = "testemail@example.com"
        if not test_customer.address1:
            test_customer.address1 = "321 Anywhere St"
            test_customer.address2 = ""
            test_customer.city = "Columbus"
            test_customer.state = "NC"
            test_customer.zip_code = "12343"

        if Store.query.count() == 0:
            db.session.add(Store("Goodwill Omaha Headquarters"))

        if ItemType.query.count() == 0:
            db.session.add(ItemType("Clothing"))
            db.session.add(ItemType("Furniture"))
            db.session.add(ItemType("Wares"))
            db.session.add(ItemType("Misc"))

        if UnitType.query.count() == 0:
            db.session.add(UnitType("Box"))
            db.session.add(UnitType("Bag"))
            db.session.add(UnitType("Each"))

        db.session.commit()
    except:
        db.session.rollback()
        raise


if __name__ == '__main__':
    manager.run()
