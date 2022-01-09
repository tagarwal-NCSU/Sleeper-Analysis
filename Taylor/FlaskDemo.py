from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return """<p>Hello, Ike!</p> 
                <form action="/home"> 
                    <input type="text" id = "user_id" name = "user_id">User ID: </input> 
                    <input type="submit" value="Submit">
                </form> """

@app.route("/home")
def home():
    user_id = request.args.get('user_id')

    
    return f"<p>Your user id is {user_id}</p>"