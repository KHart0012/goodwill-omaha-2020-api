# goodwill-omaha-2020-api

Low-level design documentation [read-only]: https://docs.google.com/document/d/1lKIXAziEQ0GgUAMVSliodO-DPPX9Yd0kJyRJi252qCo/edit?usp=sharing

Web-app Instance: http://goodwillomaha-nw2020.azurewebsites.net/
 
Resources:

- https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
- https://bitbucket.org/ecollins/passlib/wiki/Home
- https://flask.palletsprojects.com/en/1.1.x/api/


## Getting Started:

Brief:
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

## JSON structure:

### For the Web: 

{
“user”: {
    “Id”: int
    “Password”: string
},
“History”: [
{
    “Id”: int,
    “Date”: string,
    “TaxYear”: int,
    “Items”: [
{ 
        		“ItemType”: string,
“Unit”: string,
“Quantity”: int,
“Description”: string
        		}
]
}
}

### for the mobile

{
    “Id”: int,
    “Date”: string,
    “Items”: [
{ 
            “ItemType”: string,
		“Unit”: string,
	“Quantity”: int
        		}
]
     “Description”: string
}
