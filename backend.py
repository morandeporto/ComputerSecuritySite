import hashlib
import json
import string

from flask import Flask, render_template, request, redirect, url_for, make_response, session
from common_functions import *
from app_configuration import app_configuration
from flask_mail import Mail
import random

app = Flask(__name__)
app = app_configuration(app)
mail = Mail(app)


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_data = get_user_data_from_db(username=username)
        if user_data is None:
            flash('User does not exist')
            return redirect(url_for('login'))

        salt_bytes = bytes.fromhex(get_user_salt(user_id=user_data['user_id']))
        login_hashed_pwd = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt_bytes, 100000)
        user_hashed_password = bytes.fromhex(user_data['password'])

        if user_hashed_password == login_hashed_pwd:
            session['username'] = username
            session['user_id'] = user_data['user_id']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    return render_template(
        'login.html',
        user_added=request.args.get('user_added'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    _, salt_len = get_password_policy()
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        if not validate_password(new_password):
            return redirect(url_for('register'))
        new_email = request.form.get('email')
        publish_sectors = request.form.getlist('publish_sectors[]')

        user_data = get_user_data_from_db(username=new_username)
        if user_data:
            flash('Username already exists')
            return redirect(url_for('register'))

        user_salt = os.urandom(salt_len)
        new_password_hashed = hashlib.pbkdf2_hmac(
            'sha256', new_password.encode('utf-8'),
            user_salt, 100000)  # save in bytes
        insert_new_user_to_db(
            new_username,
            new_password_hashed.hex(),
            new_email,
            user_salt.hex())
        user_id = get_user_data_from_db(username=new_username)['user_id']
        insert_user_sectors_selected_to_db(publish_sectors, user_id)
        session['username'] = new_username
        session['user_id'] = user_id
        return redirect(url_for('login', user_added="user added"))

    sectors = get_all_sectors_names_from_db()
    return render_template('register.html', sectors=sectors)


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    clientid = request.args.get('clientid')
    if clientid:  # if new client added
        client_data = get_client_data(clientid)
        return render_template(
            'dashboard.html',
            username=username,
            client_data=client_data)
    return render_template('dashboard.html', username=username)


@app.route('/add_new_client', methods=['GET', 'POST'])
def add_new_client():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        fields = [
            'sector_id',
            'package_id',
            'ssn',
            'first_name',
            'last_name',
            'email',
            'phone_number']
        client_data = {field: request.form.get(field) for field in fields}
        client_data['representative_id'] = session['user_id']
        client_id = insert_new_client(client_data)
        return redirect(url_for('dashboard', clientid=client_id))

    sectors = get_user_sectors(session['user_id'])
    return render_template('add_new_client.html', sectors=sectors)


@app.route('/set_new_pwd', methods=['GET', 'POST'])
def set_new_pwd():
    if request.method == "POST":
        user_data = session.get('user_data')
        if user_data:
            user_email = user_data["email"]
            new_password = request.form.get('new_pwd')
            if not validate_password(new_password):
                return redirect(url_for('set_new_pwd', _method='GET'))

            if change_user_password_in_db(user_email, new_password):
                flash("ENTERED HERE!!")
                return render_template('login.html', password_changed=True)
        else:
            flash("No user data!")
            return render_template('set_new_pwd.html')

    # todo: Need to change the user password
    return render_template('set_new_pwd.html')


@app.route("/password_change/<string:token>", methods=["GET", "POST"])
def password_change(token):
    if request.method == "GET":
        try:
            with conn.cursor(as_dict=True) as cursor:
                hashed_token = hashlib.sha1(
                    token.encode('utf-8')).digest().hex()
                flash(f'hashed_token= {hashed_token}', 'info')
                cursor.execute(
                    '''SELECT * FROM users WHERE reset_token = %s''',
                    (hashed_token,))
                user_data = cursor.fetchone()
                session['user_data'] = user_data
                print("GOING to set_new_pws")
                return redirect(url_for('set_new_pwd'))
        except BaseException:
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
            random_string = ''.join(
                random.choices(
                    string.ascii_uppercase +
                    string.digits,
                    k=20))
            hash_code = hashlib.sha1(
                random_string.encode('utf-8')).digest().hex()

            # Insert password reset info into the database
            insert_password_reset(user_email, hash_code)
            # Send email with the random string (randomly generated token)
            send_email(
                mail=mail,
                recipient=user_email,
                hash_code=random_string)

            flash('An email was sent check your mail inbox', 'info')
            return redirect(url_for('password_reset'))
        else:
            flash('The user does not exist', 'error')
            return redirect(url_for('password_reset'))
    else:
        return render_template('password_reset.html')


@app.route('/change_password', methods=['GET', 'POST'])
def change_user_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']

        try:
            change_user_password(email, new_password)
            return "Password changed successfully!"
        except ValueError as e:
            # Return error message to user if the new password matches previous
            # passwords
            return str(e)
    else:
        return render_template('change_password.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
