import jwt
import datetime

from app_init import app, db, bcrypt

class User(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_type = db.Column(db.String(255), nullable = False)
    password = db.Column(db.String(255), nullable = False)

    def __init__(self, user_type, password):
        self.user_type = user_type
        self.password = bcrypt.generate_password_hash(password,
            app.config["BCRYPT_LOG_ROUNDS"]).decode()

    def encode_auth_token(self, user_id, timeout = datetime.timedelta(hours = 1)):
        payload = {
            'exp': datetime.datetime.utcnow() + timeout,
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, app.config["JWT_SECRET"], algorithm = 'HS256')

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, app.config["JWT_SECRET"])
            if JWTBlacklist.token_blacklisted(auth_token):
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

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
    def token_blacklisted(auth_token):
        res = JWTBlacklist.query.filter_by(token = str(auth_token)).first()
        if res:
            return True
        else:
            return False
