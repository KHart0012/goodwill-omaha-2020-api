#!/usr/bin/env python3

from flask import Flask, jsonify, request, abort

AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"

app = Flask(__name__)

# Reads in the `request` object from flask, and grabs the requested parameters
# (`params`) from the request. It can accept HTTP form arguments (as in
# "arg1=foo&arg2=bar"), or top-level JSON object arguments.
#
# params: a list of parameter names to grab. The code assumes that all supplied
#         parametes are required.
# returns: a tuple of paramater values, having the same number of elements
#          as `params`.
# aborts with HTTP 415: if request contains neither JSON nor form data.
# aborts with HTTP 400: if a supplied parameter doesn't appear in the request.
def parse_request(*params):
    values = []
    requestArray = None
    if request.json:
        requestArray = request.json
    elif request.form:
        requestArray = request.form
    else:
        abort(415) # Unsupported Media Type

    for param in params:
        if not param in requestArray:
            abort(400) # Bad request (missing required argument)
        values.append(requestArray[param])

    return values

# Returns a flask response object for errors specified by the API. This consists
# of a JSON object describing the error.
#
# httpError: A numeric HTTP status code (Use 400-499 for errors because the
#            front end provided incorrect information, 500-599 for errors
#            because of some backend issue). For status code best practices,
#            refer to: https://www.codetinkerer.com/2015/12/04/choosing-an-http-status-code.html
# errorCode: A short, all-caps string that the front ends can use to
#            differentiate between different kinds of errors. Use values from
#            the API specification document.
# error: A human-readable explanation of the error. Make sure this message is
#        suitable for display to the end user.
#
# Use within an "@app.route(...) def" as follows:
#    return api_error(403, "FAILURE_REASON", "Human explanation...")
def api_error(httpError, errorCode, error):
    return (jsonify({"errorCode": errorCode, "error": error}), httpError)

@app.route("/", methods=["GET"])
def api_root():
    return jsonify({
        "application": "Goodwill of Omaha Backend API for Northwest Missouri "
            "State University Software Engineering Practice (2020 Spring)",
        "environment": "test",
        "specification": "https://docs.google.com/document/d/1lKIXAziEQ0GgUAMVSliodO-DPPX9Yd0kJyRJi252qCo"
    })

@app.route("/user/history", methods=["GET"])
def api_user_history():
    access_token = parse_request("accessToken")
    if access_token != "ert+y76t":
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
        return jsonify({"accessToken": "ert+y76t"})

@app.route("/employee/login", methods=["POST"])
def api_employee_login():
    employeeID, password = parse_request("employeeID", "password")

    if employeeID != "67416" or password != "hunter3":
        return api_error(403, AUTHENTICATION_FAILURE,
            "Loyalty ID or password is incorrect.")
    else:
        return jsonify({"accessToken": "ert+y76t"})


@app.route("/user/transaction", methods=["POST"])
def api_user_transaction():
    date, items, description = parse_request("date", "items", "description")
    # NEED LOGIC FOR ADDING INFORMATION TO THE DATABASE
    return jsonify({"transactionID": 410992})


@app.route("/user/taxYears", method=["GET"])
def api_user_tax_years():
    access_token = parse_request("access_token")
    if access_token != "ert+y76t":
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
