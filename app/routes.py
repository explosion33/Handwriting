from flask import session, render_template, flash, redirect, request, url_for, send_file
from werkzeug import secure_filename
from app import app
import os
import shutil, stat
import glob
import logging #change logging status of wekzeug
import TTH
from random import randint
import ast

TTH.init()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def toHex(num):
    out=""
    while True:
        x = int(num/16)
        r = num-(x*16)
        
        hex = {
            10: "A",
            11: "B",
            12: "C",
            13: "D",
            14: "E",
            15: "F",
            }

        if r in hex:
            out += hex[r]
        else:
            out += str(r)
        print(x,r)
        if x == 0:
            break
        num = x
    return out[::-1]


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data = request.form["data"]
        session["rawdata"] = data

        for i in data:
            data = data.replace("”", '"')
            data = data.replace("“", '"')


        data = data.splitlines()

        session["data"] = data

        font = request.form["font"]

        if "-private" in font:
           font = font.replace("-private", "$" + session["ID"])

        print(font)
        session["font"] = font

        return redirect(url_for("generate"))

    try:
        rawdata = session["rawdata"]
    except KeyError:
        rawdata = ""

    fonts = []
    for filename in os.listdir(os.path.join(app.config["ROOT"], "fonts")):
        if "$" in filename:
            i = filename.index("$")
            p = filename[i+1::]

            try:
                if session["ID"] == p:
                    name = filename[:i]
                    fonts.append(name + "-private")
            except:
                pass


        else:
            fonts.append(filename)


    try:
        session["private"]
    except:
        session["private"] = False

    try:
        session["ID"]
        logged = True
    except:
        logged = False

    return render_template("main.html", letters=app.config["LETTERS"], data=rawdata, fonts=fonts, logged=logged)


@app.route('/form',  methods=['GET', 'POST'])
def uploadFourm():
    #if there was a POST request
    if request.method == 'POST':

        name = request.form["font"]

        if name == "" or name == None:
            name = "default"

        try:
            print(session["private"])
            if session["private"]:
                name += "$" + session["ID"]
        except:
            print("user not logged in")


        #get file and gerneate name
        f = request.files['filename']
        filename = secure_filename(f.filename)
        #make sure there was a file if not post Error
        print(filename)
        if filename:
            i = filename[::-1]
            if i[0:3] == "gnp" or i[0:3] == "gpj":
                #save file and show success page
                pth = os.path.join(app.config["ROOT"] + "/app/static/images", "fourm.png")
                f.save(pth)
                print("returning")

                try:
                    path = os.path.join(app.config["ROOT"] +"/fonts", str(name)) 
                    os.mkdir(path)
                    path2 = os.path.join(path, "upper")
                    os.mkdir(path2)
                    flash("Creating new font")
                except FileExistsError:
                    print("Directory exists, updating images")
                    flash("Updating font")

                letters = TTH.makeLetterList(app.config["LETTERS"])

                r = TTH.generateFourm(letters)
                TTH.readFourm(letters, pth, path, r)


                return redirect(url_for("home"))
            else:
                flash("Error: please submit a png file")
        else:
            flash("Error: please select a file")

    pth = app.config["ROOT"] + "/app/static/images/blankFourm.png"
    TTH.generateFourm(TTH.makeLetterList(app.config["LETTERS"]), pth)
    
    return render_template('fourm.html', filename="static/images/blankFourm.png")


@app.route('/generate', methods=["GET", "POST"])
def generate():
    if request.method == 'POST':
        session["modifier"] = float(request.form["modifier"])
        session["tolerance"] = int(request.form["tolerance"])


    letters = TTH.makeLetterList(app.config["LETTERS"])
    print(letters)

    num = session["font"]
    text = session["data"]


    try: #check if session data has been set, if not set it
        session["modifier"]
    except KeyError:
        session["tolerance"] = 200
        session["modifier"] = 0


    if not text:
        flash("Error: Please enter text")
        return redirect(url_for("home"))


    imgs, errors = TTH.loadImages(num, letters, "fonts/")
    
    for error in errors:
        print("ERROR:", error)
        flash(error)

    final = TTH.renderHandWriting(text, imgs, letters, modifier=float(session["modifier"]))

    KEY ="image"

    savePath = os.path.join(app.config["ROOT"] + "/app/static/images/", KEY + ".png")

    if int(session["tolerance"]) > 0:

        final = TTH.removeBackground(final, tolerance=int(session["tolerance"]))

    TTH.save_image(final, savePath)

    return render_template("download.html", filename="static/images/" + KEY + ".png", mod=session["modifier"], tol=session["tolerance"])

@app.route("/prefrences", methods=['GET', 'POST'])
def prefrences():
    if request.method == 'POST':
        new = request.form["letters"]
        new = new.splitlines()

        temp = ""
        for l in new:
            temp += l

        lst = []
        for i in temp:
            lst.append(i)
        lst = list(dict.fromkeys(lst))

        new=""
        for l in lst:
            new += l

        app.config["LETTERS"] = new


        try:
            request.form["private"]
            session["private"] = True
        except:
            session["private"] = False



        flash("Updated prefrences")


    if session["private"]:
        private = "checked"
    else:
        private = ""

    return render_template("prefrences.html", letters=app.config["LETTERS"], private=private)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form["user"]
        password = request.form["pass"]

        f = open(app.config["ROOT"] + "/users.txt", "r")
        users = ast.literal_eval(f.read())
        f.close()

        if username in users:
            print(password, users[username][0])
            if password == users[username][0]:
                session["ID"] = users[username][1]
                return redirect(url_for("home"))
            else:
                flash("invalid password")
        
        else:
            flash("invalid username")

    try:
        username
    except:
        username = ""
        password = ""

    return render_template("login.html", user=username, password=password)

@app.route("/logout")
def logout():
    session.pop("ID")
    return redirect(url_for("home"))

@app.route("/signup", methods=["GET", "POST"])
def signUp():
    if request.method == 'POST':
        username = request.form["user"]
        password = request.form["pass"]

        f = open(app.config["ROOT"] + "/users.txt", "r")
        users = ast.literal_eval(f.read())
        f.close()

        if username in users:
            flash("user already exists")

        else:
            key = toHex(randint(0,1000000))
            session["ID"] = key
            users[username] = [password, key]

            f = open(app.config["ROOT"] + "/users.txt", "w")
            print(str(users))
            f.write(str(users))
            f.close()

            return redirect(url_for("home"))


    try:
        username
    except:
        username = ""
        password = ""

    return render_template("signup.html", user=username, password=password)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
