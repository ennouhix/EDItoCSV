from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash
import os
import logging
import pandas as pd
import requests
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
    return os.listdir(app.config["UPLOAD_FOLDER"])

def convert_to_json(filepath):
    df = pd.read_csv(filepath)
    json_file = os.path.join(app.config["OUTPUT_FOLDER"], os.path.splitext(os.path.basename(filepath))[0] + '.json')
    df.to_json(json_file, orient='records', lines=True)
    return json_file

def convert_to_xml(filepath):
    df = pd.read_csv(filepath)
    xml_file = os.path.join(app.config["OUTPUT_FOLDER"], os.path.splitext(os.path.basename(filepath))[0] + '.xml')
    df.to_xml(xml_file, index=False)
    return xml_file

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

@app.route("/download/<filename>/<format>")
def download_file(filename, format):
    filepath = os.path.join(app.config["OUTPUT_FOLDER"], filename)
    if format == 'json':
        converted_file = convert_to_json(filepath)
    elif format == 'xml':
        converted_file = convert_to_xml(filepath)
    elif format == 'csv':
        return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True)
    else:
        return "Format not supported", 400

    return send_from_directory(app.config["OUTPUT_FOLDER"], os.path.basename(converted_file), as_attachment=True)

@app.route('/upload_to_bc365', methods=['GET', 'POST'])
def upload_to_bc365():
    if request.method == 'POST':
        file = request.files.get('csv_file')
        environment = request.form.get('environment')
        company_id = request.form.get('company_id')
        access_token = request.form.get('access_token')
        
        if not file or file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('upload_to_bc365'))
        
        if not environment or not company_id or not access_token:
            flash('All parameters are required', 'error')
            return redirect(url_for('upload_to_bc365'))
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Logic to upload file to Business Central
        url = f"https://api.businesscentral.dynamics.com/v2.0/{environment}/api/v2.0/companies({company_id})/contacts"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        with open(filepath, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)
        
        if response.status_code == 200:
            flash('File successfully uploaded to Business Central 365!', 'success')
        else:
            flash(f'Failed to upload file: {response.text}', 'error')

        return redirect(url_for('upload_to_bc365'))
    
    return render_template('upload_to_bc365.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            return redirect(url_for('home'))
        else:
            error_message = "Nom d'utilisateur ou mot de passe incorrect."
            return render_template('login.html', error=error_message)
    else:
        return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host='0.0.0.0') 
    
