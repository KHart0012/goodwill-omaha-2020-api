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

        if UnitType.query.count() == 0:
            db.session.add(UnitType("Clothing"))
            db.session.add(UnitType("Furniture"))
            db.session.add(UnitType("Wares"))
            db.session.add(UnitType("Misc"))

        if ItemType.query.count() == 0:
            db.session.add(ItemType("Box"))
            db.session.add(ItemType("Bag"))
            db.session.add(ItemType("Each"))

        db.session.commit()
    except:
        db.session.rollback()
        raise


if __name__ == '__main__':
    manager.run()
