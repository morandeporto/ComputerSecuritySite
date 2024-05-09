from flask import Flask
from dotenv import load_dotenv
import os
import json

from password_strength import PasswordPolicy


def app_configuration(app: Flask):
    load_dotenv()
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'compsec2024@gmail.com'
    app.config['MAIL_PASSWORD'] = '***REMOVED***'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.secret_key = os.getenv('MSSQL_SA_PASSWORD')
    return app


def get_password_policy():
    file = open("password_config.json")
    password_config = json.load(file)
    policy = PasswordPolicy.from_names(
        length=password_config["password_len"],  # min length: 10
        uppercase=password_config["uppercase"],  # need min. 1 uppercase letters
        numbers=password_config["numbers"],  # need min. 1 digits
        special=password_config["special_char"],  # need min. 1 special characters
        nonletters=password_config["nonletters"]  # need min. 1 non-letter characters (digits, specials, anything)
    )
    return policy
