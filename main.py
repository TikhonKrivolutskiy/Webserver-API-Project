from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from db import db
from datetime import datetime, timedelta
from random import randint
import re

app = Flask(__name__)
all_orders = []

app.config.update(SECRET_KEY = 'WOW SUCH SECRET')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(login):
    return User(login)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        row = db.users.get('login', request.form['login'])
        if not row:
            return render_template('login.html', error='Неправильный логин или пароль')
        if request.form['password'] == row.password:
            user = User(login) 
            login_user(user) 
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неправильный логин или пароль')
    return render_template('login.html')


@app.route('/products/', methods=['GET', 'POST'])
@login_required
def products():
    data = db.items.get_all()
    if request.method == 'POST':
        row = db.cart.get("item_id", request.form["item_id"])
        if not row:
            data1 = {"item_id":request.form["item_id"],
                    "amount":"1"}
            db.cart.put(data1)
        else:
            data1 = {"item_id":request.form["item_id"],
                     "amount": row.amount + 1}
            db.cart.delete('item_id', request.form['item_id'])
            db.cart.put(data1)
    data = db.items.get_all()
    for row in data:
        res = db.cart.get('item_id', row.id)
        if res:
            row.amount = res.amount
        else:
            row.amount = 0
    return render_template('products.html', data=data)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        return redirect(url_for('order'))
    data = db.cart.get_all()
    total_sum = 0
    for row in data:
        item_row = db.items.get('id', row.item_id)
        row.name = item_row.name
        row.description = item_row.description
        row.price = item_row.price
        row.total = row.amount * item_row.price
        total_sum += row.total
    return render_template('cart.html', data=data, total_sum=total_sum)


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    if request.method == 'POST':
        for key in request.form:
            if request.form[key] == '':
                return render_template('order.html', error='Не все поля заполнены!')
            if key == 'email':
                if not re.match('\w+@\w+\.(ru|com)', request.form[key]):
                    return render_template('order.html', error='Неправильный формат почты')
            if key == 'phone_number':
                if not re.match('\+7\d{9}', request.form[key]):
                    return render_template('order.html', error='Неправильный формат номера телефона')
                
        
        cart_data = db.cart.get_all()
        order_data = db.orders.get_all()

        id_ = order_data[-1].id + 1 if order_data else 1
        for row in cart_data:
            item = {'id': id_, 'item_id': row.item_id, 'amount': row.amount}
            db.orders.put(item)

        for row in cart_data:
            db.cart.delete('item_id', row.item_id)

        payload = dict(request.form)
        payload['order_id'] = id_
        all_orders.append(payload)
        return redirect(url_for('cart'))

    return render_template('order.html')


@app.route('/api/orders')
def api_orders():
    return jsonify(all_orders)


@app.route('/order_list')
@login_required
def order_list():
    return render_template('order_list.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template('login.html', error="Вы успешно вышли из аккаунта")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        for key in request.form:
            if request.form[key] == '':
                return render_template('register.html', error='Все поля должны быть заполнены!')
        row = db.users.get("login", request.form["login"])
        if row:
            return render_template("register.html", error="Такой пользователь уже существует")
        row = db.users.get("email", request.form["email"])
        if row:
            return render_template("register.html", error="Такой email уже используется")
        row = db.users.get("phone_number", request.form["phone_number"])
        if row:
            return render_template("register.html", error="Такой номер телефона уже используется")
        if request.form['password'] != request.form['password_check']:
            return render_template('register.html', error='Пароли не совпадают')
        data = dict(request.form)
        data.pop('password_check')
        db.users.put(data=data)
        return render_template('register.html', error='Регистрация прошла успешно')
    return render_template('register.html')


if __name__ == "__main__":
    app.run()