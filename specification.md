# Goodwill of Omaha - API Specification

Table of Contents:

<!-- Generated via: `ruby make-toc.rb specification.md` -->
1. [How to Call](#how-to-call)
1. [Error Return](#error-return)
1. [Authentication and Authorization](#authentication-and-authorization)
1. [Passing Parameters](#passing-parameters)
1. [Service API for Goodwill Omaha Customers](#service-api-for-goodwill-omaha-customers)
   1. [Customer Login Request](#customer-login-request)
   1. [Get Customer Information](#get-customer-information)
   1. [Get Customer’s List of Tax Years](#get-customers-list-of-tax-years)
   1. [Get Customer History For a Current Year](#get-customer-history-for-a-current-year)
1. [Service API for Goodwill Omaha employees](#service-api-for-goodwill-omaha-employees)
   1. [Employee Login Request](#employee-login-request)
   1. [Customer Lookup (by loyaltyID)](#customer-lookup-by-loyaltyid)
   1. [Customer Lookup (by any other field)](#customer-lookup-by-any-other-field)
   1. [Add Transaction](#add-transaction)
1. [DB Design](#db-design)

## How to Call

API URL: https://goodwill-nw2020.herokuapp.com/

Do not access over plain HTTP.

## Error Return

All requests may return an error instead of the specified output JSON. The
endpoint instead responds with HTTP 4xx or 5xx as appropriate for the type of
error that occurred. It outputs the following JSON:

    {"errorCode": string, "error": string, ...}

- `"errorCode"`: value is suitable for differentiating between different kinds
  of errors. Typically this will be a rather short, all-caps identifier.
- `"error"`: value is suitable for display to the end user.
- Additional key/values may exist in the JSON, but these are meant for debugging
  purposes only.

See also the documentation for each endpoint. If there are expected errors that
clients should catch, those will be enumerated. However, internal server errors
may occur, and clients must prepare for all endpoints to return unexpected
errors in addition to expected errors.

## Authentication and Authorization

Clients can use either `POST /customer/login` or `POST /employee/login` to
receive an access token. Store this token for a user session and clear the token
when the user wishes to log out.

For all other endpoints, you must provide the access token as follows in an HTTP
authorization header:

    Authorization: Bearer accessTokenGoesHere

where `accessTokenGoesHere` is replaced with the access token received from the
login request. For further reading, see documentation on the [Authorization
header] and on [Bearer tokens].

**Implementation note**: The access token provided is a JWT token containing
only the logged in user's ID (not the same thing as their loyaltyID or
employeeID).

[Authorization header]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization
[Bearer tokens]: https://oauth.net/2/bearer-tokens/

## Passing Parameters

For POST and PUT requests, the parameters may be specified as urlencoded form
data or as a JSON object. For example, a login request can take either the form:

    POST /customer/login
    Content-Type: application/json

    {
        "loyaltyID": "0118999",
        "password": "superSecretPassword"
    }

or the form:

    POST /customer/login
    Content-Type: application/x-www-form-urlencoded

    loyaltyID=0118999&password=superSecretPassword

For GET, HEAD, DELETE, the parameters will be specified in the query string,
e.g.:

    GET /customer/info?loyaltyID=67417

or substituted into the URL itself, e.g.:

    GET /customer/history/year/2020

## Service API for Goodwill Omaha Customers

### Customer Login Request

![Status: Operational](https://img.shields.io/badge/status-operational-green)

Accepts a customer’s loyalty ID and password, and returns an access token that
is required for all other API calls (so long as the loyalty ID and password are
a valid pair).

    POST /customer/login

Parameters:

- `loyaltyID` (string): The customer supplied loyalty ID (used as a stand-in for
  a username)
- `password` (string): The customer supplied password, in plain-text

Output:

    {"accessToken": string}

See "Authentication and Authorization" above for more details.

Errors:

- HTTP 403 with JSON: `{"errorCode": "AUTHENTICATION_FAILURE", "error": "Loyalty ID or password is incorrect."}`

cURL Test Command:

    curl -i -X POST "https://goodwill-nw2020.herokuapp.com/customer/login" --data "loyaltyID=67417&password=hunter2"

Save the access token in a shell variable `$accessToken` to make other cURL
commands work.

### Get Customer Information

![Status: Operational](https://img.shields.io/badge/status-operational-green)

    GET /customer/info

Authorization required. See "Authentication and Authorization" above for more
details.

Output JSON:

    {
        "firstName": string,
        "lastName": string,
        "address": {
            "line1": string,
            "line2": string,
            "city": string,
            "state": string,
            "zip": string
        }
        "email": string,
        "phone": string
    }

cURL Test Command:

    curl -i -X GET "https://goodwill-nw2020.herokuapp.com/customer/info" -H "Authorization: Bearer $accessToken"

### Get Customer’s List of Tax Years

![Status: Stub data only](https://img.shields.io/badge/status-stub%20data%20only-yellow)

Returns the list of possible tax years the currently logged in customer can
select.

    GET /customer/history

Authorization required. See "Authentication and Authorization" above for more
details.

Output JSON:

    {
        "taxYears": [
            integer,
            ...
        ]
    }

Errors:

- HTTP 403 with JSON: `{"errorCode": "TOKEN_EXPIRED", "error": "You have been logged out for too long. Please log in again."}`

cURL Test Command:

    curl -i -X GET "https://goodwill-nw2020.herokuapp.com/customer/history" -H "Authorization: Bearer $accessToken"

cURL Test Result (sample):

    {
        "taxYears": [2017, 2018, 2019]
    }

### Get Customer History For a Current Year

![Status: Stub data only](https://img.shields.io/badge/status-stub%20data%20only-yellow)

    GET /customer/history/year/:year

- `:year` (integer) is replaced by a year

Authorization required. See "Authentication and Authorization" above for more
details.

Output JSON:

    {
        "history": [
            {
                "id": int,
                "date": string,
                "items": [
                    {
                        "itemType": string,
                        "unit": string,
                        "quantity": int,
                        "description": string
                    },
                    ...
                ]
            },
            ...
        ]
    }

Errors:

- HTTP 403 with JSON `{"errorCode": "TOKEN_EXPIRED", "error": "You have been logged out for too long. Please log in again."}`

## Service API for Goodwill Omaha employees

### Employee Login Request

![Status: Operational](https://img.shields.io/badge/status-operational-green)

    POST /employee/login

Parameters:

- `employeeID` (string): An employee supplied ID
- `password` (string): An employee supplied password, in plain-text

Output JSON:

    {"accessToken": string}

See "Authentication and Authorization" above for more details.

cURL Test Command:

    curl -i -X POST "https://goodwill-nw2020.herokuapp.com/employee/login" --data "employeeID=67416&password=hunter3"

Save the access token in a shell variable `$accessToken` to make other cURL
commands work.

### Customer Lookup (by loyaltyID)

![Status: Stub data only](https://img.shields.io/badge/status-stub%20data%20only-yellow)

    GET /customer/:loyaltyID/info

Parameters:

- `:loyaltyID` (string): Replace with the loyaltyID of the customer to get
  information on.

Authorization required. See "Authentication and Authorization" above for more
details.

Output JSON:

    {
        "firstName": string,
        "lastName": string,
        "address": {
            "line1": string,
            "line2": string,
            "city": string,
            "state": string,
            "zip": string
        }
        "email": string,
        "phone": string
    }

cURL Test Command:

    curl -i -X GET "https://goodwill-nw2020.herokuapp.com/customer/67417/info" -H "Authorization: Bearer $accessToken"

### Customer Lookup (by any other field)

![Status: Stub data only](https://img.shields.io/badge/status-stub%20data%20only-yellow)

    GET /customer/by/:fieldName/:fieldValue

- `:fieldName` (string): Replaced with the field by which to look up. The
  following are searchable fields:
  - `phone`
  - `firstName`
  - `lastName`
  - `address`
  - `email`
- `:fieldValue`: Replaced with the value of the field looking up against.

Authorization required. See "Authentication and Authorization" above for more
details.

Output JSON:

    [
        {
            "firstName": string,
            "lastName": string,
            "address": {
                "line1": string,
                "line2": string,
                "city": string,
                "state": string,
                "zip": string
            }
            "email": string,
            "phone": string
        },
        ... // Possibly more than one, or no customers at all
    ]

### Add Transaction

![Status: Implemented but has no effect](https://img.shields.io/badge/status-implemented%20but%20has%20no%20effect-yellow)

    POST /customer/transaction

This endpoint doesn't support urlencoded parameters.

Input JSON:

    {
        "date": string,
        "items": [
            {
                "itemType": string,
                "unit": string,
                "quantity": int,
                "description": string
            }
        ]
    }

Authorization required. See "Authentication and Authorization" above for more
details.

Output JSON:

    {
        "transactionID": int
    }

## DB Design

![ER Diagram](https://raw.githubusercontent.com/KHart0012/goodwill-omaha-2020-api/master/docs/ER%20Diagram.png)
