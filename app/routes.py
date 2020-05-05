from flask import session, render_template, flash, redirect, request, url_for, send_file
from werkzeug import secure_filename
from app import app
import os
import shutil, stat
import glob
import logging #change logging status of wekzeug
import TTH

TTH.init()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data = request.form["data"]
        session["rawdata"] = data
        data = data.splitlines()
        session["data"] = data

        font = request.form["font"]
        session["font"] = font

        return redirect(url_for("generate"))

    try:
        rawdata = session["rawdata"]
    except KeyError:
        rawdata = ""

    fonts = []
    for filename in os.listdir(os.path.join(app.config["ROOT"], "fonts")):
        fonts.append(filename)

    return render_template("main.html", letters=app.config["LETTERS"], data=rawdata, fonts=fonts)


@app.route('/form',  methods=['GET', 'POST'])
def uploadFourm():
    #if there was a POST request
    if request.method == 'POST':

        num = request.form["font"]

        if num == "" or num == None:
            num = "default"


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
                    path = os.path.join(app.config["ROOT"] +"/fonts", str(num)) 
                    os.mkdir(path)
                    path2 = os.path.join(path, "upper")
                    os.mkdir(path2)
                except FileExistsError:
                    print("Directory exists, updating images")

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


    print(session["modifier"], type(session["modifier"]))

    if not text:
        flash("Error: Please enter text")
        return redirect(url_for("home"))


    imgs = TTH.loadImages(num, letters, "fonts/")
    final = TTH.renderHandWriting(text, imgs, letters, modifier=float(session["modifier"]))

    savePath = os.path.join(app.config["ROOT"] + "/app/static/images/", "image.png")

    if int(session["tolerance"]) > 0:

        final = TTH.removeBackground(final, tolerance=int(session["tolerance"]))

    TTH.save_image(final, savePath)

    return render_template("download.html", filename="static/images/image.png", mod=session["modifier"], tol=session["tolerance"])

@app.route("/prefrences", methods=['GET', 'POST'])
def prefrences():
    pass

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

