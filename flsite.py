import os
import sqlite3

from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g, make_response, \
    current_app
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from FDataBase import FDataBase
from UserLogin import UserLogin
from admin.admin import admin
from alchemy.alchemy import alchemy
from forms import LoginForm, RegisterForm

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)

app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(alchemy, url_prefix='/alchemy')


# app.config['SQLALCHEMY_BINDS'] = {
#     'db': 'sqlite:////path/to/flsite.db',
#     'db_alchemy': 'sqlite:////path/to/blog.db'
# }

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////path/to/db_alchemy.db'
# app.config['SQLALCHEMY_BINDS'] = {
#     'database2': 'sqlite:////path/to/database2.db'
# }


login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


# menu = [{'name': 'Settings', 'url': 'install-flask'},
#         {'name': 'First App', 'url': 'first-app'},
#         {'name': 'Contacts', 'url': 'contact'},
#         ]

@login_manager.user_loader
def load_user(user_id):
    # print("load_user")
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)

    username = session.get('_user_id')
    # print(111, current_user.get_id())
    # print(222, username)
    try:
        username = dbase.getUser(username)['name']
    except:
        username = 'unknown'
    g.username = username


@app.route("/")
def index():
    content = render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce(), username=g.username)
    # print(111, make_response(content).__dict__)
    return content


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи", username=g.username)


@app.route("/post/<alias>")
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


# @app.route('/index')
# def index():
#     return render_template('index.html', title='Flask', menu=menu)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('success', category='success')
        else:
            flash('error message', category='error')

    return render_template('contact.html', title='Flask', menu=dbase.getMenu())


# @app.route('/profile/<path:username>/<path>')
# def profile(username, path):
#     return f'profile {username}, {path} '


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title="Профиль")


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='not found', menu=dbase.getMenu()), 404


# with app.test_request_context():
#     print(url_for('index'))
#     print(url_for('profile', username='111', path='profile'))


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()

    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)

        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)

            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(form.name.data, form.email.data, hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация", form=form)


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(debug=True)
