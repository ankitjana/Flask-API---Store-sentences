from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
# from flask.ext.bcrypt import Bcrypt
import bcrypt

app = Flask(__name__)

app = Flask(__name__)
api = Api(app)
# bcrypt = Bcrypt(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db["Users"]
# sentences = db["sentences"]

class Register(Resource):
    def post(self):
        postedData = request.get_json()

        # get the data, validate the un,pw
        username = postedData["username"]
        password = postedData["password"]
        #hash password
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        # Store un and pw in db
        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Sentence": "",
            "Tokens": 6
        })

        retJson = {
            "status":200,
            "msg": "You successfully signed up for the API"
        }
        return jsonify(retJson)

api.add_resource(Register, '/register')

def verifyPw(username, password):
    hashed_pw = users.find({
        "Username":username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({
        "Username":username
    })[0]["Tokens"]
    return tokens

class Store(Resource):
    def post(self):
        # get posted data
        postedData = request.get_json()

        # get the data
        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]

        # verify UN and pwd
        correct_pw = verifyPw(username,password)

        if not correct_pw:
            retJson = {
                "status":302
            }
            return jsonify(retJson)

        # verify if enough tokens
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status" : 301
            }
            return jsonify(retJson)

        users.update({
            "Username":username
        }, {
            "$set":{
                "Sentence":sentence,
                "Tokens":num_tokens-1
                }
        })
        retJson = {
            "status" :200,
            "msg" : " Successfully stored"
        }
        return jsonify(retJson)
        
api.add_resource(Store, '/store')

class Get(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]

        correct_pw = verifyPw(username,password)

        if not correct_pw:
            retJson = {
                "status":302
            }
            return jsonify(retJson)
        
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status" : 301
            }
            return jsonify(retJson)

        users.update({
            "Username":username
        }, {
            "$set":{
                "Tokens":num_tokens-1
                }
        })

        sentence = users.find({
            "Username": username
        })[0]["Sentence"]

        retJson = {
            "status": 200,
            "sentence": sentence
        }
        return jsonify(retJson)



api.add_resource(Get, '/get')

if __name__=="__main__":
    app.run(host='0.0.0.0')
