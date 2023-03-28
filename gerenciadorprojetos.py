# importação de dependencias
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import generate_password_hash, Bcrypt
from flask_qrcode import QRcode
from flask_googlemaps import GoogleMaps

from chaveGoogle import API_KEY


# definição de chave
app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

qrcode = QRcode(app)

# you can set key as config
app.config['GOOGLEMAPS_KEY'] = API_KEY


# Initialize the extension
GoogleMaps(app)

from views import *

if __name__ == '__main__':
    app.run(host='192.168.31.69', debug=True)
    #app.run(debug=True)