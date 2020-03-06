from flask import request, abort, jsonify

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

class APIError:
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
    #    return api_error(403, "FAILURE_REASON", "Human explanation...")
    @staticmethod
    def api_error(httpError, errorCode, error):
        return (jsonify({"errorCode": errorCode, "error": error}), httpError)

    def customer_authentication_failure():
        return APIError.api_error(403, "AUTHENTICATION_FAILURE", "Loyalty ID or password is incorrect.")

    def employee_authentication_failure():
        return APIError.api_error(403, "AUTHENTICATION_FAILURE", "Employee ID or password is incorrect.")

    def bad_access_token():
        return APIError.api_error(403, "BAD_ACCESS_TOKEN", "Please log in again.")
