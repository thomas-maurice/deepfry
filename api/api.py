from flask import Flask, flash, request, redirect, url_for, session, send_file, redirect
from werkzeug.utils import secure_filename
import tempfile
import cv2 as cv
import uuid
import os

from effects import (
    needs_more_dank,
    downsize_image,
)
from log import (
    get_logger
)

ALLOWED_EXTENSIONS = set(['png', 'jpeg', 'jpg'])
app = Flask(__name__)
app.secret_key = 'yolo'
upload_dir = "uploads"
fried_dir = "fried"

if os.path.isabs(upload_dir):
    app.config['UPLOAD_FOLDER'] = upload_dir
else:
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), upload_dir)

if os.path.isabs(fried_dir):
    app.config['FRIED_FOLDER'] = fried_dir
else:
    app.config['FRIED_FOLDER'] = os.path.join(os.getcwd(), fried_dir)

logger = get_logger()

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    logger.info("Creating upload directory")
    os.mkdir(app.config["UPLOAD_FOLDER"])

if not os.path.exists(app.config["FRIED_FOLDER"]):
    logger.info("Creating fried directory")
    os.mkdir(app.config["FRIED_FOLDER"])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    logger = get_logger()
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            resize = request.form['resize'].split('x')
            maxx, maxy = -1, -1
            if len(resize) == 2:
                try:
                    maxx = int(resize[0])
                    maxy = int(resize[1])
                except Exception as exce:
                    logger.error("Could not set max dimension: {}".format(exce))

            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            frame = cv.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if maxx != -1 and maxy != -1:
                logger.info("Downsizing image")
                frame = downsize_image(frame, maxy, maxx)
            frame = needs_more_dank(frame,
                request.form["filters"].split(',') if len(request.form["filters"]) != 0 else [],
                request.form["noise_type"],
                float(request.form["gauss_noise"]),
                float(request.form["sp_ratio"]),
                float(request.form["sp_amount"]),
                float(request.form["motion"]),
                int(request.form["sharpening"]),
                float(request.form["saturation"]),
                int(request.form["brightness"]),
                int(request.form["contrast"]),
                int(request.form["jpeg_iterations"]),
                int(request.form["jpeg_quality"]),
                './filters',
                {},
                ['saturation','noise','sharpening','contrast','motion','jpeg'],
            )
            newfile = "{}.jpg".format(str(uuid.uuid4()))

            cv.imwrite(os.path.join(app.config["FRIED_FOLDER"], newfile), frame)
            #return send_file(newfile, mimetype='image/jpg')
            return redirect("fried/{}".format(newfile))

@app.route('/fried/<image>', methods=['GET'])
def get_fried(image):
    return send_file(
        # Doing this because otherwise it would allow file exfil
        os.path.join(
            app.config["FRIED_FOLDER"],
            os.path.basename(image),
        ),
        mimetype='image/jpg',
    )

@app.route('/', methods=['GET'])
def main():
    return """
    <html>
<body>

    <form action = "upload" method = "POST" enctype = "multipart/form-data">
        File: <input type="file" name="file" /> <br>
        Coma separated filters <input type="text" name="filters" value="joint,lasers_3" /> <br>
        Noise type (gauss, sp, poisson) <input type="text" name="noise_type" value="sp" /> <br>
        Gauss noise amount <input type="text" name="gauss_noise" value="1000" /> <br>
        Salt and pepper ratio <input type="text" name="sp_ratio" value="0.5" /> <br>
        Salt and pepper amount <input type="text" name="sp_amount" value="0.08" /> <br>
        Motion amount <input type = "text" name="motion" value="0"/> <br>
        Sharpening <input type="text" name="sharpening" value="600" /> <br>
        Saturation <input type="text" name="saturation" value="5" /> <br>
        Brightness <input type="text" name="brightness" value="15" /> <br>
        Contrast <input type="text" name="contrast" value="120" /> <br>
        JPEG iterations <input type="text" name="jpeg_iterations" value="5" /> <br>
        JPEG quality <input type="text" name="jpeg_quality" value="10" /> <br>
        Resize <input type="text" name="resize" value="600x600" /> <br>
        <input type="submit"/>
    </form>

</body>
</html>
    """