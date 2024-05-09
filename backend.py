import hashlib
import json
import string

from flask import Flask, render_template, request, redirect, url_for, make_response
from common_functions import *
from app_configuration import app_configuration
from flask_mail import Mail
import random

app = Flask(__name__)
app = app_configuration(app)
mail = Mail(app)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_data = get_user_by_username(username)
        if user_data:
            user_hashed_password = bytes.fromhex(user_data['password'])
            salt_bytes = bytes.fromhex(user_data['salt'])
            login_hashed_pwd = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_bytes, 100000)
            if user_hashed_password == login_hashed_pwd:
                username = username.upper()
                internet_package_type = user_data["package_id"]
                response = make_response(
                    render_template('dashboard.html', username=username, internet_package_type=internet_package_type))
                response.set_cookie('username', username)
                response.set_cookie('internet_package_type', str(internet_package_type))
                return response
            else:
                flash('Invalid username or password')
                return redirect(url_for('login'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    _, salt_len = get_password_policy()
    sectors = get_all_sectors_names_from_db()
    if request.method == 'POST':
        # Handle registration logic here
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        new_email = request.form.get('email')
        internet_package_type = request.form.get('internet_package_type')
        publish_sectors = request.form.getlist('publish_sectors')
        user_data = get_user_data_from_db(username=new_username)
        if user_data:
            flash('Username already exists')
            return redirect(url_for('register'))
        else:
            user_salt = os.urandom(salt_len)
            new_password_hashed = hashlib.pbkdf2_hmac('sha256', new_password.encode('utf-8'), user_salt,
                                                      100000)  # save in bytes
            insert_new_user_to_db(new_username, new_password_hashed.hex(), new_email, internet_package_type,
                                  user_salt.hex())
            user_id = get_user_data_from_db(username=new_username)['user_id']
            insert_user_sectors_selected_to_db(publish_sectors, user_id)
            return render_template('login.html', user_added="user added")

    return render_template('register.html', sectors=sectors)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    username = request.cookies.get('username')
    internet_package_type = request.cookies.get('internet_package_type')
    # Render the dashboard.html template
    if request.method == 'POST':
        return redirect(url_for('add_new_client'))
    clientname = request.args.get('clientname')
    if clientname:  # if new client added
        clientname = request.args.get('clientname')
        return render_template('dashboard.html', username=username, clientname=clientname,
                               internet_package_type=internet_package_type)
    return render_template('dashboard.html', username=username)


@app.route('/add_new_client', methods=['GET', 'POST'])
def add_new_client():
    username = request.cookies.get('username')
    internet_package_type = request.cookies.get('internet_package_type')
    if request.method == 'POST':
        return render_template('dashboard.html', username=username, internet_package_type=internet_package_type)

    return render_template('add_new_client.html')


@app.route('/set_new_pwd')
def set_new_pwd():
    if request.method == "POST":
        user_data = request.args.get('user_data')
        flash(f'user_data= {user_data}', 'info')
        if user_data:
            flash(f'user_data= {user_data}', 'info')
            user_data = json.loads(user_data)
            user_salt = bytes.fromhex(user_data["salt"])
            user_email = user_data["email"]
            new_password = request.form.get('new_pwd')
            new_password_hashed = hashlib.pbkdf2_hmac('sha256', new_password.encode('utf-8'), user_salt,
                                                   100000)  # save in bytes
            change_user_password(user_email, new_password_hashed.hex())
            return render_template('login.html', password_changed=True)
    # todo: Need to change the user password
    return render_template('set_new_pwd.html')


@app.route("/<string:token>", methods=["GET", "POST"])
def password_change(token):
    if request.method == "GET":
        try:
            with conn.cursor(as_dict=True) as cursor:
                hashed_token = hashlib.sha1(token.encode('utf-8')).digest().hex()
                flash(f'hashed_token= {hashed_token}', 'info')
                cursor.execute('''SELECT * FROM PasswordReset WHERE hash_code = %s''', (hashed_token,))
                got_data = cursor.fetchone()
                flash('Get method', 'success')
                return render_template('set_new_pwd.html', user_data=got_data)
        except:
            flash('The code was not valid', 'error')
            return render_template('password_reset.html')

    else:
        flash('The code was not valid', 'error')
        return render_template('password_reset.html')


@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    if request.method == 'POST':
        user_email = request.form["email"]
        if check_if_user_exists_using_email(email=user_email):
            random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
            hash_code = hashlib.sha1(random_string.encode('utf-8')).digest()

            # Insert password reset info into the database
            insert_password_reset(user_email, hash_code.hex())
            # Send email with the random string (randomly generated token)
            send_email(mail=mail, recipient=user_email, hash_code=random_string)

            flash('An email was sent check your mail inbox', 'info')
            return redirect(url_for('password_reset'))
        else:
            flash('The user does not exist', 'error')
            return redirect(url_for('password_reset'))
    else:
        return render_template('password_reset.html')


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    return render_template('change_password.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
