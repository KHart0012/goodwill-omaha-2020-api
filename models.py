import jwt
import datetime

from app_init import app, db, bcrypt

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

    def __init__(self, user_type, password):
        self.user_type = user_type
        self.password = bcrypt.generate_password_hash(password,
            app.config["BCRYPT_LOG_ROUNDS"]).decode()

    @staticmethod
    def from_authorization(access_token):
        payload = jwt.decode(access_token, app.config["JWT_SECRET"])
        if JWTBlacklist.token_blacklisted(access_token):
            raise JWTBlacklistedError("Key expired (logout)")
        return User.query.filter_by(user_id=payload['sub']).first()

    def is_authentic(self, candidate_password):
        return bcrypt.check_password_hash(self.password, candidate_password)

    def generate_access_token(self, timeout=datetime.timedelta(hours=1)):
        # SECURITY: This payload is only signed, not encrypted, so do not put
        # sensitive information inside. Sending a autoincremented user-id may be
        # a business intelligence security flaw. See for more info:
        # https://medium.com/lightrail/prevent-business-intelligence-leaks-by-using-uuids-instead-of-database-ids-on-urls-and-in-apis-17f15669fd2e
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
    loyalty_id = db.Column(db.Integer, nullable=False)


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
    employee_id = db.Column(db.Integer, nullable=False)

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

#TODO: enable some way to clean up this table of expired tokens
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
