import datetime
import sqlite3
import string
import random

from flask import Flask, render_template, request, make_response, redirect, session, g

app = Flask(__name__)
app.secret_key = "aj.bshdm12 3,nm,z .xxcjklb3lrbn1234l.1ibvloiujzkxl,/c li  2hv3bli1`jkm2 3li`u1j23n"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("db.db")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.before_first_request
def init_db():
    create_users = "CREATE TABLE IF NOT EXISTS users " \
                   "(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, " \
                   "login VARCHAR(200) UNIQUE, password VARCHAR(200))"

    create_memes = "CREATE TABLE IF NOT EXISTS memes " \
                   "(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT," \
                   "text VARCHAR(500), user_id INTEGER NOT NULL)"
    db = get_db()
    db.cursor().execute(create_memes)
    db.cursor().execute(create_users)
    db.commit()


users = dict()
memes = dict()


def random_string(n):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(n)])


def get_from_session(sessionid):
    filename = sessionid
    f = open('sessions/' + filename, 'r')
    data = f.read()
    f.close()
    return data


def new_session(data):
    filename = random_string(10)
    f = open('sessions/' + filename, 'w')
    f.write(data)
    f.close()
    return filename


def new_user(login, password):
    new_user = "INSERT INTO users (login,password) VALUES ('{}','{}')".format(login, password)
    db = get_db()
    db.cursor().execute(new_user)
    db.commit()


def get_user_memes(id):
    memes = "SELECT * FROM memes WHERE user_id = {}".format(id)
    print(memes)
    c = get_db().cursor()
    c.execute(memes)
    memes = c.fetchall()
    if memes:
        return [x[1] for x in memes]
    return None


def add_memes(id, mem):
    memes = "INSERT INTO memes (text, user_id) VALUES ('{}',{})".format(mem, id)
    db = get_db()
    db.cursor().execute(memes)
    db.commit()



def check_user(login, password):
    find_user = "SELECT * FROM users WHERE login = '{}' and password = '{}'".format(login, password)
    db = get_db().cursor()
    db.execute(find_user)
    res = db.fetchone()
    if res is None:
        return None
    else:
        return res[0]


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        login = request.form.get("login", "")
        password = request.form.get('password', '')
        if login == '' or password == '':
            return "Please vvedi vse"
        new_user(login, password)
        return redirect('/login')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        login = request.form.get("login", "")
        password = request.form.get('password', '')
        u_id = check_user(login, password)
        if u_id:
            response = make_response(redirect('/'))
            # expire_date = datetime.datetime.now()
            # expire_date = expire_date + datetime.timedelta(days=90)
            # response.set_cookie("sessionid", new_session(login), expires=expire_date)
            session['id'] = u_id
            return response
        else:
            return "No such user"


@app.route('/add', methods=["POST", "GET"])
def add():
    # sessionid = request.cookies.get('sessionid', '')
    # if sessionid == '':
    #     return "Please, login"

    # login = get_from_session(sessionid)
    u_id = session.get('id', '')
    if request.method == "GET":
        return render_template("add.html")
    else:
        mem = request.form.get('mem', '')
        add_memes(u_id, mem)
        return redirect('/')


@app.route('/memes')
def memes_list():
    # sessionid = request.cookies.get('sessionid', '')
    # if sessionid == '':
        # return "Please, login"

    # u_id = get_from_session(sessionid)
    u_id = session.get('id', '')
    user_memes = get_user_memes(u_id)
    if user_memes is None:
        return "Вы еще не добавили мемчиги!"
    else:

        return '<br>'.join(get_user_memes(u_id))


app.run()
