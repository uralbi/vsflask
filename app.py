from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)

app.config.from_object(Config)

db=SQLAlchemy(app)

@app.route("/")
def home():
    return render_template("/main.html")

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000)
    app.run(host="127.0.0.1", port=5000)