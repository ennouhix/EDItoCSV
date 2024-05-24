from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash
import os
import logging
from msconsconverter.functions import convert_batch, convert_single
from msconsconverter.logger import CustomLogger

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "outputs"

# Ensure the directories exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

def get_uploaded_files():
    uploaded_files = os.listdir(app.config["UPLOAD_FOLDER"])
    return uploaded_files

#@app.route("/")
#def home():
    #return render_template("home.html")

@app.route("/convert", methods=["GET", "POST"])
def convert():
    if request.method == "POST":
        input_file = request.files.get("input_file")
        input_directory = request.form.get("input_directory")
        debug_mode = request.form.get("debug_mode") == "on"

        if not input_file and not input_directory:
            flash("At least one of the file or directory must be provided", "error")
            return redirect(url_for("convert"))

        custom_logger = CustomLogger()
        logging_level = logging.DEBUG if debug_mode else logging.INFO
        logger = custom_logger.get_logger(logging_level=logging_level)

        output_directory = app.config["OUTPUT_FOLDER"]

        if input_file:
            input_filepath = os.path.join(app.config["UPLOAD_FOLDER"], input_file.filename)
            input_file.save(input_filepath)
            convert_single(filename=input_filepath, target_dir=output_directory, logger=logger)
            flash(f"File {input_file.filename} converted successfully!", "success")

        elif input_directory:
            convert_batch(directory=input_directory, target_dir=output_directory, logger=logger)
            flash(f"Directory {input_directory} converted successfully!", "success")

        return redirect(url_for("convert"))

    return render_template("convert.html")

@app.route("/uploads")
def list_uploads():
    uploaded_files = get_uploaded_files()
    return render_template("uploads.html", uploaded_files=uploaded_files)

@app.route("/outputs")
def list_outputs():
    files = os.listdir(app.config["OUTPUT_FOLDER"])
    return render_template("output.html", files=files)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename)
# Page de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Ici, vous vérifieriez les informations d'identification
        # Par exemple, vous pourriez vérifier dans une base de données si les informations d'identification sont valides
        # Pour cet exemple, nous allons simplement vérifier si le nom d'utilisateur est "admin" et le mot de passe est "password"
        if username == 'admin' and password == 'admin':
            # Si les informations d'identification sont valides, rediriger vers la page d'accueil
            return redirect(url_for('home'))
        else:
            # Si les informations d'identification sont incorrectes, afficher un message d'erreur
            error_message = "Nom d'utilisateur ou mot de passe incorrect."
            return render_template('login.html', error=error_message)
    else:
        # Si la méthode est GET, afficher simplement le formulaire de connexion
        return render_template('login.html')

# Page d'accueil
@app.route('/home')
def home():
    return render_template('home.html')



if __name__ == "__main__":
    app.run(debug=True)
