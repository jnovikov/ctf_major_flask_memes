import datetime
import string
import random

from flask import Flask, render_template, request, make_response, redirect

app = Flask(__name__)

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
    users[login] = password


def get_user_memes(login):
    if memes.get(login) is None:
        return None
    else:
        return memes[login]


def add_memes(login, mem):
    if memes.get(login) is None:
        memes[login] = [mem, ]
    else:
        memes[login].append(mem)


def check_user(login, password):
    password_data = users.get(login)
    if password_data is None:
        return False
    else:
        return password_data == password


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
        ok = check_user(login, password)
        if ok:
            response = make_response(redirect('/'))
            expire_date = datetime.datetime.now()
            expire_date = expire_date + datetime.timedelta(days=90)
            response.set_cookie("sessionid", new_session(login), expires=expire_date)
            return response
        else:
            return "No such user"


@app.route('/add', methods=["POST", "GET"])
def add():
    sessionid = request.cookies.get('sessionid', '')
    if sessionid == '':
        return "Please, login"

    login = get_from_session(sessionid)

    if request.method == "GET":
        return render_template("add.html")
    else:
        mem = request.form.get('mem', '')
        add_memes(login, mem)
        return redirect('/')


@app.route('/memes')
def memes_list():
    sessionid = request.cookies.get('sessionid', '')
    if sessionid == '':
        return "Please, login"

    login = get_from_session(sessionid)
    user_memes = get_user_memes(login)
    if user_memes is None:
        return "Вы еще не добавили мемчиги!"
    else:

        return '<br>'.join(get_user_memes(login))


app.run()
