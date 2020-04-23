#!/usr/bin/env python3

from datetime import date
from flask import jsonify
from flask_cors import cross_origin

from app_init import app, bcrypt, db
from environment import AZURE_ENVIRONMENT
from utility import APIError, format_phone_number, normalize_phone_number, request_access_token, parse_request
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
    transactions = Transaction.query.filter_by(loyalty_id=customer.loyalty_id)

    tax_years = map(lambda x : x.date.year, transactions)
    return jsonify({
        "taxYears": list(tax_years)
    })

@app.route("/customer/history/year/<year>", methods=["GET"])
@cross_origin()
def api_customer_history_year(year):
    customer = User.from_authorization(request_access_token(), Customer)
    transactions = Transaction.query.filter_by(loyalty_id=customer.loyalty_id)

    history = []
    for transaction in transactions:
        if transaction.date.year == int(year):
            transaction_lines = TransactionLine.query.filter_by(transaction_id=transaction.transaction_id)
            items = []
            for transaction_line in transaction_lines:
                items.append({
                    "itemType": ItemType.query.get(transaction_line.item_type_id),
                    "unit": UnitType.query.get(transaction_line.unit_type_id),
                    "quantity": transaction_line.quantity,
                    "description": transaction_line.description
                })

            history.append({
                "transactionID": 410992,
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
    employee = User.from_authorization(request_access_token(), Employee)
    customer = Customer.query.filter_by(loyalty_id=loyalty_id).first()

    if customer is None:
        raise APIError(404, "NOT_FOUND", "Loyalty ID Not Found")

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

    if customers is None:
        return jsonify([])

    cust_infos = []
    for customer in customers:
        humanized_phone, uri_phone = format_phone_number(customer.phone)
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
    
    return jsonify(cust_infos)

@app.route("/customer/transaction", methods=["POST"])
@cross_origin()
def api_customer_transaction():
    employee = User.from_authorization(request_access_token(), Employee)

    loyalty_id, store_id, date_, items = parse_request("loyaltyID", "storeID", "date", "items")    
    date_of_transaction = date.fromisoformat(date_)

    # HANDLE ERROR IF ITEMS IS EMPTY
    if len(items) == 0:
        raise APIError(400, "EMPTY_SET", "No items in list")

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
        # If item type is None, delete transaction line to cancel transaction
        item_type_id = ItemType.query.filter_by(item_type=item["itemType"]).first()
        if item_type_id is None:
            db.session.delete(transaction)
            db.session.commit()
            raise APIError(400, "BAD_ITEM_TYPE", "Item Type does not exist")

        unit_type_id = UnitType.query.filter_by(unit_type=item["unit"]).first()
        # If unit type is None, delete transaction line to cancel transaction
        if unit_type_id is None:
            db.session.delete(transaction)
            db.session.commit()
            raise APIError(400, "BAD_UNIT_TYPE", "Unit Type does not exist")

        transaction_line = TransactionLine(
            item_type_id.item_type_id,
            unit_type_id.unit_type_id,
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
