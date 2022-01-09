from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/")
def hello_world():
    html = """
            <html>
                <h1>Sleeper Analysis</h1> 
                <form action="/home"> 
                    <label for="username">Username: </label>
                    <input type="text" id = "username" name = "username"></input> 
                    <input type="submit" value="Submit">
                </form>
            </html>
            """
    

    return html

@app.route("/home")
def home():
    username = request.args.get('username', "-")
    

    return f"<p>Your username is {username}</p>"

app.run(debug = True)