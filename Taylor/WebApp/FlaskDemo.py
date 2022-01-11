from flask import Flask, request,url_for

app = Flask(__name__)


@app.route("/")
def hello_world():
    html = f"""
            <html>
                <link rel= "stylesheet" type= "text/css" href="{ url_for('static',filename='style.css') }">
                <h1>Sleeper Analysis</h1> 
                <form action="/home" id="username"> 
                    <label for="username">Username: </label>
                    <input type="text" id = "username" name = "username"></input>
                    <br><br>
                    <input type="submit" value="Submit">
                </form>
            </html>
            """
    return html

@app.route("/home")
def home():
    username = request.args.get('username', "-")
    
    html = f"""
            <html>
                <link rel= "stylesheet" type= "text/css" href="{ url_for('static',filename='style.css') }">
                <h1>Your username is {username}</h1>
            </html>
            """

    return html

app.run(debug = True)