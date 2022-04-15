from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import cryptography
from cryptography.fernet import Fernet

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/kerem/Desktop/todoapp/todo.db'
db = SQLAlchemy(app)
key = Fernet.generate_key()
print(key)

@app.route("/")
def index():
    todos = Todo.query.all()

    return render_template("index.html",todos = todos)

@app.route("/rules")
def rulesTodo():
    q = request.args.get("q")

    if q:
        todos = Todo.query.filter(Todo.title.contains(q) | Todo.category.contains(q))
    else:
        todos = Todo.query.all()

    return render_template("rules.html",todos = todos,q = q)

@app.route("/add",methods = ["POST"])
def addTodo():
    title = request.form.get("title")
    content = request.form.get("content")
    category = request.form.get("category")
    contentx = request.form.get("contentx")
    appname = request.form.get("appname")

    newTodo = Todo(title = title,content = content,category = category,contentx = contentx,appname = appname)

    db.session.add(newTodo)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<string:id>")
def deleteTodo(id):
    todo = Todo.query.filter_by(id=id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/detail/<string:id>")
def detailTodo(id):
    todo = Todo.query.filter_by(id=id).first()

    return render_template("detail.html",todo = todo)

@app.route("/update/<int:id>", methods=["POST","GET"])
def updateTodo(id):
    todo = Todo.query.filter_by(id=id).first()
    rule_update = Todo.query.get_or_404(id)
    if request.method == "POST":
        rule_update.title = request.form["title"]
        rule_update.category = request.form["category"]
        rule_update.content= request.form["content"]
        rule_update.contentx = request.form["contentx"]
        rule_update.appname = request.form["appname"]
        rule_update.image = request.form["img"]
        
        db.session.commit()
        return render_template("update.html",todo = todo,rule_update = rule_update)       
    else:
        return render_template("update.html",todo = todo,rule_update = rule_update)

class Todo(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(80),nullable=True)
    content = db.Column(db.Text,nullable=True)
    category = db.Column(db.Text)
    contentx = db.Column(db.Text)
    appname = db.Column(db.Text)

if __name__ == "__main__":
    app.run(debug=True)