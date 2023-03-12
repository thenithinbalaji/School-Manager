import pymongo, os
from flask import Flask, flash, redirect, render_template, request, url_for, session
import datetime
from studentdata import studentdata
from authdata import authdata
from schooldata import schooldata
import re

############################################################################

app = Flask(__name__)
app.config["SECRET_KEY"] = "poshan tracker gov"
database_name = "poshanapp"  # make sure another db in same name doesn't exist, change this name to your custom one
mongo_uri = "mongodb://localhost:27017"
############################################################################

### Database creation ######################################################
myclient = pymongo.MongoClient(mongo_uri)
dblist = myclient.list_database_names()

if database_name in dblist:
    print(f"The '{database_name}' database exists")
else:
    mydb = myclient[database_name]

    auth = mydb["auth"]
    data = authdata
    auth.insert_many(data)

    school = mydb["school"]
    data = schooldata
    school.insert_many(data)

    student = mydb["student"]
    data = studentdata
    student.insert_many(data)

    print(f"Database named {database_name} has been created in localhost")

############################################################################


@app.route("/")
def home():
    return render_template(
        "home.html",
        schoolcount=myclient[database_name]["school"].count_documents({}),
        studentcount=myclient[database_name]["student"].count_documents({}),
    )


@app.errorhandler(404)
def not_found_error(error):
    return redirect(url_for("home"))


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        client = pymongo.MongoClient(mongo_uri)[database_name]["auth"]

        # auth contains the collection that matches the mail id submitted in form
        auth = client.find_one({"email": email})

        # checking if password matches the db
        if auth != None:  # making sure collection is not None
            pbool = auth["password"] == password

        if auth == None:
            flash("imail", category="error")  # invalid mail
        elif pbool == False:
            flash("ipass", category="error")  # invalid password
        else:
            # login success
            if auth["type"] == "admin":
                session["admin"] = True
                print("Session Cookie = ", session)
                return redirect(url_for("admin"))

            elif auth["type"] == "student" or auth["type"] == "parent":
                session["student"] = auth["poshanid"]
                print("Session Cookie = ", session)
                return redirect(url_for("student"))

            elif auth["type"] == "school":
                session["school"] = auth["poshanid"]
                print("Session Cookie = ", session)
                return redirect(url_for("school"))

        # rendering the same page (login page) if auth fails
        return render_template("login.html")
    else:
        if "admin" in session:
            return redirect(url_for("admin"))
        elif "school" in session:
            return redirect(url_for("school"))
        elif "student" in session:
            return redirect(url_for("student"))
        else:
            return render_template("login.html")


@app.route("/school", methods=["POST", "GET"])
def school():
    if "school" in session:
        data = pymongo.MongoClient(mongo_uri)[database_name]["school"].find_one(
            {"poshanid": session["school"]}
        )
        return render_template("school.html", data=data)
    else:
        return redirect(url_for("login"))


@app.route("/school/attendance", methods=["POST", "GET"])
def attendance():
    if request.method == "GET":
        if "school" in session:
            return render_template("school/attendance.html")
        else:
            return redirect(url_for("login"))
    else:
        for i in request.form.keys():
            pymongo.MongoClient(mongo_uri)[database_name]["student"].update_one(
                {"poshanid": i}, {"$push": {"attendance": int(request.form[i])}}
            )

        return render_template("school/attendance.html")


@app.route("/school/health", methods=["POST", "GET"])
def health():
    if request.method == "GET":
        if "school" in session:
            return render_template("school/health.html")
        else:
            return redirect(url_for("login"))
    else:
        print(request.form.keys())
        for i in request.form.keys():
            if i[-2:] == "ht":
                pymongo.MongoClient(mongo_uri)[database_name]["student"].update_one(
                    {"poshanid": i[:-3]}, {"$push": {"height": int(request.form[i])}}
                )
            else:
                pymongo.MongoClient(mongo_uri)[database_name]["student"].update_one(
                    {"poshanid": i[:-3]}, {"$push": {"weight": int(request.form[i])}}
                )

        return render_template("school/health.html")
        # return request.form


@app.route("/school/menu", methods=["POST", "GET"])
def menu():
    if request.method == "GET":
        if "school" in session:
            return render_template("school/menu.html")
        else:
            return redirect(url_for("login"))

    else:
        pymongo.MongoClient(mongo_uri)[database_name]["school"].update_one(
            {"poshanid": session["school"]},
            {"$push": {"menu": request.form}},
        )

        pymongo.MongoClient(mongo_uri)[database_name]["school"].update_one(
            {"poshanid": session["school"]},
            {"$set": {"menuupdatetime": datetime.datetime.now().strftime("%x")}},
        )
        return redirect(url_for("school"))


@app.route("/school/attendance/<classid>", methods=["POST", "GET"])
def attendance_select(classid):
    if "school" in session:
        data = pymongo.MongoClient(mongo_uri)[database_name]["student"].find(
            {}, {"poshanid": 1, "name": 1, "class": 1}
        )

        studentslist = []

        for student in data:
            if student["poshanid"][:2] == str(session["school"]) and student[
                "class"
            ] == int(classid):
                studentslist.append(student)

        return render_template("school/attendance_select.html", students=studentslist)
    else:
        return redirect(url_for("login"))


@app.route("/school/health/<classid>", methods=["POST", "GET"])
def health_select(classid):
    if "school" in session:
        data = pymongo.MongoClient(mongo_uri)[database_name]["student"].find(
            {}, {"poshanid": 1, "name": 1, "class": 1}
        )

        studentslist = []

        for student in data:
            if student["poshanid"][:2] == str(session["school"]) and student[
                "class"
            ] == int(classid):
                studentslist.append(student)

        return render_template("school/health_select.html", students=studentslist)
    else:
        return redirect(url_for("login"))


@app.route("/admin/school/<poshanid>", methods=["POST", "GET"])
def admin_school(poshanid):
    if "admin" in session:
        school = pymongo.MongoClient(mongo_uri)[database_name]["school"].find_one(
            {"poshanid": poshanid}
        )

        if school != None:
            studentcount = school["studentscount"]
            attendancelist = []
            bmilist = []

            sumofbmi = 0
            uw = 0
            nw = 0
            ow = 0
            obs = 0

            sumofht = 0
            sumofwt = 0

            for student in myclient[database_name]["student"].find({}):
                if student["poshanid"][:2] == str(poshanid):
                    gender = student["gender"]
                    age = student["age"]
                    weight = sum(student["weight"]) / len(student["weight"])
                    height = sum(student["height"]) / len(student["height"])

                    sumofht += height
                    sumofwt += weight

                    attnpercent = (
                        student["attendance"].count(1) / len(student["attendance"])
                    ) * 100

                    # Calculate BMI
                    bmi = weight / ((height / 100) ** 2)
                    if gender == "M":
                        bmi = bmi + (0.5 if age >= 50 else 0)
                    else:
                        bmi = bmi - (0.5 if age >= 50 else 0)

                    bmilist.append(bmi)
                    attendancelist.append(attnpercent)

                    sumofbmi += bmi
                    # Determine weight category based on BMI
                    if bmi < 15:
                        uw += 1
                    elif bmi < 23:
                        nw += 1
                    elif bmi < 28:
                        ow += 1
                    else:
                        obs += 1

            print(len(attendancelist))
            print(len(bmilist))

            data = {
                "schoolid": school["poshanid"],
                "schoolname": school["name"],
                "location": school["address"],
                "contact": school["contact"],
                "menuupdate": school["menuupdatetime"],
                "studentcount": studentcount,
                "avgbmi": round(sumofbmi / studentcount, 3),
                "avght": round(sumofht / studentcount, 3),
                "avgwt": round(sumofwt / studentcount, 3),
                "uw": uw,
                "nw": nw,
                "ow": ow,
                "obs": obs,
                "attendancelist": attendancelist,
                "bmilist": bmilist,
            }

            return render_template("admin/school.html", data=data)
        else:
            flash("ischool")
            return redirect(url_for("admin"))
    else:
        return redirect(url_for("login"))


@app.route("/admin/student/<poshanid>", methods=["POST", "GET"])
def admin_student(poshanid):
    if "admin" in session:
        student = pymongo.MongoClient(mongo_uri)[database_name]["student"].find_one(
            {"poshanid": poshanid}
        )

        if student != None:
            weight = sum(student["weight"]) / len(student["weight"])
            height = sum(student["height"]) / len(student["height"])
            gender = student["gender"]
            bmi = weight / ((height / 100) ** 2)
            age = student["age"]

            if gender == "M":
                bmi = bmi + (0.5 if age >= 50 else 0)
            else:
                bmi = bmi - (0.5 if age >= 50 else 0)

            if bmi < 15:
                status = "Under Weight"
            elif bmi < 23:
                status = "Normal Weight"
            elif bmi < 28:
                status = "Over Weight"
            else:
                status = "Obese"

            if bmi < 15:
                bmivariation = 15 - bmi
            elif bmi < 23:
                bmivariation = 0
            else:
                bmivariation = bmi - 23

            data = {
                "name": student["name"],
                "poshanid": student["poshanid"],
                "schoolid": student["poshanid"][:2],
                "class": student["class"],
                "age": student["age"],
                "gender": student["gender"],
                "attendance": (
                    student["attendance"].count(1) / len(student["attendance"])
                )
                * 100,
                "feedback": student["feedbacks"][-1],
                "avgwt": round(weight, 3),
                "avght": round(height, 3),
                "bmi": round(bmi, 3),
                "bmistatus": status,
                "bmirange": "15 to 22",
                "bmivariation": round(bmivariation, 3),
            }
            return render_template("admin/student.html", data=data)
        else:
            flash("istudent")
            return redirect(url_for("admin"))
    else:
        return redirect(url_for("login"))


@app.route("/student", methods=["POST", "GET"])
def student():
    if "student" in session:
        if request.method == "GET":
            return render_template("student.html")
        else:
            pymongo.MongoClient(mongo_uri)[database_name]["student"].update_one(
                {"poshanid": session["student"]},
                {"$push": {"feedbacks": request.form["feedback"]}},
            )

            print(request.form)

            flash("Feedback Submission Successful", category="success")
            return render_template("student.html")
    else:
        return redirect(url_for("login"))


@app.route("/admin", methods=["POST", "GET"])
def admin():
    if "admin" in session:
        schoolcount = myclient[database_name]["school"].count_documents({})
        studentcount = myclient[database_name]["student"].count_documents({})

        sumofbmi = 0
        uw = 0
        nw = 0
        ow = 0
        obs = 0

        sumofht = 0
        sumofwt = 0

        for student in myclient[database_name]["student"].find({}):
            gender = student["gender"]
            age = student["age"]
            weight = sum(student["weight"]) / len(student["weight"])
            height = sum(student["height"]) / len(student["height"])

            sumofht += height
            sumofwt += weight

            # Calculate BMI
            bmi = weight / ((height / 100) ** 2)
            if gender == "M":
                bmi = bmi + (0.5 if age >= 50 else 0)
            else:
                bmi = bmi - (0.5 if age >= 50 else 0)

            sumofbmi += bmi
            # Determine weight category based on BMI
            if bmi < 15:
                uw += 1
            elif bmi < 23:
                nw += 1
            elif bmi < 28:
                ow += 1
            else:
                obs += 1

        data = {
            "schoolcount": schoolcount,
            "studentcount": studentcount,
            "avgbmi": round(sumofbmi / studentcount, 3),
            "avght": round(sumofht / studentcount, 3),
            "avgwt": round(sumofwt / studentcount, 3),
            "uw": uw,
            "nw": nw,
            "ow": ow,
            "obs": obs,
        }

        return render_template("admin.html", data=data)

    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    if "student" in session:
        session.pop("student")
    elif "admin" in session:
        session.pop("admin")
    elif "school" in session:
        session.pop("school")

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
