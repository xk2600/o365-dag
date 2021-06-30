from flask import Flask
frpm requests import get


app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

