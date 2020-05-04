from flask import request, abort, jsonify
import phonenumbers
import phonenumbers.geocoder

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
    elif request.args:
        requestArray = request.args
    else:
        abort(415) # Unsupported Media Type

    for param in params:
        if not param in requestArray:
            abort(400) # Bad request (missing required argument)
        values.append(requestArray[param])

    if len(values) == 1:
        return values[0]
    else:
        return values

def request_access_token():
    try:
        if not "Authorization" in request.headers:
            abort(401, www_authenticate = "Bearer") # Unauthorized

        authorization_header = request.headers["Authorization"]
        authn_type, authn_value = authorization_header.split(" ", 1)
        if authn_type != "Bearer":
            abort(401, www_authenticate = "Bearer") # Unauthorized

        return authn_value
    except ValueError: #Assuming because tuple unwrap on .split() failed
        abort(400) # Bad request

# Expects the phone number from the database (which should be E.164, but any
# global phone number will work)
#
# Returns a tuple of (the humanized phone number, the RFC 3966 phone number).
# The former is suitable for display to a user, the latter can be used in an <a
# href="...">, or similar contexts
def format_phone_number(phone_number):
    phone_number_info = phonenumbers.parse(phone_number)

    # XXX: this assumes that the user is in the US themselves. If there is a
    # need to show "+1" in front of US numbers, then always choose INTERNATIONAL
    number_format = phonenumbers.PhoneNumberFormat.INTERNATIONAL
    if phonenumbers.geocoder.country_name_for_number(phone_number_info, "en") == "United States":
        number_format = phonenumbers.PhoneNumberFormat.NATIONAL

    return (
        phonenumbers.format_number(phone_number_info, number_format),
        phonenumbers.format_number(phone_number_info, phonenumbers.PhoneNumberFormat.RFC3966),
    )
# Expects the phone number from the user in any parseable format.
#
# Returns an E.164 formatted phone_number, which should be string-comparable
# with the `phone` field in the database.
def normalize_phone_number(phone_number):
    return phonenumbers.format_number(
        phonenumbers.parse(phone_number, "US"),
        phonenumbers.PhoneNumberFormat.E164)

class APIError(Exception):
    # Returns a flask response object for errors specified by the API. This consists
    # of a JSON object describing the error.
    #
    # It is recommended to use one of the other methods in this class that calls
    # into this function (or create one if needed)
    #
    # httpError: A numeric HTTP status code (Use 400-499 for errors because the
    #            front end provided incorrect information, 500-599 for errors
    #            because of some backend issue). For status code best practices,
    #            refer to: https://www.codetinkerer.com/2015/12/04/choosing-an-http-status-code.html
    # errorCode: A short, all-caps string that the front ends can use to
    #            differentiate between different kinds of errors. Use values from
    #            ErrorCodes, which correspond to values in the API specification.
    # error: A human-readable explanation of the error. Make sure this message is
    #        suitable for display to the end user.
    #
    # Use within an "@app.route(...) def" as follows:
    #    raise APIError(403, "FAILURE_REASON", "Human explanation...")
    def __init__(self, httpError, errorCode, error):
        self.httpError = httpError
        self.errorCode = errorCode
        self.error = error

    def api_error_response(self):
        return (jsonify({
            "errorCode": self.errorCode,
            "error": self.error
        }), self.httpError)

    @staticmethod
    def customer_authentication_failure():
        return APIError(403, "AUTHENTICATION_FAILURE", "Loyalty ID or password is incorrect.")

    @staticmethod
    def employee_authentication_failure():
        return APIError(403, "AUTHENTICATION_FAILURE", "Employee ID or password is incorrect.")

    @staticmethod
    def bad_access_token(extra_message=None):
        if extra_message:
            return APIError(401, "BAD_ACCESS_TOKEN", f"{extra_message} Please log in again.")
        else:
            return APIError(401, "BAD_ACCESS_TOKEN", "Please log in again.")

    @staticmethod
    def forbidden():
        return APIError(403, "FORBIDDEN", "You do not have access to this resource.")
