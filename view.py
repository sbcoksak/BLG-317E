from flask import Flask, flash, current_app, render_template, abort, request, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime
import server

app = Flask(__name__,instance_relative_config=True)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_DATABASE_PORT'] = '3306'
app.config['MYSQL_PASSWORD'] = 'mysqlpw963741'
app.config['MYSQL_DB'] = 'blg'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

def home_page():
    today_s = datetime.today().strftime("%A")
    return render_template("Main_page.html")
    
def projects_page():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM project;")
    projects = cur.fetchall()
    cur.execute("Select project_id, keyword_name from includes inner join keyword on includes.keyword_id = keyword.keyword_id;")
    keyword = cur.fetchall()
    cur.close()
    return render_template("Sec_page.html", projects=projects, keywords=keyword)

def search_page(searchfor):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM project WHERE year = %s OR programming_language = %s OR web_framework = %s OR dbms = %s;",(searchfor, searchfor, searchfor, searchfor))
    projects = cur.fetchall()
    
    cur.execute("SELECT keyword_id FROM keyword WHERE keyword_name = %s;",(searchfor,))
    search_keyword= cur.fetchone()
    
    if search_keyword:
        cur.execute("SELECT * FROM includes RIGHT JOIN project ON includes.project_id = project.project_id WHERE keyword_id = %s;",(search_keyword["keyword_id"],))
        projects_fromkeyword=(cur.fetchall())
    else:
        projects_fromkeyword = ()
    cur.execute("Select project_id, keyword_name from includes inner join keyword on includes.keyword_id = keyword.keyword_id;")
    keyword = cur.fetchall()
    cur.close()
    if projects_fromkeyword:
        return render_template("Sec_page.html", projects=projects, keywords=keyword , projectsfk = projects_fromkeyword)
    else:
        return render_template("Sec_page.html", projects=projects, keywords=keyword)
    
def project_page(project_key):
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM project where project_id = %s;", (project_key,))
        project = cur.fetchone()
        if project is None:
            abort(404)
        
        cur.execute("SELECT keyword.keyword_name FROM keyword join includes on keyword.keyword_id = includes.keyword_id where project_id = %s;", (project_key,))
        keyword_names = cur.fetchall();
        
        cur.execute("SELECT student.generated_student_id,student.student_name FROM student join did on student.generated_student_id = did.generated_student_id where project_id = %s;", (project_key,))
        std_names = cur.fetchall();
           
        cur.execute("SELECT teaching_staff.teaching_staff_id, teaching_staff.teaching_staff_name FROM teaching_staff join supervises on teaching_staff.teaching_staff_id = supervises.teaching_staff_id where project_id = %s;", (project_key,))
        ts_names = cur.fetchall();
        
        cur.close()
        
        return render_template("Project.html", Project=project, Keywords = keyword_names, Students = std_names, Teaching_staff = ts_names)
    else:
        if request.form["Button"] == "Update":
            return redirect(url_for("project_update_page", project_key=project_key))
        else:
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM includes where project_id = (%s);", [project_key])
            cur.execute("DELETE FROM did where project_id = (%s);", [project_key])
            cur.execute("DELETE FROM supervises where project_id = (%s);", [project_key])
            cur.execute("DELETE FROM project where project_id = (%s);", [project_key])
            mysql.connection.commit()
            cur.close()
            return render_template("Main_page.html") 
    
def project_update_page(project_key):
    if request.method == "GET":
        values = {"P_name": "", "year": "", "P_desc": "","progL": "","wf": "","dbms": "","kw": "", "std": "","ts":""}
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM project where project_id = %s;", (project_key,))
        project = cur.fetchone()
        
        if project is None:
            abort(404)
        values["P_name"] = project["project_name"]
        values["year"] = project["year"]
        values["P_desc"] = project["project_description"]
        values["progL"] = project["programming_language"]
        values["wf"] = project["web_framework"]
        values["dbms"] = project["dbms"]
        
        cur.execute("SELECT * FROM includes where project_id = %s;", (project_key,))
        keyword_ids = cur.fetchall()
        for row in keyword_ids:
            cur.execute("SELECT keyword_name FROM keyword WHERE keyword_id = %s;", [row["keyword_id"]])
            new_keyword = cur.fetchone()
            values["kw"] += new_keyword["keyword_name"] + ",";
        values["kw"] = values["kw"][:-1]           
        cur.execute("SELECT * FROM did where project_id = %s;", (project_key,))
        std_ids = cur.fetchall()
        for row in std_ids:
            cur.execute("SELECT student_name FROM student WHERE generated_student_id = %s;", [row["generated_student_id"]])
            new_std = cur.fetchone()
            values["std"] += new_std["student_name"] + ",";
        values["std"] = values["std"][:-1]      
        
        cur.execute("SELECT * FROM supervises where project_id = %s;", (project_key,))
        ts_ids = cur.fetchall()
        for row in ts_ids:
            cur.execute("SELECT teaching_staff_name FROM teaching_staff WHERE teaching_staff_id = %s;", [row["teaching_staff_id"]])
            new_ts = cur.fetchone()
            values["ts"] += new_ts["teaching_staff_name"] + ",";
        values["ts"] = values["ts"][:-1]  
        cur.close()
        
        return render_template("Update_page.html", min_year=1980, max_year=datetime.now().year, values=values)
    else:
        
        form_name = request.form["P_name"]
        form_year = request.form["year"]
        form_year_int = int(form_year)
        form_description = request.form["P_desc"]
        form_pl = request.form["progL"]
        form_wf = request.form["wf"]
        form_dbms = request.form["dbms"]
        form_inkw = request.form["kw"]
        form_instd = request.form["std"]
        form_ints = request.form["ts"]
        
        
        cur = mysql.connection.cursor()
        cur.execute('UPDATE project SET project_name = %s , year = %s, project_description = %s ,programming_language = %s, web_framework = %s, dbms = %s WHERE project_id = %s;', (form_name, form_year_int, form_description, form_pl, form_wf, form_dbms, project_key))
        mysql.connection.commit()
        
        cur.execute("DELETE FROM includes where project_id = (%s);", [project_key])
        if form_inkw:
            form_inkw = form_inkw.casefold()
            form_kw = form_inkw.split(",")
            for key in form_kw:
                cur.execute("Select keyword_id from keyword where keyword_name = (%s);",[key])
                mysql.connection.commit()
                key_exist = cur.fetchone()
                if not key_exist:
                    cur.execute("INSERT INTO keyword(keyword_name) VALUES (%s);", [key])
                    cur.execute("SELECT LAST_INSERT_ID();");
                    key_id = cur.fetchone()["LAST_INSERT_ID()"]
                    cur.execute("INSERT INTO includes(project_id, keyword_id) VALUES (%s,%s);", (project_key, key_id))
                else:
                    key_id = key_exist["keyword_id"]
                    cur.execute("INSERT INTO includes(project_id, keyword_id) VALUES (%s,%s);", (project_key, key_id))
            mysql.connection.commit()
        
        cur.execute("DELETE FROM did where project_id = (%s);", [project_key])
        if form_instd:
            form_instd = form_instd.upper()
            form_std = form_instd.split(",")
            for student in form_std:
                cur.execute("Select generated_student_id from student where student_name = (%s);",[student])
                mysql.connection.commit()
                std_exist = cur.fetchone()
                if not std_exist:
                    cur.execute("INSERT INTO student(student_name) VALUES (%s);", [student])
                    cur.execute("SELECT LAST_INSERT_ID();");
                    std_id = cur.fetchone()["LAST_INSERT_ID()"]
                    cur.execute("INSERT INTO did(project_id, generated_student_id) VALUES (%s,%s);", (project_key, std_id))
                else:
                    std_id = std_exist["generated_student_id"]
                    cur.execute("INSERT INTO did(project_id, generated_student_id) VALUES (%s,%s);", (project_key, std_id))
            mysql.connection.commit()
        
        cur.execute("DELETE FROM supervises where project_id = (%s);", [project_key])
        if form_ints:
            form_ints = form_ints.upper()
            form_ts = form_ints.split(",")
            for ts in form_ts:
                cur.execute("Select teaching_staff_id from teaching_staff where teaching_staff_name = (%s);",[ts])
                mysql.connection.commit()
                ts_exist = cur.fetchone()
                if not ts_exist:
                    cur.execute("INSERT INTO teaching_staff(teaching_staff_name) VALUES (%s);", [ts])
                    cur.execute("SELECT LAST_INSERT_ID();");
                    ts_id = cur.fetchone()["LAST_INSERT_ID()"]
                    cur.execute("INSERT INTO supervises(project_id, teaching_staff_id) VALUES (%s,%s);", (project_key, ts_id))
                else:
                    ts_id = ts_exist["teaching_staff_id"]
                    cur.execute("INSERT INTO supervises(project_id, teaching_staff_id) VALUES (%s,%s);", (project_key, ts_id))
            mysql.connection.commit()
        
        return redirect(url_for("project_page", project_key=project_key))

def addp():
    if request.method == "GET":
        values = {"name": "", "year": "", "P_desc": "","progL": "","wf": "","dbms": "","kw": ""}
        return render_template("addp.html", min_year=1980, max_year=datetime.now().year, values=values)
    else:
        
        form_name = request.form["P_name"]
        form_year = request.form["year"]
        form_year_int = int(form_year)
        form_description = request.form["P_desc"]
        form_pl = request.form["progL"]
        form_wf = request.form["wf"]
        form_dbms = request.form["dbms"]
        form_inkw = request.form["kw"]
        form_instd = request.form["std"]
        form_ints = request.form["ts"]
        
        cur = mysql.connection.cursor()
        
        cur.execute("INSERT INTO project(project_name, year, project_description,programming_language, web_framework, dbms) VALUES (%s, %s, %s, %s,%s,%s);", (form_name, form_year_int, form_description,form_pl,form_wf,form_dbms))
        cur.execute("SELECT project_id FROM project ORDER BY project_id DESC LIMIT 1;")
        mysql.connection.commit()
        project_n = cur.fetchone()
        project_key= project_n["project_id"]
        mysql.connection.commit()
        if form_inkw:
            form_inkw = form_inkw.casefold()
            form_kw = form_inkw.split(",")
            for key in form_kw:
                cur.execute("Select keyword_id from keyword where keyword_name = (%s);",[key])
                mysql.connection.commit()
                key_exist = cur.fetchone()
                if not key_exist:
                    cur.execute("INSERT INTO keyword(keyword_name) VALUES (%s);", [key])
                    cur.execute("SELECT LAST_INSERT_ID();");
                    key_id = cur.fetchone()["LAST_INSERT_ID()"]
                    cur.execute("INSERT INTO includes(project_id, keyword_id) VALUES (%s,%s);", (project_key, key_id))
                else:
                    key_id = key_exist["keyword_id"]
                    cur.execute("INSERT INTO includes(project_id, keyword_id) VALUES (%s,%s);", (project_key, key_id))
            mysql.connection.commit()
        if form_instd:
            form_instd = form_instd.upper()
            form_std = form_instd.split(",")
            for student in form_std:
                cur.execute("Select generated_student_id from student where student_name = (%s);",[student])
                mysql.connection.commit()
                std_exist = cur.fetchone()
                if not std_exist:
                    cur.execute("INSERT INTO student(student_name) VALUES (%s);", [student])
                    cur.execute("SELECT LAST_INSERT_ID();");
                    std_id = cur.fetchone()["LAST_INSERT_ID()"]
                    cur.execute("INSERT INTO did(project_id, generated_student_id) VALUES (%s,%s);", (project_key, std_id))
                else:
                    std_id = std_exist["generated_student_id"]
                    cur.execute("INSERT INTO did(project_id, generated_student_id) VALUES (%s,%s);", (project_key, std_id))
            mysql.connection.commit()
        if form_ints:
            form_ints = form_ints.upper()
            form_ts = form_ints.split(",")
            for ts in form_ts:
                cur.execute("Select teaching_staff_id from teaching_staff where teaching_staff_name = (%s);",[ts])
                mysql.connection.commit()
                ts_exist = cur.fetchone()
                if not ts_exist:
                    cur.execute("INSERT INTO teaching_staff(teaching_staff_name) VALUES (%s);", [ts])
                    cur.execute("SELECT LAST_INSERT_ID();");
                    ts_id = cur.fetchone()["LAST_INSERT_ID()"]
                    cur.execute("INSERT INTO supervises(project_id, teaching_staff_id) VALUES (%s,%s);", (project_key, ts_id))
                else:
                    ts_id = ts_exist["teaching_staff_id"]
                    cur.execute("INSERT INTO supervises(project_id, teaching_staff_id) VALUES (%s,%s);", (project_key, ts_id))
            mysql.connection.commit()
        
        cur.close()
        return redirect(url_for("project_page", project_key=project_key))      
        
def delete_multiple_page():
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM project;")
        projects = cur.fetchall()
        cur.close()
        return render_template("delete_mult.html", projects=projects)
    else:
        form_project_keys = request.form.getlist("project_keys")
        cur = mysql.connection.cursor()
        for form_project_key in form_project_keys:
            id_to_delete = int(form_project_key)
            cur.execute("DELETE FROM includes where project_id = (%s);", [id_to_delete])
            cur.execute("DELETE FROM did where project_id = (%s);", [id_to_delete])
            cur.execute("DELETE FROM supervises where project_id = (%s);", [id_to_delete])
            cur.execute("DELETE FROM project where project_id = (%s);", [id_to_delete])
            mysql.connection.commit()
        cur.close()
        return redirect(url_for("delete_multiple_page"))

def student_page(student_id):
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM student where generated_student_id = %s;", (student_id,))
        student = cur.fetchone()
        if student is None:
            abort(404) 
        cur.execute("SELECT project.project_id,project.project_name FROM project join did on project.project_id = did.project_id where generated_student_id = %s;", (student_id,))
        projects = cur.fetchall()
        return render_template("Student_page.html", Student = student, Projects = projects)
        
    else:
        if request.form["Button"] == "Update":
            return redirect(url_for("std_update", std_id=student_id))
        elif request.form["Button"] == "Delete":
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM did where generated_student_id = (%s);", [student_id])
            cur.execute("DELETE FROM student where generated_student_id = (%s);", [student_id])
            mysql.connection.commit()
            cur.close()
            return render_template("Main_page.html")
        else:
            
            return render_template("Main_page.html")
            
def ts_page(ts_id):
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM teaching_staff where teaching_staff_id = %s;", (ts_id,))
        ts = cur.fetchone()
        if ts is None:
            abort(404) 
        cur.execute("SELECT project.project_id,project.project_name FROM project join supervises on project.project_id = supervises.project_id where teaching_staff_id = %s;", (ts_id,))
        projects = cur.fetchall()
        cur.close()
        return render_template("Ts_page.html", Ts = ts, Projects = projects)
        
    else:
        if request.form["Button"] == "Update":
            return redirect(url_for("ts_update", ts_id=ts_id))
        elif request.form["Button"] == "Delete":
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM supervises where teaching_staff_id = (%s);", [ts_id])
            cur.execute("DELETE FROM teaching_staff where teaching_staff_id = (%s);", [ts_id])
            mysql.connection.commit()
            cur.close()
            return render_template("Main_page.html")
        else:
            
            return render_template("Main_page.html")            

def addu():
    if request.method == "GET":
        values = {"name": "", "ima": "", "un": "","pw": "", "isn": ""}
        return render_template("addu.html", values=values)
    else:
        form_name = request.form["name"]
        form_ima = request.form["ima"]
        form_un = request.form["un"]
        form_pw = request.form["pw"]    # REMEMBER TO HASH IT !!!!!!!!!!!!!!!!!!!!!!!
        form_isn = request.form["isi"]    
        if "@itu.edu.tr" not in form_ima:
            return render_template("addu.html", values=request.form)
        else:
        
            if request.form["member_type"] == "std":    #check radiobox here
                cur = mysql.connection.cursor()
                if form_isn:
                    cur.execute("INSERT INTO student(student_name, itu_mail_address , user_name , user_password, itu_student_id) VALUES (%s, %s, %s, %s, %s);",(form_name, form_ima, form_un,form_pw, form_isn))
                else:
                    cur.execute("INSERT INTO student(student_name, itu_mail_address , user_name , user_password) VALUES (%s, %s, %s, %s);",(form_name, form_ima, form_un,form_pw))
                cur.execute("SELECT * FROM student where generated_student_id=(SELECT LAST_INSERT_ID());");
                mysql.connection.commit()
                cur.execute("SELECT LAST_INSERT_ID();");
                newstd_id = cur.fetchone()["LAST_INSERT_ID()"]
                cur.close()
                return redirect(url_for("student_page",student_id=newstd_id))
            else:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO teaching_staff(teaching_staff_name, itu_mail_address , user_name , user_password) VALUES (%s, %s, %s, %s);",(form_name, form_ima, form_un,form_pw))
                mysql.connection.commit()
                cur.execute("SELECT LAST_INSERT_ID();");
                newts_id = cur.fetchone()["LAST_INSERT_ID()"]
                cur.close()
                return redirect(url_for('ts_page', ts_id=newts_id))    

def std_update(std_id):
    if request.method == "GET":
        values = {"name": "", "ima": "", "un": "","pw": "", "isi": ""}
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM student where generated_student_id = %s;", (std_id,))
        student = cur.fetchone()
        
        values["name"] = student["student_name"]
        if student["itu_mail_address"]:
            values["ima"] = student["itu_mail_address"]
        if student["user_name"]:
            values["un"] = student["user_name"]
        if student["user_password"]:
            values["pw"] = student["user_password"]
        if student["itu_student_id"]:
            values["isi"] = student["itu_student_id"] 
        return render_template("updatestd.html", values=values)
        
    else:
        form_name = request.form["name"]
        form_ima = request.form["ima"]
        form_un = request.form["un"]
        form_pw = request.form["pw"]    
        form_isi = request.form["isi"]    
        if "@itu.edu.tr" not in form_ima:
            return render_template("updatestd.html", values=request.form)
        else:
            cur = mysql.connection.cursor()
            if form_isi:
                cur.execute('UPDATE student SET student_name = %s, itu_mail_address = %s , user_name = %s , user_password = %s, itu_student_id = %s WHERE generated_student_id = %s;',(form_name, form_ima, form_un,form_pw, form_isi, std_id))
            else:
                cur.execute('UPDATE student SET student_name = %s, itu_mail_address = %s , user_name = %s , user_password = %s, itu_student_id = "" WHERE generated_student_id = %s;',(form_name, form_ima, form_un,form_pw, std_id))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for("student_page",student_id=std_id))

def ts_update(ts_id):
    if request.method == "GET":
        values = {"name": "", "ima": "", "un": "","pw": ""}
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM teaching_staff where teaching_staff_id = %s;", (ts_id,))
        ts = cur.fetchone()
        
        values["name"] = ts["teaching_staff_name"]
        if ts["itu_mail_address"]:
            values["ima"] = ts["itu_mail_address"]
        if ts["user_name"]:
            values["un"] = ts["user_name"]
        if ts["user_password"]:
            values["pw"] = ts["user_password"]
        return render_template("updatets.html", values=values)
        
    else:
        form_name = request.form["name"]
        form_ima = request.form["ima"]
        form_un = request.form["un"]
        form_pw = request.form["pw"]      
        if "@itu.edu.tr" not in form_ima:
            return render_template("updatets.html", values=request.form)
        else:
            cur = mysql.connection.cursor()
            cur.execute('UPDATE teaching_staff SET teaching_staff_name = %s, itu_mail_address = %s , user_name = %s , user_password = %s WHERE teaching_staff_id = %s;',(form_name, form_ima, form_un,form_pw, ts_id))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for("ts_page",ts_id=ts_id))
            
def user_list():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student;")
    students = cur.fetchall()
    cur.execute("SELECT * FROM teaching_staff;")
    tss = cur.fetchall()
    cur.close()
    return render_template("Userlist.html", students=students, tss=tss)