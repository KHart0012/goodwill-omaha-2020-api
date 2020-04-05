import itertools
import pytest
import re
import requests
import subprocess
import time

PORT = 8001
API_ROOT = "http://localhost:" + str(PORT)
# Assumes accurate test data is loaded to DB
# run `python ./manage.py db upgrade`
# and `python ./manage.py db seed_db`
# on a fresh postgres DB to get this data.

def setup_module(mod):
    mod.gunicorn = subprocess.Popen(["gunicorn", "--bind", "127.0.0.1:" + str(PORT), "application:app"])
    for i in itertools.count():
        try:
            time.sleep(0.5) # Give gunicorn time to start
            requests.get(API_ROOT + "/").json()
            break
        except:
            # Give gunicorn 5 seconds to start
            if i >= 10:
                raise

def teardown_module(mod):
    mod.gunicorn.terminate()
    mod.gunicorn.wait()

@pytest.fixture
def customer_authorization():
    req = requests.post(API_ROOT + "/customer/login",
        {"loyaltyID": "67417", "password": "hunter2"})
    req.raise_for_status()
    return "Bearer " + req.json()["accessToken"]

@pytest.fixture
def employee_authorization():
    req = requests.post(API_ROOT + "/employee/login",
        {"employeeID": "67416", "password": "hunter3"})
    req.raise_for_status()
    return "Bearer " + req.json()["accessToken"]

def assert_api_error(req, http_code, error_code, error_msg):
    result = req.json()
    assert req.status_code == http_code
    assert "errorCode" in result
    assert "error" in result
    assert result["errorCode"] == error_code
    assert result["error"] == error_msg

def assert_key_type(obj, key, type, nullable=False):
    assert key in obj
    assert isinstance(obj[key], type) or (nullable and not obj[key])

def test_root():
    req = requests.get(API_ROOT + "/")
    req.raise_for_status()
    req.json()

def test_customer_login_good():
    req = requests.post(API_ROOT + "/customer/login",
        {"loyaltyID": "67417", "password": "hunter2"})
    req.raise_for_status()
    result = req.json()
    assert "accessToken" in result

def test_customer_login_bad():
    # password wrong
    req = requests.post(API_ROOT + "/customer/login",
        {"loyaltyID": "67417", "password": "wrongPassword"})
    assert_api_error(req, 403, "AUTHENTICATION_FAILURE", "Loyalty ID or password is incorrect.")

    # username wrong
    req = requests.post(API_ROOT + "/customer/login",
        {"loyaltyID": "22335", "password": "hunter2"})
    assert_api_error(req, 403, "AUTHENTICATION_FAILURE", "Loyalty ID or password is incorrect.")

    # Both wrong
    req = requests.post(API_ROOT + "/customer/login",
        {"loyaltyID": "22335", "password": "wrongPassword"})
    assert_api_error(req, 403, "AUTHENTICATION_FAILURE", "Loyalty ID or password is incorrect.")

# def test_endpoint_with_no_auth():
#     req = requests.get(API_ROOT + "/customer/info")
#     assert_api_error(req, 401, "UNAUTHORIZED",
#         "Bad request: you must be supply authorization to this resource.")

def test_customer_info(customer_authorization):
    req = requests.get(API_ROOT + "/customer/info", headers={"Authorization": customer_authorization})
    req.raise_for_status()
    result = req.json()
    assert_key_type(result, "loyaltyID", int)
    assert_key_type(result, "firstName", str)
    assert_key_type(result, "lastName", str)
    assert_key_type(result, "email", str, nullable=True)
    assert_key_type(result, "phone", str, nullable=True)
    assert_key_type(result, "phoneURI", str, nullable=True)
    assert re.compile(r'^tel:').match(result["phoneURI"]) != None

    assert "address" in result
    assert_key_type(result["address"], "line1", str, nullable=True)
    assert_key_type(result["address"], "line2", str, nullable=True)
    assert_key_type(result["address"], "city", str, nullable=True)
    assert_key_type(result["address"], "state", str, nullable=True)
    assert_key_type(result["address"], "zip", str, nullable=True)


def test_customer_info_bad_role(employee_authorization):
    req = requests.get(API_ROOT + "/customer/info", headers={"Authorization": employee_authorization})
    assert_api_error(req, 403, "FORBIDDEN", "You do not have access to this resource.")

def test_customer_history(customer_authorization):
    req = requests.get(API_ROOT + "/customer/history", headers={"Authorization": customer_authorization})
    req.raise_for_status()
    result = req.json()
    assert "taxYears" in result
    for year in result["taxYears"]:
        assert isinstance(year, int)

def test_customer_history_bad_role(employee_authorization):
    req = requests.get(API_ROOT + "/customer/history", headers={"Authorization": employee_authorization})
    assert_api_error(req, 403, "FORBIDDEN", "You do not have access to this resource.")

def test_customer_history_year(customer_authorization):
    req = requests.get(API_ROOT + "/customer/history/year/2019", headers={"Authorization": customer_authorization})
    req.raise_for_status()
    result = req.json()
    assert "history" in result
    for transaction in result["history"]:
        # assert_key_type(transaction, "id", int)
        assert_key_type(transaction, "date", str)
        assert "items" in transaction
        for item in transaction["items"]:
            assert_key_type(item, "itemType", str)
            assert_key_type(item, "unit", str)
            assert_key_type(item, "quantity", int)
            assert_key_type(item, "description", str)

def test_customer_history_year_bad_role(employee_authorization):
    req = requests.get(API_ROOT + "/customer/history/year/2019", headers={"Authorization": employee_authorization})
    assert_api_error(req, 403, "FORBIDDEN", "You do not have access to this resource.")
