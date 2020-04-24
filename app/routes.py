from flask import render_template, flash, redirect, request, url_for
from werkzeug import secure_filename
from app import app
import os
import shutil, stat
import glob
import logging #change logging status of wekzeug

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

clearedDIR = False

#Call to shutdown server and close QR window
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

#main page plus random key handles transfers
@app.route('/' + app.config["DOWNKEY"],  methods=['GET', 'POST'])
def download_file():
    #if there was a POST request
    if request.method == 'POST':
        #get file and gerneate name
        f = request.files['filename']
        filename = secure_filename(f.filename)
        #make sure there was a file if not post Error
        if filename != "":
            #save file and show success page
            pth = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            f.save(pth)
            nicePth = app.config["UPLOAD_FOLDER"] + "/" + str(filename)
            return render_template("success.html", filename=filename, filepath=nicePth, link1=app.config["DOWNKEY"])
        else:
            flash("Error: please select a file")

    return render_template('download.html')

@app.route('/' + app.config["UPKEY"],  methods=['GET', 'POST'])
def upload_file():
    shutil.make_archive(app.config["ROOT"] + "/app/static/files", 'zip', app.config["ROOT"] + "/app/static/files")
    return render_template("upload.html", filename="static/files.zip", filenameLong=app.config["QR_IP"] + "static/files.zip")

@app.route('/' + app.config["UPKEY"][0:10] + "select",  methods=['GET', 'POST'])
def upload_select():
    global clearedDIR
    if not clearedDIR:
        try:
            shutil.rmtree(app.config["ROOT"] + "/app/static/files")
        except:
            pass
        os.mkdir(app.config["ROOT"] + "/app/static/files")
        clearedDIR = True

    #if there was a POST request
    if request.method == 'POST':
        #get file and gerneate name
        f = request.files['filename']
        filename = secure_filename(f.filename)
        #make sure there was a file if not post Error
        if filename != "":
            #save file and show success page
            pth = os.path.join("files", filename)
            f.save(app.config["ROOT"] + "/app/static/files/" + str(filename))
            nicePth = "files" + "/" + str(filename)
            return render_template("success.html", filename=filename, filepath="server", link1=app.config["UPKEY"][0:10] + "select")
        else:
            flash("Error: please select a file")
    return render_template("uploadSelect.html")


#exit page shutsdown server
@app.route("/exit")
def exit():
    shutdown_server()
    return render_template("exit.html")