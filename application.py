#!/usr/bin/env python3

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from environment import DB_URI, AZURE_ENVIRONMENT
from utility import parse_request, api_error
import models

AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# All API routes follow
################################################################################

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
        return api_error(403, AUTHENTICATION_FAILURE,
            "Loyalty ID or password is incorrect.")
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
    loyaltyID, password = parse_request("loyaltyID", "password")

    if loyaltyID != "67417" or password != "hunter2":
        return api_error(403, AUTHENTICATION_FAILURE,
            "Loyalty ID or password is incorrect.")
    else:
        return jsonify({"accessToken": "ert2y76t"})

@app.route("/employee/login", methods=["POST"])
def api_employee_login():
    employeeID, password = parse_request("employeeID", "password")

    if employeeID != "67416" or password != "hunter3":
        return api_error(403, AUTHENTICATION_FAILURE,
            "Loyalty ID or password is incorrect.")
    else:
        return jsonify({"accessToken": "ert2y76t"})


@app.route("/user/transaction", methods=["POST"])
def api_user_transaction():
    date, items, description = parse_request("date", "items", "description")
    # NEED LOGIC FOR ADDING INFORMATION TO THE DATABASE
    return jsonify({"transactionID": 410992})


@app.route("/user/taxYears", methods=["GET"])
def api_user_tax_years():
    access_token = parse_request("accessToken")[0]
    print(access_token)
    if access_token != "ert2y76t":
        return api_error(403, AUTHENTICATION_FAILURE, 
            "Loyalty ID or password is incorrect.")
    else:
        return jsonify({
            "taxYears" : [
                2017, 2018, 2019
            ]
        })


if __name__ == '__main__':
    app.run(debug=True)
