from flask import Flask, request, url_for, render_template
import os

app = Flask(__name__)

@app.context_processor #allows CSS to update (bypass browser cache)
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route("/")
def hello_world():
    return render_template("home.html")

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