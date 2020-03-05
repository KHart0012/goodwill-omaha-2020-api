import json
from os import path, environ

ENVIRONMENT_JSON_FILENAME = "environment.json"

environment_json = None
try:
    with open(path.join(path.dirname(__file__), ENVIRONMENT_JSON_FILENAME)) as file:
        environment_json = json.load(file)
except FileNotFoundError:
    pass # Ignore exception, environment_json will be None in this case

# Get a variable from either "environment.json" or the environment. If `varname`
# exists in neither, it will return None.
def variable(varname):
    if environment_json and varname in environment_json:
        return environment_json[varname]
    elif varname in environ:
        return environ[varname]
    else:
        return None
