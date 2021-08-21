from flask import Flask
from flaskr.models import db
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
# db.drop_all(app=app)
db.create_all(app=app)
migrate = Migrate(app, db)
migrate.init_app(app, db, render_as_batch=True)

# set FLASK_APP=flaskr/migrate
# set FLASK_DEV=development
# flask db migrate   (после создания файла миграции - проверить его)
# flask db upgrade
