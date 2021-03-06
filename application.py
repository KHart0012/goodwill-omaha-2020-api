#!/usr/bin/env python3

from datetime import date
from backports.datetime_fromisoformat import MonkeyPatch
MonkeyPatch.patch_fromisoformat()
from flask import jsonify
from flask_cors import cross_origin

from app_init import app, bcrypt, db
from environment import ENVIRONMENT
from utility import APIError, format_phone_number, normalize_phone_number, request_access_token, parse_request
from models import User, Customer, Employee, Store, Transaction, TransactionLine, ItemType, UnitType

# See also: "specification.md" for details concerning each endpoint

# An endpoint not in specification meant to be for informational use only.
# Neither the web nor mobile frontends depend on this value.
@app.route("/", methods=["GET"])
def api_root():
    return jsonify({
        "application": "Goodwill Omaha Backend API for Northwest Missouri "
            "State University Software Engineering Practice (2020 Spring)",
        "environment": ENVIRONMENT,
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
    transactions = Transaction.query.filter_by(loyalty_id=customer.loyalty_id)

    tax_years = map(lambda x : x.tax_year, transactions)
    return jsonify({
        "taxYears": list(set(tax_years))
    })

@app.route("/customer/history/year/<year>", methods=["GET"])
@cross_origin()
def api_customer_history_year(year):
    customer = User.from_authorization(request_access_token(), Customer)
    transactions = Transaction.query.filter_by(loyalty_id=customer.loyalty_id)

    history = []
    for transaction in transactions:
        if transaction.tax_year == int(year):
            transaction_lines = TransactionLine.query.filter_by(transaction_id=transaction.transaction_id)
            items = []
            for transaction_line in transaction_lines:
                items.append({
                    "itemType": ItemType.query.get(transaction_line.item_type_id).item_type,
                    "unit": UnitType.query.get(transaction_line.unit_type_id).unit_type,
                    "quantity": transaction_line.quantity,
                    "description": transaction_line.description
                })

            history.append({
                "transactionID": transaction.transaction_id,
                "date": str(transaction.date.date()),
                "taxYear": year,
                "items": items
            })

    return jsonify({
        "history": history
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
    # Authenticates the employee to access Database
    employee = User.from_authorization(request_access_token(), Employee)

    # Queries Database to find customer with entered loyalty_id
    customer = Customer.query.filter_by(loyalty_id=loyalty_id).first()

    # If no customer is found, raise a 404 error
    if customer is None:
        raise APIError(404, "NOT_FOUND", "Loyalty ID Not Found")

    # Generated easily readable phone number and phone URI
    humanized_phone, uri_phone = format_phone_number(customer.phone)

    # Return information of the customer that was matched with the loyalty_id
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
    # Authenticates the employee to access Database
    employee = User.from_authorization(request_access_token(), Employee)

    # Checks what field_name was passed in, and based on that, queries the database
    # for and returns all results with the matching field_value
    # If the field name does not match an accepted field name, raises 400 error
    if field_name.lower() == 'firstname':
        customers = Customer.query.filter(db.func.lower(Customer.first_name) == field_value.lower()).all()
    elif field_name.lower() == 'lastname':
        customers = Customer.query.filter(db.func.lower(Customer.last_name) == field_value.lower()).all()
    elif field_name.lower() == 'email':
        customers = Customer.query.filter(db.func.lower(Customer.email) == field_value.lower()).all()
    elif field_name.lower() == 'phone':
        customers = Customer.query.filter(Customer.phone == normalize_phone_number(field_value)).all()
    else:
        raise APIError(400, "INVAILD_FIELD_NAME", "Field name is not in the list of acceptable field names")

    # If field name is correct but no customers with matching field value
    # is found, returns empty array
    if customers is None:
        return jsonify([])

    # Creates list of different customer's information that match the field value
    cust_infos = []
    for customer in customers:
        humanized_phone, uri_phone = format_phone_number(customer.phone)

        # Add the customer's information to the cust_infos list
        cust_infos.append({
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

    # Returns all found customer's information
    return jsonify(cust_infos)

@app.route("/customer/transaction", methods=["POST"])
@cross_origin()
def api_customer_transaction():
    # Authenticates the employee to access Database
    employee = User.from_authorization(request_access_token(), Employee)

    # Grabs information from the JSON POST data that is used to make transaction information.
    loyalty_id, store_id, date_, items = parse_request("loyaltyID", "storeID", "date", "items")

    # Converts date to iso format using datetime library
    date_of_transaction = date.fromisoformat(date_)

    # HANDLE ERROR IF ITEMS IS EMPTY
    if len(items) == 0:
        raise APIError(400, "EMPTY_SET", "No items in list")

    # Create Transaction in order to have a transaction_id to put in each TransactionLine
    transaction = Transaction(
        date_of_transaction,
        loyalty_id,
        store_id,
        date_of_transaction.year
    )

    # Adds and commits the database transaction so that the transaction.transaction_id
    # field can be populated.
    db.session.add(transaction)
    db.session.commit()

    # Create transaction line for every item in the transaction
    for item in items:

        # If item type is None, delete transaction and commit
        # the change to cancel the transaction
        item_type_id = ItemType.query.filter(db.func.lower(ItemType.item_type) == item["itemType"].lower()).first()
        if item_type_id is None:
            db.session.delete(transaction)
            db.session.commit()
            raise APIError(400, "BAD_ITEM_TYPE", "Item Type does not exist")

        # If unit type is None, delete transaction and commit
        # the change to cancel the transaction
        unit_type_id = UnitType.query.filter(db.func.lower(UnitType.unit_type) == item["unit"].lower()).first()
        if unit_type_id is None:
            db.session.delete(transaction)
            db.session.commit()
            raise APIError(400, "BAD_UNIT_TYPE", "Unit Type does not exist")

        # Create a new TransactionLine item
        transaction_line = TransactionLine(
            item_type_id.item_type_id,
            unit_type_id.unit_type_id,
            item["quantity"],
            item["description"],
            transaction.transaction_id
        )

        # Add and commit the TransactionLine to the database
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
