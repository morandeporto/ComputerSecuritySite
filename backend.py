import hashlib
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
        user_data = get_user_data_from_db(username=username, password=password)
        if user_data:
            username = user_data["username"].upper()
            internet_package_type = user_data["package_id"]
            response = make_response(
                render_template('dashboard.html', username=username, internet_package_type=internet_package_type))
            response.set_cookie('username', username)
            response.set_cookie('internet_package_type', str(internet_package_type))
            return response
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
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
            insert_new_user_to_db(new_username, new_password, new_email, internet_package_type)
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
    return render_template('set_new_pwd.html')


@app.route("/<string:token>", methods=["GET", "POST"])
def password_change(token):
    hashed_token = hashlib.sha1(token.encode('utf-8')).digest()
    if PasswordReset.query.filter_by(hash_code=hashed_token).first():
        if request.method == 'POST':
            flash('Post method', 'error')
            return render_template('password_reset.html')

        else:
            flash('Get method', 'success')
            return render_template('set_new_pwd.html')



    else:
        flash('the code was not valid', 'error')
        return render_template('password_reset.html')

@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    if request.method == 'POST':
        user_email = request.form["email"]
        if check_if_user_exists_using_email(email=user_email):
            random_string = (''.join(random.choices(string.ascii_uppercase + string.digits, k=20)))
            hash_code = hashlib.sha1(random_string.encode('utf-8')).digest()
            pwd_reset_obj = PasswordReset(user_email, hash_code) #todo: how to write it?
            db.session.add(pwd_reset_obj)
            db.session.commit()
            send_email(mail=mail, recipient=user_email, hash_code=random_string)
            flash('an email was sent', 'error')
            return redirect(url_for('password_reset'))
        else:
            flash('the user does not exists', 'error')
            return redirect(url_for('password_reset'))
    else:
        return render_template('password_reset.html')


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    return render_template('change_password.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
