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

@app.route("/user/history", methods=["GET"])
def api_user_history():
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


@app.route("/user/login", methods=["POST"])
def api_user_login():
    loyalty_id, password = parse_request("loyaltyID", "password")

    #XXX: user_id is not the same thing as loyalty_id, this is temporary!!!
    user = User.query.filter_by(user_id = loyalty_id).first()
    if user and bcrypt.check_password_hash(user.password, password):
        auth_token = user.encode_auth_token(user.user_id)
        return jsonify({"accessToken": auth_token.decode()})
    else:
        return APIError.customer_authentication_failure()

@app.route("/employee/login", methods=["POST"])
def api_employee_login():
    employeeID, password = parse_request("employeeID", "password")

    if employeeID != "67416" or password != "hunter3":
        return APIError.employee_authentication_failure()
    else:
        return jsonify({"accessToken": "ert2y76t"})


@app.route("/user/transaction", methods=["POST"])
def api_user_transaction():
    date, items, description = parse_request("date", "items", "description")
    # NEED LOGIC FOR ADDING INFORMATION TO THE DATABASE
    return jsonify({"transactionID": 410992})


@app.route("/user/taxYears", methods=["GET"])
def api_user_tax_years():
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


if __name__ == '__main__':
    app.run(debug=True)
