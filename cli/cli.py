import click
import cv2 as cv
import logging
from tabulate import tabulate
import os
import copy
import tempfile
import sys

from log import (
    get_logger,
    set_level,
)
from config import (
    EFFECTS,
)
from effects import (
    needs_more_dank,
    Filter,
    downsize_image,
)

@click.group()
@click.option('--verbose', default=False, is_flag=True, help="Enable verbose logging")
def cli(verbose):
    if verbose:
        set_level(logging.INFO)

@cli.command()
@click.option('--image', default="", help='Image to process')
@click.option('--video', default=False, help='Do use the video ?', is_flag=True)
@click.option('--filters', default='', help='Coma separated list of filters to use, the filters will be applied in the order you specify them on every face found')
@click.option('--noise_type', default='gauss',
    help="types of noises to add", type=click.Choice([
        "gauss",
        "poisson",
        "speckle",
        "sp"
    ]))
@click.option('--gauss_amount', default=600, help="Amount of gaussian noise")
@click.option('--sp_ratio', default=0.5, help="Salt and pepper noise ratio")
@click.option('--sp_amount', default=0.04, help="Salt and pepper noise amount")
@click.option('--motion', default=0, help="Amount of motion blur to add")
@click.option('--sharpening', default=110, help="Sharpening")
@click.option('--saturation', default=3.5, help="Saturation")
@click.option('--brightness', default=15, help="Brightness")
@click.option('--contrast', default=110, help="Contrast")
@click.option('--jpeg_iterations', default=5, help="How many times compress the image after frying ?")
@click.option('--jpeg_quality', default=110, help="How shitty should the compression be")
@click.option('--filters_dir', default="./filters", help="Where to find the filters")
@click.option('--output', default="out.jpg", help="Output file name")
@click.option('--overrides', default="", help="Coma separated list of overrides on the form filter:variable=value")
@click.option('--effects', default="saturation,noise,sharpening,contrast,motion,jpeg", help="""Coma separated list of the effects you want to apply,
like motion,noise,saturation,jpeg, the full list of available effects is {}""".format(EFFECTS))
@click.option('--url', default="", help="URL of an image to download and deepfry")
@click.option('--directory', default="", help="Deepfries all the images in a directory")
@click.option('--max-size', default="", help="Downsizes the image to maximum dimensions HEIGHTxWIDTH")
def fry(image,
            video,
            filters,
            noise_type,
            gauss_amount,
            sp_ratio,
            sp_amount,
            motion,
            sharpening,
            saturation,
            brightness,
            contrast,
            jpeg_iterations,
            jpeg_quality,
            filters_dir,
            output,
            overrides,
            effects,
            url,
            directory,
            max_size):
    filters = filters.split(',')
    effects = effects.split(',')
    logger = get_logger()
    max_height = -1
    max_width = -1
    max_dim = max_size.split('x')
    if len(max_dim) == 2:
        try:
            max_height = int(max_dim[0])
            max_width = int(max_dim[1])
        except Exception as exce:
            logger.error("Could not set max dimension: {}".format(exce))

    # Parse all the override shit
    parsed_overrides = {}
    if len(overrides) != 0:
        overrides = overrides.split(',')
        for override in overrides:
            f, o = override.split(":")
            k, v = o.split('=')
            try:
                v = float(v)
            except:
                # it is probably a string value what do i know
                pass
            if not f in parsed_overrides:
                parsed_overrides[f] = {k: v}
            else:
                parsed_overrides[f][k] = v

    logger.info('Using the following overrides: {}'.format(parsed_overrides))
    logger.info('Using the following effects: {}'.format(effects))
    logger.info('The output image is going to be saved at {}'.format(output))

    if not video:
        if url != "":
            logger.info("Trying to download {}".format(url))
            tmp = tempfile.NamedTemporaryFile(delete=False)
            img = requests.get(url)
            if img.status_code != 200:
                logger.error("Download failed with exit status {}".format(img.status_code))
                sys.exit(1)
            else:
                logger.info("Saving file at {}".format(tmp.name))
                tmp.write(img.content)
                tmp.close()
            image = tmp.name

        if image == "" and directory == "":
            logger.error("No image specified !")
            sys.exit(1)

        if directory == "" and not os.path.isfile(image):
            logger.error("This image file does not exist")
            sys.exit(1)

        if directory == "":
            frame = cv.imread(image)
            if max_height != -1 and max_width != -1:
                logger.info("Downsizing image")
                frame = downsize_image(frame, max_height, max_width)
            frame = needs_more_dank(frame,
                filters,
                noise_type,
                gauss_amount,
                sp_ratio,
                sp_amount,
                motion,
                sharpening,
                saturation,
                brightness,
                contrast,
                jpeg_iterations,
                jpeg_quality,
                filters_dir,
                parsed_overrides,
                effects,
            )
            cv.imwrite(output, frame)
            if url != "":
                os.unlink(image)
        else:
            for img in os.listdir(directory):
                if '-fried.jpg' in img:
                    continue
                inname = os.path.join(directory, img)
                frame = cv.imread(img)
                if max_height != -1 and max_width != -1:
                    frame = downsize_image(frame, max_height, max_width)
                outname = os.path.join(directory, img.split('.')[0] + '-fried.jpg')
                logger.info("Frying {} to {}".format(inname, outname))
                try:
                    frame = needs_more_dank(frame,
                        filters,
                        noise_type,
                        gauss_amount,
                        sp_ratio,
                        sp_amount,
                        motion,
                        sharpening,
                        saturation,
                        brightness,
                        contrast,
                        jpeg_iterations,
                        jpeg_quality,
                        filters_dir,
                        parsed_overrides,
                        effects,
                    )
                    cv.imwrite(outname, frame)
                except Exception as exce:
                    logger.error("Could not deepfry {}: {}".format(inname, exce))
    else:
        cap = cv.VideoCapture(0)
        cap.set(cv.CAP_PROP_FPS, 2)
        while(cap.isOpened()):
            ret, frame = cap.read()
            original = copy.deepcopy(frame)
            if ret==True:
                if max_height != -1 and max_width != -1:
                    frame = downsize_image(frame, max_height, max_width)
                frame = needs_more_dank(frame,
                    filters,
                    noise_type,
                    gauss_amount,
                    sp_ratio,
                    sp_amount,
                    motion,
                    sharpening,
                    saturation,
                    brightness,
                    contrast,
                    jpeg_iterations,
                    jpeg_quality,
                    filters_dir,
                    parsed_overrides,
                    effects,
                )

                cv.imshow('dank',frame)
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
        cap.release()
        cv.destroyAllWindows()

@cli.group()
def filter():
    pass

@filter.command(name="list")
@click.option('--filters_dir', default="./filters", help="Where to find the filters")
def filter_list(filters_dir):
    headers = [
        'Name',
        'Long name',
        'Description',
        'Application',
        'Priority',
    ]
    data = []
    for d in os.listdir(filters_dir):
        if os.path.isdir(os.path.join(filters_dir, d)):
            f = Filter(os.path.join(filters_dir, d, 'filter.yml'), {})
            data.append([
                d,
                f.name,
                f.description,
                ','.join(f.applies),
                f.priority
            ])
    print(tabulate(data, headers))

@cli.command()
@click.option('--host', default="127.0.0.1", help="Which address to listen to")
@click.option('--port', default=7777, help="Which port to listen on")
@click.option('--upload-dir',
    default=os.path.join(os.getcwd(), "uploads"),
    help="Which directory to use for the uploads")
@click.option('--fried-dir',
    default=os.path.join(os.getcwd(), "fried"),
    help="Which directory to use for the fried images")
@click.option('--debug', default=False, help="Debug mode for Flask", is_flag=True)
def server(host, port, upload_dir, fried_dir, debug):
    from api import app

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

    app.run(debug=debug, host=host, port=port)
