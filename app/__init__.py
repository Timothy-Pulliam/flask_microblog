from flask import Flask
from config import DevConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(DevConfig)
login = LoginManager(app)
# redirect users to login view if they are not logged in
login.login_view = 'login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import routes, models, errors
