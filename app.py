from flask import Flask, render_template, session, request, redirect, flash
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp
from flask_session import Session
from helper import login_required
from datetime import datetime
import re

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

@app.route('/')
def index():
    return render_template("index.html")

# rota onde mostrará os eventos pendentes
@app.route("/events")
@login_required
def events():
        db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER NOT NULL,name TEXT NOT NULL, date TEXT NOT NULL, description TEXT NOT NULL, start TEXT NOT NULL, end TEXT NOT NULL)")
        events_rows = db.execute("SELECT * FROM events WHERE id=:id", id=session["user_id"])

        # passa os valores de cada coluna do banco de dado
        return render_template("events.html", events_rows=events_rows)   

# adiciona um evento
@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        # Get what user inputed
        name = request.form.get("name")
        date = request.form.get("date")
        description = request.form.get("description")
        start = request.form.get("start")
        end = request.form.get("end")

        # Put validade in the pattern of date
        valid_date = re.match("[0-9]{2}/[0-9]{2}/[0-9]{4}", date)
        # Validates validade
        if not valid_date:
            flash("Data inválida, use o formato Dia/Mês/Ano. Ex: 22/09/2020")
            return redirect("/add")

        # Define DD/MM/YYYY for date
        day,month,year = date.split("/")
        # Check if user inputed a correct value for day, month or year
        if int(day) > 31 or int(month) > 12 or int(year) > 9999:
            flash("Valor inválido para dia, mês ou ano.")
            return redirect("/add")

        # Check if the valid_date date is a valid date
        isValidDate = True
        try:
            datetime(int(year),int(month),int(day))
        except ValueError:
            isValidDate = False
            if True:
                flash("Data inválida, use o formato Dia/Mês/Ano. Ex: 22/09/2020")
                return redirect("/add")
        if not isValidDate:
            flash("Data de validade inválida, use o formato Dia/Mês/Ano. Ex: 22/09/2020")
            return redirect("/add")
        else:
            # Convert the user input(validade) and convert it into a real date
            final_date = datetime(int(year),int(month),int(day))
            names = db.execute("SELECT name FROM events WHERE id=:id", id=session["user_id"])
            already_name = []
            for i in range(len(names)):
                already_name.append(names[i]["name"])
            # checa se o nome das contas são iguais, adicionando 1,2,3,...,n na frente
            if name in already_name:
                name_counter = 1
                while (name in already_name):
                    name_counter += 1
                    new_name = str(name) + str(name_counter)
                    if new_name in already_name:
                        continue
                    else:
                        name = new_name
                        break
            # insere os valores na tabela
            db.execute("INSERT INTO events (id, name, date, description, start, end) VALUES (:id , :name, :date, :description, :start, :end)",
                        id=session["user_id"],
                        name=name,
                        date=final_date,
                        description=description,
                        start=start,
                        end=end)
            # Redirect user to see the table
            return redirect("/events")

    else:
        # Display add form to the user when he gets to /add
        return render_template("add.html")

# edita um evento
@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "POST":

        # seleciona o nome do evento que o usuário selecionou para editar
        name = request.form.get("name")
        new_name = request.form.get("new_name")
        date = request.form.get("date")
        description = request.form.get("description")
        start = request.form.get("start")
        end = request.form.get("end")

        # remove esse evento da tabela de eventos
        db.execute("UPDATE events SET name=:new_name, date=:date, description=:description, start=:start, end=:end WHERE id=:id AND name=:name",
                    new_name=new_name,
                    date=date,
                    description=description,
                    start=start,
                    end=end,
                    id=session["user_id"],
                    name=name)

        return redirect("/events")
    else:
        events_rows = db.execute("SELECT * FROM events WHERE id=:id", id=session["user_id"])
        return render_template("edit.html", events_rows=events_rows)

# remove um evento
@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    if request.method == "POST":

        # seleciona o nome do evento que o usuário selecionou para remover
        name = request.form.get("name")

        # remove esse evento da tabela de eventos
        db.execute("DELETE FROM events WHERE id=:id AND name=:name",
                    id=session["user_id"],
                    name=name)

        return redirect("/events")
    else:
        events_rows = db.execute("SELECT * FROM events WHERE id=:id", id=session["user_id"])
        return render_template("remove.html", events_rows=events_rows)



"""Log user in"""
@app.route("/login", methods=["GET", "POST"])
def login():
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Você precisa digitar o seu nome de usuário.")
            return redirect("/login")

        # Ensure password was submitted
        if not request.form.get("password"):
            flash("Você precisa digitar a sua senha.")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("invalid username and/or password")
            return redirect('/login')

        # Forget any user_id
        session.clear()

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

"""Log user out"""
@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


"""Register user"""
@app.route("/register", methods=["GET", "POST"])
def register():

    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL)")
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check if the user provided a username
        if not request.form.get("username"):
            flash("Você precisa digitar um nome de usuário.")
            return redirect("/register")

        # Check if the user provided a password
        elif not request.form.get("password"):
            flash("Você precisa digitar uma senha.")
            return redirect("/register")
        # Check if the user confirmed his/her password
        elif not request.form.get("confirmation"):
            flash("Você precisa confirmar sua senha.")
            return redirect("/register")
        # Check if the user passwords match
        elif request.form.get("confirmation") != request.form.get("password"):
            flash("Suas senhas não são iguais.")
            return redirect("/register")

        # Check if username already exist
        exists_username = db.execute("SELECT * FROM users WHERE username= :uname",
                                    uname=request.form.get("username"))

        if exists_username:
            flash("Falha ao registrar: o nome de usuário já existe, escolha outro por favor.")
            return redirect("/register")
        else:
            insert = db.execute("INSERT INTO users (username, hash) VALUES (:username, :password_hash)",
                                  username = request.form.get("username"),
                                  password_hash = generate_password_hash(request.form.get("password")))
        # Set session id to the new user id
        session["user_id"] = insert

        # Redirect user to homepage
        return redirect("/")

    # Open the register form to the user
    else:
        return render_template("register.html")