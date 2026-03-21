from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from config import Config
from dotenv import load_dotenv
from utils.ds import Utils
from domain.db.models import db, User, Post
from flask_login import LoginManager, current_user, login_required
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

HOST = os.getenv("HOST")
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "home"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from domain.auth import auth_bp
from domain.posts import posts_bp
app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)


myutils = Utils()


if not os.path.exists('logs'):
    os.mkdir('logs')

log_file = os.path.join('logs', 'flask_app.log')

handler = RotatingFileHandler(log_file, maxBytes=100000, backupCount=3)
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
)
handler.setFormatter(formatter)

app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

app.logger.info("loading app.py")

@app.route("/")
def home():
    posts = []
    if current_user.is_authenticated:
        posts = Post.query.filter_by(author_id=current_user.id).order_by(Post.created_at.desc()).all()
    return render_template("main.html", posts=posts)

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
    try:
        app.debug = True
        app.run(host=f"{HOST}", port=5000)
    except Exception as e:
        app.logger.debug("Error in starting app:", e)
    