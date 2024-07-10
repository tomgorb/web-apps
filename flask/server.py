import os
import pandas as pd
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object('config')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def upload_file():
    file_path = ''
    if request.method == 'POST':
        # check if the post request has the file part
        if 'data' not in request.files:
            return file_path
        file = request.files['data']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return file_path
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

    return file_path


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == "GET":
        args = {
            'min': 'min',
            'max': 'max',
            'sum': 'sum',
            'mean': 'mean',
            'median': 'median',
            'std': 'std',
            'quantile': 'quantile'
            }
        return render_template("index.html", **args)
    elif request.method == "POST":
        userdata = request.form.to_dict(flat=False)

        file_path = upload_file()

        cmd = "python3 compute.py"

        if file_path:
            cmd += f""" -d {file_path}"""

        output_file = 'data_{}.csv'.format(datetime.now().strftime("%Y%m%d_%H%M%S"))
        output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_file)
        cmd += f""" -o {output_filepath}"""

        for i in range(1, 11):
            if f"""period_start_{i}""" in userdata.keys():
                period_name_col = f"""period_name_{i}"""
                period_start_col = f"""period_start_{i}"""
                period_end_col = f"""period_end_{i}"""
                cmd += f""" -n{i} '{userdata[period_name_col][0]}'"""
                cmd += f""" -p{i} {userdata[period_start_col][0]} {userdata[period_end_col][0]} """

        cmd += "SOURCE "

        stats = userdata['stats']
        cmd += f""" -k {' '.join("'" + k + "'" for k in stats)}"""

        print(cmd)
        os.system(cmd)
        try:
            data = pd.read_csv(output_filepath)
        except:
            data = pd.DataFrame()

        return render_template("result.html",
                               tables=[data.replace(np.nan, '').to_html(index=False, max_rows=10, max_cols=10, classes='mystyle')],
                               filename=output_file)


@app.route("/result", methods=["POST"])
def result():
    filename = request.form['output_file']
    return redirect(url_for("data_file", filename=filename))


@app.route('/uploads/<filename>')
def data_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],  filename)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=app.config['PORT'])
