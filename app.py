from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
from flask_sqlalchemy import SQLAlchemy
from config import Config
from dotenv import load_dotenv
from utils.ds import Utils

app = Flask(__name__)
app.config.from_object(Config)
db=SQLAlchemy(app)

myutils = Utils()

CORRECT_PASSWORD = os.getenv("SECRET_PASSWORD", "123094;sjasdfiEJEdf")

@app.route("/")
def home():
    return render_template("/main.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    query = data.get("password")
    if "фирма:" in query.lower():
        comp_name = str(query[6:].strip())
        lk = myutils.get_company(comp_name)
        return jsonify({"data": lk, "query": comp_name, "type": 1, }), 200
    elif "тнвэдкод:" in query.lower():
        qwords = query[9:].split(" ")
        res = myutils.find_hscodes(qwords)
        return jsonify({"res_list": res, "query": 'query', "type": 2}), 200
    else:
        return jsonify({"success": False, "message": "Incorrect query"}), 401
    
if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000)
    app.run(host="127.0.0.1", port=5000)