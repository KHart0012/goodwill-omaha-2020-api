import json
from os import path, environ, urandom

ENVIRONMENT_JSON_FILENAME = "environment.json"

environment_json = None
try:
    with open(path.join(path.dirname(__file__), ENVIRONMENT_JSON_FILENAME)) as file:
        environment_json = json.load(file)
except FileNotFoundError:
    pass # Ignore exception, environment_json will be None in this case

# Get a variable from either "environment.json" or the environment. If `varname`
# exists in neither, it will return None.
def variable(varname, default = None):
    if environment_json and varname in environment_json:
        return environment_json[varname]
    elif varname in environ:
        return environ[varname]
    else:
        return default

DB_URI = variable("db_uri")
AZURE_ENVIRONMENT = variable("azure_environment", default = "unknown")
JWT_SECRET = variable("jwt_secret", default = urandom(32))

if not DB_URI:
    raise KeyError("db_uri not found! Please create an environment.json " +
        "or set it as an environment variable")
