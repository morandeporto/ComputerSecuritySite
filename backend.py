from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
users = {
    'eran': {'password': '123', 'internet_package_type': 'premium', 'publish_sectors': ['Technology', 'Science']},
    # Add more users as needed
}


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users.keys() and password == users[username]['password']:
            user_data = users[username]
            return render_template('dashboard.html', internet_package_type=user_data['internet_package_type'],
                                   publish_sectors=user_data['publish_sectors'])

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle registration logic here
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        new_email = request.form.get('email')
        internet_package_type = request.form.get('internet_package_type')
        publish_sectors = request.form.get('publish_sectors')
        users[new_username] = {"password": new_password, "internet_package_type": internet_package_type,
                                 "publish_sectors": publish_sectors}

        # Perform registration logic (e.g., store new user in a database)
        # For simplicity, I'm just printing the values here
        print(
            f"New User: {new_username}, Password: {new_password}, Email: {new_email}, internet_package_type: {internet_package_type}, publish_sectors: {publish_sectors} ")

        # Redirect to the login page after successful registration
        print(users)
        return redirect(url_for('login'))

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
