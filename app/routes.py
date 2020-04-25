from flask import render_template, flash, redirect, request, url_for
from werkzeug import secure_filename
from app import app
import os
import shutil, stat
import glob
import logging #change logging status of wekzeug
import TTH

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

clearedDIR = False

#Call to shutdown server and close QR window
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/')
def home():
    pth = os.path.join(app.config["ROOT"], "input.txt")

    t = TTH.parseFile(pth)

    print(pth,t)

    return render_template("main.html", text=t)


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


#exit page shutsdown server
@app.route("/exit")
def exit():
    shutdown_server()
    return render_template("exit.html")