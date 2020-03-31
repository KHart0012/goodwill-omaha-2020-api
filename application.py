#!/usr/bin/env python3

from flask import jsonify, abort
from flask_cors import cross_origin

from app_init import app, bcrypt
from environment import AZURE_ENVIRONMENT
from utility import parse_request, request_access_token, APIError
from models import User, Customer, Employee

@app.route("/", methods=["GET"])
def api_root():
    return jsonify({
        "application": "Goodwill of Omaha Backend API for Northwest Missouri "
            "State University Software Engineering Practice (2020 Spring)",
        "environment": AZURE_ENVIRONMENT,
        "specification": "https://docs.google.com/document/d/1lKIXAziEQ0GgUAMVSliodO-DPPX9Yd0kJyRJi252qCo"
    })

# /customer/... ################################################################

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


@app.route("/customer/history", methods=["GET"])
@cross_origin()
def api_customer_tax_years():
    customer = User.from_authorization(request_access_token())
    print(customer)

    return jsonify({
        "taxYears": [
            2017, 2018, 2019
        ]
    })

@app.route("/customer/history/year/<year>", methods=["GET"])
@cross_origin()
def api_customer_history(year):
    customer = User.from_authorization(request_access_token())

    if (year == "2019"):
        return jsonify({
            "history": [
                {
                    "transactionID": 410992,
                    "date": "02-27-2020",
                    "taxYear": 2019,
                    "items": [
                        {
                            "itemType": "clothing",
                            "unit": "box",
                            "quantity": 1,
                            "description": "box of old clothes"
                        }
                    ]
                },
                {
                    "transactionID": 410993,
                    "date": "01-31-2020",
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

@app.route("/customer/info", methods=["GET"])
@cross_origin()
def api_customer_info():
    employee = User.from_authorization(request_access_token())
    loyaltyID = parse_request("loyaltyID")

    return jsonify([
        {
            "firstName": "Hank",
            "lastName": "Hill",
            "Address": {
                "line1": "Test street 1",
                "line2": "Test line 2",
                "city": "Test City",
                "state": "Missouri",
                "zip": "123456"
            },
            "email": "test.email@downloadramhere.com",
            "phone": "18005555555"
        },
        {
            "firstName": "Deborah",
            "lastName": "Hill",
            "Address": {
                "line1": "Test street 1",
                "line2": "Test line 2",
                "city": "Test City",
                "state": "Missouri",
                "zip": "123456"
            },
            "email": "test.email2@downloadramhere.com",
            "phone": "18165555555"
        }
    ])

@app.route("/customer/transaction", methods=["POST"])
@cross_origin()
def api_customer_transaction():
    customer = User.from_authorization(request_access_token())

    date, items, description = parse_request("date", "items", "description")
    # NEED LOGIC FOR ADDING INFORMATION TO THE DATABASE
    return jsonify({"transactionID": 410992})

## /employee/... ###############################################################

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

## Error handling ##############################################################

@app.errorhandler(APIError)
def api_error_handler(e):
    return e.api_error_response()

# Used if you call ./application.py directly, unused on azure service
if __name__ == '__main__':
    app.run(debug=True)
