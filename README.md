# Goodwill Omaha 2020 API

Web-app Instance: https://goodwill-nw2020.herokuapp.com/
## Getting Started

This is an overview of the backend structure of the Goodwill of Omaha App.

## Interfaces

Our service will interface with the web client to access members’ previous
donations, and prepare end-of-year reports. It will also have an interface for
the mobile app for storing donation information. Both the web client and mobile
client will use the same interface but will use application-specific endpoints.

Reports:

Reports include daily/monthly reports for overall donation information,
high-level detailed reports on totals on each donation type, and specific
donations made that day.

Go to the [API Specification Document](specification.md)

## Security

Our service will be responsible for storing customer data. Thus it is important
that customer data is only made available to the authorized customer.
Additionally, user passwords will be stored using an industry-standard password
hash/salt library (bcrypt).

Host Service:

- Hosted by Heroku or a similar service. Our prototype will be hosted there.

## Architecture

- **Database:** SQL (by PostgreSQL)
- **Service Layer:** Python flask
- **Input/output format:** JSON

## Resources
- https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
- https://bitbucket.org/ecollins/passlib/wiki/Home
- https://flask.palletsprojects.com/en/1.1.x/api/
- PostgreSQL:
  - https://docs.microsoft.com/en-us/azure/app-service/containers/tutorial-python-postgresql-app#deploy-the-web-app-to-azure-app-service
  - https://realpython.com/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/
	- https://www.c-sharpcorner.com/article/python-with-postgressql-sqlalchemy-and-flask2/
	- https://docs.sqlalchemy.org/en/13/dialects/postgresql.html
- JSON Web Tokens:
  - https://realpython.com/token-based-authentication-with-flask/
