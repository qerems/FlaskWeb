from ast import Bytes
from cmath import log
from distutils.command.upload import upload
import os
import string
from tkinter import Image
from tokenize import String
from flask import Flask,render_template,request,redirect, send_file,url_for,Response,flash
from flask_login import UserMixin,login_user, login_required, logout_user, current_user,LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import cryptography
from cryptography.fernet import Fernet
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nsc123 956csn'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/kerem/Desktop/todoapp/todo.db'
db = SQLAlchemy(app)
key = Fernet.generate_key()
print(key)
login_manager = LoginManager()
login_manager.login_view = 'loginApp'
login_manager.init_app(app)


#Kural App
@app.route("/index")
@login_required
def index():
    todos = Todo.query.all()
    return render_template("index.html",todos = todos) 

@app.route("/rules")
@login_required
def rulesTodo():
    q = request.args.get("q")

    if q:
        todos = Todo.query.filter(Todo.title.contains(q) | Todo.category.contains(q))
    else:
        todos = Todo.query.all()

    return render_template("rules.html",todos = todos,q = q)

@app.route("/add",methods = ["POST"])
@login_required
def addTodo():
    title = request.form.get("title")
    content = request.form.get("content")
    category = request.form.get("category")
    contentx = request.form.get("contentx")
    appname = request.form.get("appname")
    if request.method == 'POST':
        file = request.files["file"]

    newTodo = Todo(title = title,content = content,category = category,contentx = contentx,appname = appname,filename=file.filename, file=file.read())

    db.session.add(newTodo)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<string:id>")
@login_required
def deleteTodo(id):
    todo = Todo.query.filter_by(id=id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/detail/<string:id>")
@login_required
def detailTodo(id):
    todo = Todo.query.filter_by(id=id).first()

    return render_template("detail.html",todo = todo)

@app.route("/update/<int:id>", methods=["POST","GET"])
@login_required
def updateTodo(id):
    todo = Todo.query.filter_by(id=id).first()
    rule_update = Todo.query.get_or_404(id)
    if request.method == "POST":
        rule_update.title = request.form["title"]
        rule_update.category = request.form["category"]
        rule_update.content= request.form["content"]
        rule_update.contentx = request.form["contentx"]
        rule_update.appname = request.form["appname"]
        rule_update.file = request.form["file"]
        
        db.session.commit()
        return render_template("update.html",todo = todo,rule_update = rule_update)       
    else:
        return render_template("update.html",todo = todo,rule_update = rule_update)
#Login
@app.route("/", methods=['GET','POST'])
def loginApp():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Giriş Başarılı!', category='success')
                login_user(user, remember=False)
                return redirect(url_for("dashboard"))
            else:
                flash('Şifre Hatalı!', category='error')
        else:
            flash('Kullanıcı Adı Hatalı!', category='error')
    return render_template("login.html", user=current_user)

@app.route("/dashboard", methods=["GET","POST"])
@login_required
def dashboard():

    user = User.query.all()

    return render_template("dashboard.html",user=user)

@app.route("/logout")
@login_required
def logoutApp():
    logout_user()
    return redirect(url_for("loginApp"))

@app.route("/sign_up", methods=['GET','POST'])
@login_required
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Kullanıcı Adı Zaten Var', category='error')
        elif len(username) < 4:
            flash('Kullanıcı Adı 3 Karakterden Fazla Olmalıdır', category='error')
        elif len(first_name) < 2:
            flash('İsim 2 Karakterden Fazla Olmalıdır', category='error')
        elif password1 != password2:
            flash('Parola Uyuşmadı', category='error')
        elif len(password1) < 7:
            flash('Parola En Az 7 Karakterden Oluşmalıdır', category='error')
        else:
            new_user = User(username=username, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=False)
            flash('Kullanıcı Oluşturuldu!', category='success')
            return redirect(url_for("dashboard"))

    return render_template("sign_up.html", user=current_user)

@login_manager.user_loader
def _load_user(id):
    return User.query.get(int(id))
 
#Veritabanları
class Todo(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(80),nullable=True)
    content = db.Column(db.Text,nullable=True)
    category = db.Column(db.Text)
    contentx = db.Column(db.Text)
    appname = db.Column(db.Text)
    filename = db.Column(db.String(50))
    file = db.Column(db.LargeBinary)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(150),unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))

if __name__ == "__main__":
    app.run(debug=True)
