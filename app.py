from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
from sqlalchemy.orm import Session
from config import Config
from dotenv import load_dotenv
from utils.ds import Utils
from domain.db.database import get_db  # Import the DB dependency

load_dotenv()

HOST = os.getenv("HOST")
app = Flask(__name__)
app.config.from_object(Config)


myutils = Utils()


@app.route("/")
def home():
    return render_template("main.html")

@app.route("/query", methods=["POST"])
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
    elif "новости:" in query.lower():
        qword = query[8:]
        res = myutils.get_news(qword)
        return jsonify({"res_list": res, "query": 'query', "type": 2}), 200
    else:
        return jsonify({"success": False, "message": "Incorrect query"}), 401
    
if __name__ == "__main__":
    app.run(host=f"{HOST}", port=5000)