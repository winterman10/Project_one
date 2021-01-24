from flask import Flask
import simplejson as json
from flask import request
import project_one.src.models as models
import project_one.src.db as db
import pandas as pd
# from flask_jsonpify import jsonpify


def create_app(database='project_one', testing = False, debug = True):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=database,
        DEBUG = debug,
        TESTING = testing
    )

    @app.route('/')
    def root_url():
        return 'Welcome to Schoolsy - always find the best school!'

    @app.route('/schools')
    def schools():
        conn = db.get_db()
        cursor = conn.cursor()
        schools = db.find_all(models.Schools, cursor)
        school_dict = [school.__dict__ for school in schools]
        schools = json.dumps(school_dict, default = str)
        return schools

    @app.route('/schools/<id>')
    def attendance_id(id):
        conn = db.get_db()
        cursor = conn.cursor()
        school_obj = db.find(models.Schools, id, cursor)
        school =  json.dumps(school_obj.__dict__, default = str)
        return school

    return app



app = create_app()
app.run(debug = True)