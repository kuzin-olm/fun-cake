from flaskr.settings import SECRET_KEY, SQLALCHEMY_DATABASE_URI

from flaskr.models import db
from flask import Flask, render_template

from flaskr.admin import admin

app = Flask(__name__)   # , instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY=SECRET_KEY,
    SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI,      # os.path.join(app.instance_path, 'test.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    FLASK_ADMIN_SWATCH="flatly"
)
db.init_app(app)
admin.init_app(app)
# db.drop_all(app=app)
db.create_all(app=app)


from flaskr import blog, auth, ingredient, template_group_layer
app.register_blueprint(auth.bp)
app.register_blueprint(blog.bp)
app.register_blueprint(ingredient.bp)
app.register_blueprint(template_group_layer.bp)


@app.route('/')
def home():
    return render_template('home_landing.html')


app.add_url_rule('/', endpoint='home')


if __name__ == '__main__':
    app.run(port=5000, debug=True, threaded=True)
