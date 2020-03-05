# Goodwill Omaha 2020 API

Low-level design documentation [read-only]: https://docs.google.com/document/d/1lKIXAziEQ0GgUAMVSliodO-DPPX9Yd0kJyRJi252qCo/edit?usp=sharing

Web-app Instance: http://goodwillomaha-nw2020.azurewebsites.net/

## Resources
- https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
- https://bitbucket.org/ecollins/passlib/wiki/Home
- https://flask.palletsprojects.com/en/1.1.x/api/
- PostgreSQL:
  - https://docs.microsoft.com/en-us/azure/app-service/containers/tutorial-python-postgresql-app#deploy-the-web-app-to-azure-app-service
  - https://realpython.com/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/
	- https://www.c-sharpcorner.com/article/python-with-postgressql-sqlalchemy-and-flask2/
	- https://docs.sqlalchemy.org/en/13/dialects/postgresql.html

## Getting Started

### Brief:
This is an overview of the backend structure of the Goodwill of Omaha App.

## Security
Our service will be responsible for storing customer data. Thus it is important that customer data is only made available to the authorized customer. Additionally, user passwords will be stored using an industry-standard password hash/salt library.
Host Service
Hosted by Heroku or a similar service. Our prototype will be hosted there.

## Architecture
Database: SQL (by PostgreSQL)
Service Layer: Python flask
Input/output format: JSON

## Interfaces
Our service will interface with the web client to access members’ previous donations, and prepare end-of-year reports. It will also have an interface for the mobile app for storing donation information. Both the web client and mobile client will use the same interface but will use application-specific endpoints. 
Reports
Reports include daily/monthly reports for overall donation information, high-level detailed reports on totals on each donation type, and specific donations made that day.

## JSON structure

### For the Web
    {
      "user": {
        "Id": int
        "Password": string
      },
      "History": [
      {
        "Id": int,
        "Date": string,
        "TaxYear": int,
        "Items": [
          {
            "ItemType": string,
            "Unit": string,
            "Quantity": int,
            "Description": string
          }
        ]
      }
    }

### For the Mobile
    {
      "Id": int,
      "Date": string,
      "Items": [
        {
          "ItemType": string,
          "Unit": string,
          "Quantity": int
        }
      ]
      "Description": string
    }

## Service API for Goodwill Omaha Customers

### User Login Request
Accepts a customer’s loyalty ID and password, and returns an access token that is required for all other API calls (so long as the loyalty ID and password are a valid pair).

cURL Examples

Sample successful request:

    curl -i -X POST "https://goodwillomaha-nw2020.azurewebsites.net/user/login" \
    --data "loyaltyID=67417&password=hunter2"

### Get User’s List of Tax Years
Returns the list of possible tax years the currently logged in user can select.

cURL Examples

Sample successful request:

    curl -i -X GET "https://goodwillomaha-nw2020.azurewebsites.net/user/taxYears?accessToken=ert2y76t"

## Service API for Goodwill Omaha employees

### Employee Login
cURL Examples

Sample successful request:

    curl -i -X POST "https://goodwillomaha-nw2020.azurewebsites.net/employee/login" \
    --data "employeeID=67416&password=hunter3"
