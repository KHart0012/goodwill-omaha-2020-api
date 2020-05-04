import jwt
import jwt.exceptions
import datetime

from app_init import app, db, bcrypt
from utility import APIError

# See also: "/docs/ER Diagram.svg"
# All tables besides JWTBlacklist appear on the diagram, JWTBlacklist
# is documented in text form below.

class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_type = db.Column(db.String(4), nullable=False)
    __mapper_args__ = {
        "polymorphic_on": user_type
    }

    password = db.Column(db.String(255), nullable=False)

    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    address1 = db.Column(db.String(255), nullable=True)
    address2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    state = db.Column(db.String(255), nullable=True)
    zip_code = db.Column(db.String(5), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(255), nullable=True)

    def __init__(self, user_type, password, first_name, last_name):
        self.user_type = user_type
        self.password = bcrypt.generate_password_hash(password,
            app.config["BCRYPT_LOG_ROUNDS"]).decode()
        self.first_name = first_name
        self.last_name = last_name

    @staticmethod
    def from_authorization(access_token, expected_type):
        try:
            payload = jwt.decode(access_token, app.config["JWT_SECRET"])
            if JWTBlacklist.token_blacklisted(access_token):
                raise APIError.bad_access_token("Session expired (logout).")

            user = User.query.filter_by(user_id=payload['sub']).first()
            if not isinstance(user, expected_type):
                raise APIError.forbidden()

            return user

        except jwt.ExpiredSignatureError:
            raise APIError.bad_access_token("Session expired.")
        except jwt.InvalidTokenError:
            raise APIError.bad_access_token("Invalid session.")
        except jwt.exceptions.InvalidKeyError: #Happens if alg="none" in received header
            raise APIError.bad_access_token("Invalid session.")

    def is_authentic(self, candidate_password):
        return bcrypt.check_password_hash(self.password, candidate_password)

    def generate_access_token(self, timeout=datetime.timedelta(hours=1)):
        # SECURITY: This payload is only signed, not encrypted, so do not put
        # sensitive information inside. Sending a autoincremented user-id may be
        # a business intelligence security flaw. See for more info:
        # https://medium.com/lightrail/prevent-business-intelligence-leaks-by-using-uuids-instead-of-database-ids-on-urls-and-in-apis-17f15669fd2e

        # Another minor security note: we could use a 'jti' to prevent jwt
        # replay. But doing so would be overkill: we allow unlimited logins and
        # have no need for / implementation of a "logout of all devices" feature
        payload = {
            'exp': datetime.datetime.utcnow() + timeout,
            'iat': datetime.datetime.utcnow(),
            'sub': self.user_id
        }

        # Are you wondering why encode then decode?, the encode returns a byte-string
        # the decode at the end converts it into a JSON serializable string
        return jwt.encode(payload, app.config["JWT_SECRET"], algorithm="HS256").decode()

class Customer(User):
    __tablename__ = "customer"
    __mapper_args__ = {
        "polymorphic_identity": "CUST"
    }

    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), primary_key=True)
    loyalty_id = db.Column(db.Integer, nullable=False, unique=True)

    def __init__(self, loyalty_id, password, first_name, last_name):
        super().__init__("CUST", password, first_name, last_name)
        self.loyalty_id = loyalty_id


    @staticmethod
    def find_and_authenticate(loyalty_id, password):
        user = Customer.query.filter_by(loyalty_id=loyalty_id).first()
        if not user:
            return None
        elif user.is_authentic(password):
            return user
        else:
            return None

class Employee(User):
    __tablename__ = "employee"
    __mapper_args__ = {
        "polymorphic_identity": "EMPL"
    }

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    employee_id = db.Column(db.Integer, nullable=False, unique=True)

    def __init__(self, employee_id, password, first_name, last_name):
        super().__init__("EMPL", password, first_name, last_name)
        self.employee_id = employee_id

    @staticmethod
    def find_and_authenticate(employee_id, password):
        user = Employee.query.filter_by(employee_id=employee_id).first()
        if not user:
            return None
        elif user.is_authentic(password):
            return user
        else:
            return None

class JWTBlacklistedError(Exception):
    pass

# This table stores logged out JWT tokens; currently however, there is no implemented
# way to log out a token, so this table will always be empty.
#
# TODO: implement a way to log out tokens if this is a desired feature
# TODO: enable some way to clean up this table of expired tokens
class JWTBlacklist(db.Model):
    __tablename__ = 'jwt_blacklist'

    id = db.Column('jwt_blacklist_id', db.Integer, primary_key=True, autoincrement=True)
    token = db.Column('token', db.String(500), unique=True, nullable=False)
    blacklistedOn = db.Column('blacklisted_on', db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklistedOn = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}>'.format(self.token)

    @staticmethod
    def token_blacklisted(access_token):
        return JWTBlacklist.query.filter_by(token=str(access_token)).count() != 0


class Store(db.Model):
    __tablename__ = 'store'

    store_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_name = db.Column(db.String(255), nullable=False)

    def __init__(self, store_name):
        self.store_name = store_name


class Transaction(db.Model):
    __tablename__ = 'transaction'

    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    loyalty_id = db.Column(db.Integer, db.ForeignKey('customer.loyalty_id'))
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'))
    tax_year = db.Column(db.Integer, nullable=False)

    def __init__(self, date, loyalty_id, store_id, tax_year):
        self.date = date
        self.loyalty_id = loyalty_id
        self.store_id = store_id
        self.tax_year = tax_year


class TransactionLine(db.Model):
    __tablename__ = 'transaction_line'

    transaction_line_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_type_id = db.Column(db.Integer, db.ForeignKey('item_type.item_type_id'))
    unit_type_id = db.Column(db.Integer, db.ForeignKey('unit_type.unit_type_id'))
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500))
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'))

    def __init__(self, item_type_id, unit_type_id, quantity, description, transaction_id):
        self.item_type_id = item_type_id
        self.unit_type_id = unit_type_id
        self.quantity = quantity
        self.description = description
        self.transaction_id = transaction_id


class ItemType(db.Model):
    __tablename__ = 'item_type'

    item_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_type = db.Column(db.String(255), nullable=False)

    def __init__(self, item_type):
        self.item_type = item_type


class UnitType(db.Model):
    __tablename__ = 'unit_type'

    unit_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    unit_type = db.Column(db.String(255), nullable=False)

    def __init__(self, unit_type):
        self.unit_type = unit_type
