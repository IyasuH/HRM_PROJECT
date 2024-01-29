import bcrypt

def verify_password(plain_password, hashed_password):
    plain_password_bytes = plain_password.encode("utf-8")
    return bcrypt.checkpw(plain_password_bytes, hashed_password.encode('utf-8'))

def get_password_hash(password):
    password_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_password.decode("utf-8")