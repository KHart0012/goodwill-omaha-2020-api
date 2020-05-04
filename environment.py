import json
from os import path, environ, urandom
from base64 import b64decode, b64encode

# TO SET ENVIRONMENT VARIABLES
# ----------------------------
#
# either set them in the system environment, or create an "environment.json"
# file at the project root with the following structure:
#
#    {
#        "DATABASE_URL": string,      # required
#        "ENVIRONMENT": string,       # defaults to "unknown"
#        "JWT_SECRET": string,        # defaults to a random value
#        "BCRYPT_LOG_ROUNDS": integer # defaults to 12
#    }
#
# DATABASE_URL:
# A URL such as "postgres://localhost/db_name" or similar
#
# ENVIRONMENT:
# a descriptive string that is currently only printed verbatim in the "GET /"
# endpoint for informational purposes.
#
# JWT_SECRET:
# Set to a base64 encoded random value. It is important for security that this
# has 128 or 256 bits of entropy. While you can leave this unset for testing
# purposes, it is highly recommended to set this to a specific value so that
# user sessions will work across restarts, and across multiple instances. This
# value must be carefully guarded; it is a session-equivalent for all users.
#
# To generate this, you can run the following code at command line
#
#     python -c 'import base64,os; print(base64.b64encode(os.urandom(32)).decode())'
#
# BCRYPT_LOG_ROUNDS:
# Used to tune how long password hashing and verifying should take. In general,
# a larger value => more security, but more wait time; and a lower value is less
# of both. This value is logarithmic, an increment or a decrement corresponds to
# a doubling or halving of the time cost, respectively.


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

DATABASE_URL = variable("DATABASE_URL")
ENVIRONMENT = variable("ENVIRONMENT", default="unknown")
JWT_SECRET = b64decode(variable("JWT_SECRET", default=b64encode(urandom(32))))
BCRYPT_LOG_ROUNDS = variable("BCRYPT_LOG_ROUNDS", default=12)

if not DATABASE_URL:
    raise KeyError("DATABASE_URL not found! Please create an environment.json " +
        "or set it as an environment variable")
