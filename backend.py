from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import pymssql
import os

app = Flask(__name__)
app.secret_key = os.environ['MSSQL_SA_PASSWORD']
password = os.environ['MSSQL_SA_PASSWORD']
conn = pymssql.connect("127.0.0.1", "sa", password, "CommunicationLTD")
cursor = conn.cursor(as_dict=True)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with conn.cursor(as_dict=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user_data = cursor.fetchone()
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
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute("SELECT sector_name FROM sectors")
        sectors = cursor.fetchall()
        sectors = [sector['sector_name'] for sector in sectors]

    if request.method == 'POST':
        # Handle registration logic here
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        new_email = request.form.get('email')
        internet_package_type = request.form.get('internet_package_type')
        publish_sectors = request.form.getlist('publish_sectors')
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (new_username))
            user_data = cursor.fetchone()

            if user_data:
                flash('Username already exists')
                return redirect(url_for('register'))
            else:
                cursor.execute("INSERT INTO users (username, password, email, package_id) VALUES (%s, %s, %s, %s)",
                               (new_username, new_password, new_email, internet_package_type))
                cursor.execute("SELECT user_id FROM users WHERE username = %s", (new_username))
                user_id = cursor.fetchone()['user_id']
                for sector in publish_sectors:
                    cursor.execute("SELECT sector_id FROM sectors WHERE sector_name = %s", (sector))
                    sector_id = cursor.fetchone()['sector_id']
                    cursor.execute("INSERT INTO user_sectors (user_id, sector_id) VALUES (%s, %s)",
                                   (user_id, sector_id))
                conn.commit()
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


if __name__ == '__main__':
    app.run(debug=True)
