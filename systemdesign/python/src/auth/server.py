import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server =  Flask(__name__)
mysql = MySQL(server)

# config 
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")

@server.route("/login", methods=["POST"])
def login():

    auth = request.authorization
    
    if not auth:
        return "missing credentials", 401
    
    # check for username and password
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT emali, password FROM user WHERE email = '%s'", (auth.username)
    )
    
    if res > 0:
         user_row = cur.fetchone()
         email_r = user_row[0]
         password_r = user_row[1]
         
         if auth.username != email_r or auth.password != password_r:
             return "invalid username or password", 401
         else:
             return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
         
    else:
        return "user not found", 401
    
@server.route("/validate", methods=["POST"])
def validate():
    encode_jwt =  request.headers["Authorization"]
    
    if not encode_jwt :
        return "missing credentials", 401
    
    encode_jwt = encode_jwt.split(" ")[1]
    
    try:
        decoded = jwt.decode(
            encode_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"])
    except:
        return "not authorized", 403
    
    return decoded, 200

def createJWT(username, secret, auth):
    
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": auth,            
        },
        secret,
        algorithm="HS256"
    )
    
    
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)