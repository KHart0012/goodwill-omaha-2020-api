#!/usr/bin/env python3

from flask import jsonify, abort

from app_init import app, bcrypt
from environment import AZURE_ENVIRONMENT
from utility import parse_request, APIError
from models import User, JWTBlacklist

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
def api_customer_login():
    loyalty_id, password = parse_request("loyaltyID", "password")
    #XXX: User.find_and_authenticate is the wrong thing to use here !!!
    customer = User.find_and_authenticate(loyalty_id, password)
    if not customer:
        return APIError.customer_authentication_failure()

    return jsonify({
        "accessToken": customer.generate_access_token()
    })


@app.route("/customer/taxYears", methods=["GET"])
def api_customer_tax_years():
    access_token = parse_request("accessToken")
    print(access_token)
    if access_token != "ert2y76t":
        return APIError.bad_access_token()
    else:
        return jsonify({
            "taxYears" : [
                2017, 2018, 2019
            ]
        })

@app.route("/customer/history", methods=["GET"])
def api_customer_history():
    access_token = parse_request("accessToken")
    if access_token != "ert2y76t":
        return APIError.bad_access_token()
    else:
        return jsonify({
            "history": [
                {
                    "transactionID": 410992,
                    "date": "02-27-2020",
                    "taxYear": 2020,
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
                    "taxYear": 2020,
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

@app.route("/customer/transaction", methods=["POST"])
def api_customer_transaction():
    date, items, description = parse_request("date", "items", "description")
    # NEED LOGIC FOR ADDING INFORMATION TO THE DATABASE
    return jsonify({"transactionID": 410992})

# The folllowing below exist for backwards compatibility only
@app.route("/user/login", methods=["POST"])
def api_user_login(): return api_customer_login()
@app.route("/customer/taxYears", methods=["GET"])
def api_user_tax_years(): return api_customer_tax_years()
@app.route("/customer/history", methods=["GET"])
def api_user_history(): return api_customer_history()
@app.route("/customer/transaction", methods=["POST"])
def api_user_transaction(): return api_customer_transaction()


## /employee/... ###############################################################

@app.route("/employee/login", methods=["POST"])
def api_employee_login():
    employeeID, password = parse_request("employeeID", "password")
    if employeeID != "67416" or password != "hunter3":
        return APIError.employee_authentication_failure()

    return jsonify({
        "accessToken": "ert2y76t"
    })


# Used if you call ./application.py directly, unused on azure service
if __name__ == '__main__':
    app.run(debug=True)
