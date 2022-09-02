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
app.config['SECRET_KEY'] = '123456789'
app.config['SQLALCHEMY_DATABASE_URI'] = '#DB PATH#'
app.config['UPLOAD_PATH'] = 'static/img'
db = SQLAlchemy(app)
key = Fernet.generate_key()
print(key)
login_manager = LoginManager()
login_manager.login_view = 'loginApp'
login_manager.init_app(app)


#DB App
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
        todos = Todo.query.filter(Todo.title.contains(q) | Todo.category.contains(q) | Todo.appname.contains(q))
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
        filename = secure_filename(file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

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
        if request.method == 'POST':
            rule_update.file = request.files["file"]
            filename = secure_filename(file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

        db.session.commit()
        return render_template("update.html",todo = todo,rule_update = rule_update,filename=file.filename,file=file.read())       
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
                flash('Login successful!', category='success')
                login_user(user, remember=False)
                return redirect(url_for("dashboard"))
            else:
                flash('Password is wrong!', category='error')
        else:
            flash('Username is wrong!', category='error')
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
            flash('Username alredy exist', category='error')
        elif len(username) < 4:
            flash('Username must be at least 3 characters', category='error')
        elif len(first_name) < 2:
            flash('Name must be at least 2 characters', category='error')
        elif password1 != password2:
            flash('Password did not match', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
        else:
            new_user = User(username=username, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=False)
            flash('User Created!', category='success')
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
