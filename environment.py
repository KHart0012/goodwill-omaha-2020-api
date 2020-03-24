import json
from os import path, environ, urandom
from base64 import b64decode, b64encode

ENVIRONMENT_JSON_FILENAME = "environment.json"

environment_json = None
try:
    with open(path.join(path.dirname(__file__), ENVIRONMENT_JSON_FILENAME)) as file:
        environment_json = json.load(file)
except FileNotFoundError:
    pass # Ignore exception, environment_json will be None in this case

# Get a variable from either "environment.json" or the environment. If `varname`
# exists in neither, it will return `default`.
def variable(varname, default=None):
    if environment_json and varname in environment_json:
        return environment_json[varname]
    elif varname in environ:
        return environ[varname]
    else:
        return default

DB_URI = variable("DATABASE_URL")
AZURE_ENVIRONMENT = variable("ENVIRONMENT", default="unknown")
JWT_SECRET = b64decode(variable("JWT_SECRET", default=b64encode(urandom(32))))
BCRYPT_LOG_ROUNDS = variable("BCRYPT_LOG_ROUNDS", default=12)

if not DB_URI:
    raise KeyError("DATABASE_URL not found! Please create an environment.json " +
        "or set it as an environment variable")
