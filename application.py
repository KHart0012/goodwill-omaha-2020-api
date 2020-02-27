#!/usr/bin/env python3

from flask import Flask, jsonify, request, abort

app = Flask(__name__)

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

def api_error(errorCode, error):
    return jsonify({"errorCode": errorCode, "error": error})

@app.route("/", methods=["GET"])
def api_root():
    return jsonify({
        "application": "Goodwill of Omaha Backend API for Northwest Missouri "
            "State University Software Engineering Practice (2020 Spring)",
        "environment": "test",
        "specification": "https://docs.google.com/document/d/1lKIXAziEQ0GgUAMVSliodO-DPPX9Yd0kJyRJi252qCo"
    })

@app.route("/user/login", methods=["POST"])
def api_user_login():
    loyaltyID, password = parse_request("loyaltyID", "password")

    if loyaltyID != "67417" or password != "hunter2":
        return api_error("AUTHENTICATION_FAILURE",
            "Loyalty ID or password is incorrect.")
    else:
        return jsonify({"accessToken": "ert+y76t"})

@app.route("/employee/login", methods=["POST"])
def api_employee_login():
    employeeID, password = parse_request("employeeID", "password")

    if employeeID != "67416" or password != "hunter3":
        return api_error("AUTHENTICATION_FAILURE",
            "Loyalty ID or password is incorrect.")
    else:
        return jsonify({"accessToken": "ert+y76t"})


if __name__ == '__main__':
    app.run(debug=True)
