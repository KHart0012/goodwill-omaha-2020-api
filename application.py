#!/usr/bin/env python3

from datetime import date
from flask import jsonify, abort
from flask_cors import cross_origin

from app_init import app, bcrypt, db
from environment import AZURE_ENVIRONMENT
from utility import APIError, format_phone_number, request_access_token, parse_request
from models import User, Customer, Employee, Store, Transaction, TransactionLine, ItemType, UnitType

@app.route("/", methods=["GET"])
def api_root():
    return jsonify({
        "application": "Goodwill of Omaha Backend API for Northwest Missouri "
            "State University Software Engineering Practice (2020 Spring)",
        "environment": AZURE_ENVIRONMENT,
        "specification": "https://github.com/KHart0012/goodwill-omaha-2020-api/blob/master/specification.md"
    })

# Service API For Goodwill Omaha Customers #####################################

@app.route("/customer/login", methods=["POST"])
@cross_origin()
def api_customer_login():
    loyalty_id, password = parse_request("loyaltyID", "password")

    customer = Customer.find_and_authenticate(loyalty_id, password)
    if not customer:
        raise APIError.customer_authentication_failure()

    return jsonify({
        "accessToken": customer.generate_access_token()
    })

@app.route("/customer/info", methods=["GET"])
@cross_origin()
def api_customer_info():
    customer = User.from_authorization(request_access_token(), Customer)

    humanized_phone, uri_phone = format_phone_number(customer.phone)

    return jsonify({
        "loyaltyID": customer.loyalty_id,
        "firstName": customer.first_name,
        "lastName": customer.last_name,
        "address": {
            "line1": customer.address1,
            "line2": customer.address2,
            "city": customer.city,
            "state": customer.state,
            "zip": customer.zip_code
        },
        "email": customer.email,
        "phone": humanized_phone,
        "phoneURI": uri_phone
    })

@app.route("/customer/history", methods=["GET"])
@cross_origin()
def api_customer_history():
    customer = User.from_authorization(request_access_token(), Customer)

    return jsonify({
        "taxYears": [
            2017, 2018, 2019
        ]
    })

@app.route("/customer/history/year/<year>", methods=["GET"])
@cross_origin()
def api_customer_history_year(year):
    customer = User.from_authorization(request_access_token(), Customer)

    if (year == "2019"):
        return jsonify({
            "history": [
                {
                    "transactionID": 410992,
                    "date": "02-27-2019",
                    "taxYear": 2019,
                    "items": [
                        {
                            "itemType": "clothing",
                            "unit": "box",
                            "quantity": 1,
                            "description": "box of old clothes"
                        },
                        {
                            "itemType": "Random things",
                            "unit": "bags",
                            "quantity": 2,
                            "description": "bags of random things"
                        }
                    ]
                },
                {
                    "transactionID": 410993,
                    "date": "01-31-2019",
                    "taxYear": 2019,
                    "items": [
                        {
                            "itemType": "furniture",
                            "unit": "each",
                            "quantity": 1,
                            "description": "old coffee table"
                        }
                    ]
                }
            ]
        })
    else:
        return jsonify({
            "history": [
            ]
        })

# Service API For Goodwill Omaha Employees #####################################

@app.route("/employee/login", methods=["POST"])
@cross_origin()
def api_employee_login():
    employee_id, password = parse_request("employeeID", "password")

    employee = Employee.find_and_authenticate(employee_id, password)
    if not employee:
        raise APIError.employee_authentication_failure()

    return jsonify({
        "accessToken": employee.generate_access_token()
    })

@app.route("/customer/<loyalty_id>/info", methods=["GET"])
@cross_origin()
def api_customer_lookup_info(loyalty_id):
    employee = User.from_authorization(request_access_token(), Employee)

    customer = Customer.query.get(loyalty_id)

    humanized_phone, uri_phone = format_phone_number(customer.phone)

    return jsonify({
        "loyaltyID": customer.loyalty_id,
        "firstName": customer.first_name,
        "lastName": customer.last_name,
        "address": {
            "line1": customer.address1,
            "line2": customer.address2,
            "city": customer.city,
            "state": customer.state,
            "zip": customer.zip_code
        },
        "email": customer.email,
        "phone": humanized_phone,
        "phoneURI": uri_phone
    })

@app.route("/customer/by/<field_name>/<field_value>", methods=["GET"])
@cross_origin()
def api_customer_lookup_info_by(field_name, field_value):
    employee = User.from_authorization(request_access_token(), Employee)

    return jsonify([
        {
            "firstName": "TestFirstName1",
            "lastName": "TestLastName1",
            "address": {
                "line1": "Test street 1",
                "line2": "Test line 2",
                "city": "Test City",
                "state": "MO",
                "zip": "123456"
            },
            "email": "test.email1@test.com",
            "phone": "18005555555"
        },
        {
            "firstName": "TestFirstName2",
            "lastName": "TestLastName2",
            "address": {
                "line1": "Test street 1",
                "line2": "Test line 2",
                "city": "Test City",
                "state": "KS",
                "zip": "654321"
            },
            "email": "test.email2@test.com",
            "phone": "18005555556"
        }
    ])

@app.route("/customer/transaction", methods=["POST"])
@cross_origin()
def api_customer_transaction():
    employee = User.from_authorization(request_access_token(), Employee)

    loyalty_id, store_id, date_, items = parse_request("loyaltyID", "storeID", "date", "items")
    
    date_of_transaction = date.fromisoformat(date_)

    # HANDLE ERROR IF ITEMS IS EMPTY

    # Create Transaction
    transaction = Transaction(
        date_of_transaction,
        loyalty_id,
        store_id,
        date_of_transaction.year
    )

    db.session.add(transaction)
    db.session.commit()

    # Create transaction line for every item
    for item in items:
        # Grab lookup table ids
        item_type_id = ItemType.query.filter_by(item_type=item["itemType"]).first()
        unit_type_id = UnitType.query.filter_by(unit_type=item["unit"]).first()
        
        transaction_line = TransactionLine(
            item_type_id,
            unit_type_id,
            item["quantity"],
            item["description"],
            transaction.transaction_id
        )

        db.session.add(transaction_line)
        db.session.commit()

    # Return transaction id to signal success

    return jsonify({"transactionID": transaction.transaction_id})

## Error handling ##############################################################

@app.errorhandler(APIError)
def api_error_handler(e):
    return e.api_error_response()

# Used if you call ./application.py directly, unused on heroku service
if __name__ == '__main__':
    app.run(debug=True)
