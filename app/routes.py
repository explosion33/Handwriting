from flask import render_template, flash, redirect, request, url_for, send_file
from werkzeug import secure_filename
from app import app
import os
import shutil, stat
import glob
import logging #change logging status of wekzeug
import TTH

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

pth = os.path.join(app.config["ROOT"], "input.txt")
num = 0

#Call to shutdown server and close QR window
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/')
def home():
    t = TTH.parseFile(pth)

    print(pth,t)

    return render_template("main.html", text=t, letters=app.config["LETTERS"], chars=app.config["CHARS"])


#main page plus random key handles transfers
@app.route('/text',  methods=['GET', 'POST'])
def uploadText():
    #if there was a POST request
    if request.method == 'POST':
        #get file and gerneate name
        f = request.files['filename']
        filename = secure_filename(f.filename)
        #make sure there was a file if not post Error
        print(filename)
        if filename:
            i = filename[::-1]
            if i[0:3] == "txt":
                #save file and show success page
                pth = os.path.join(app.config["ROOT"], "input.txt")
                f.save(pth)
                print("returning")
                return redirect(url_for("home"))
            else:
                flash("Error: please submit a txt file")
        else:
            flash("Error: please select a file")
    print("text")
    return render_template('text.html')

@app.route('/fourm',  methods=['GET', 'POST'])
def uploadFourm():
    #if there was a POST request
    if request.method == 'POST':
        #get file and gerneate name
        f = request.files['filename']
        filename = secure_filename(f.filename)
        #make sure there was a file if not post Error
        print(filename)
        if filename:
            i = filename[::-1]
            if i[0:3] == "gnp":
                #save file and show success page
                pth = os.path.join(app.config["ROOT"], "fourm.png")
                f.save(pth)
                print("returning")
                return redirect(url_for("home"))
            else:
                flash("Error: please submit a png file")
        else:
            flash("Error: please select a file")
    print("fourm")
    return render_template('fourm.html')

@app.route('/generate')
def generate():

    temp = []
    for l in app.config["LETTERS"]:
        temp.append(l)
    temp += app.config["CHARS"]
    letters = temp


    text = TTH.parseFile(pth)
    imgs = TTH.loadImages(num, letters)
    final = TTH.renderHandWriting(text, imgs, letters)

    savePath = os.path.join(app.config["ROOT"] + "/app/static/images/", "image.png")

    TTH.save_image(final, savePath)

    return render_template("download.html", filename="static/images/image.png")


#exit page shutsdown server
@app.route("/exit")
def exit():
    shutdown_server()
    return render_template("exit.html")