from flask import Flask, render_template
from datetime import datetime
import view
from flask_mysqldb import MySQL

app = Flask(__name__,instance_relative_config=True)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_DATABASE_PORT'] = '3306'
app.config['MYSQL_PASSWORD'] = 'mysqlpw963741'
app.config['MYSQL_DB'] = 'blg'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


def create_app(): 
    app.add_url_rule("/", view_func=view.home_page)
    app.add_url_rule("/projects", view_func=view.projects_page)
    app.add_url_rule("/users", view_func=view.user_list)
    app.add_url_rule("/delete", view_func=view.delete_multiple_page, methods=["GET", "POST"])
    app.add_url_rule("/addP", view_func=view.addp, methods=["GET", "POST"])
    app.add_url_rule("/project/<int:project_key>", view_func=view.project_page, methods=["GET", "POST"])
    app.add_url_rule("/student/<int:student_id>", view_func=view.student_page, methods=["GET", "POST"])
    app.add_url_rule("/teaching_staff/<int:ts_id>", view_func=view.ts_page, methods=["GET", "POST"])
    app.add_url_rule("/addU", view_func=view.addu, methods=["GET", "POST"])
    app.add_url_rule("/update/<int:project_key>", view_func=view.project_update_page, methods=["GET", "POST"] )
    app.add_url_rule("/stdupdate/<int:std_id>", view_func=view.std_update, methods=["GET", "POST"] )
    app.add_url_rule("/tsupdate/<int:ts_id>", view_func=view.ts_update, methods=["GET", "POST"] )
    app.add_url_rule("/search/<string:searchfor>", view_func=view.search_page)
    app.config.from_object("settings")   
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080)    
