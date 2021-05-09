from werkzeug.security import generate_password_hash  , check_password_hash
#Flask utils
from flask import Flask, jsonify , request
from flask_sqlalchemy import SQLAlchemy
import requests
import os 

dir_path = os.path.dirname(os.path.realpath('__file__'))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    username = db.Column(db.String(80) , unique = True , nullable = False )
    fullname = db.Column(db.String(120) , unique = True , nullable = False )
    email = db.Column(db.String(120) , unique = True , nullable = False )
    password_hash = db.Column(db.String(120))
    
    def set_password(self , password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash , password)

    def __repr__(self):
        info = {"username" : self.username , 
                "fullname" : self.fullname , 
                "email" : self.email }
        return info

db.create_all()


@app.route('/') 
def home():
    users , data = User.query.all() , []

    for u in users:
        drink_data = {'name' : u.username , 'fullname' : u.fullname  , "email" :u.email , "password_hash" : u.password_hash}
        data.append(drink_data)

    return jsonify({"users": data})




@app.route('/API/login' , methods = ['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        msg = {"status" :
               {"type" : "failure" , "msg" : "missing data"}
            }
        return jsonify(msg)

    user = User.filter_by(username = username).first() 

    if not user or not user.check_password(password):
        msg = {"status" : { "type" : "failure" ,   "message" : "Username or password incorrect"}}
    else:
        msg = {"status" : { "type" : "success" ,
                             "message" : "You logged in"} , 
               "data" : {"user" : user.getJsonData() }
        }

    return jsonify(msg)


@app.route('/API/register', methods=['POST'])
def register():
    username = request.form.get('username')
    fullname = request.form.get('fullname')
    password = request.form.get('password')
    email = request.form.get('email')

    if not username or not fullname or not email or not password:
        msg = {"status" : { "type" : "failure" ,   "message" : "missing data"}}
        return jsonify(msg)
    if User.filter_by(username = username).count() == 1 :
        msg = {"status" : { "type" : "failure" ,   "message" : "username already taken"}}
        return jsonify(msg)

    if User.filter_by(email = email).count() == 1:
        msg = {"status" : { "type" : "failure" ,   "message" : "email already taken"}}
        return jsonify(msg)

    user = User(username =  username , fullname = fullname , email = email , password = password)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    msg = {"status" : { "type" : "success" ,   "message" : "You have registered"}}
    return jsonify(msg)



if __name__ == "__main__":
    app.run(debug = True)
