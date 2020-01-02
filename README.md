# Deepfrier
This is a python OpenCV based scrit aimed at deep frying images.

# Installation
You need to install the OpenCV library on your system, read the docs
of the project for more info on how to do so.

Install the python dependencies afterwards, `pip3 install -r requirements.txt`
should do it.

You should be all set to use the project.

## Usage
```
$ ./deepfry.py fry --help
Usage: deepfry.py fry [OPTIONS]

Options:
  --image TEXT                    Image to process
  --video                         Do use the video ?
  --filters TEXT                  Coma separated list of filters to use, the
                                  filters will be applied in the order you
                                  specify them on every face found
  --noise_type [gauss|poisson|speckle|sp]
                                  types of noises to add
  --gauss_amount INTEGER          Amount of gaussian noise
  --sp_ratio FLOAT                Salt and pepper noise ratio
  --sp_amount FLOAT               Salt and pepper noise amount
  --motion INTEGER                Amount of motion blur to add
  --sharpening INTEGER            Sharpening
  --saturation FLOAT              Saturation
  --brightness INTEGER            Brightness
  --contrast INTEGER              Contrast
  --jpeg_iterations INTEGER       How many times compress the image after
                                  frying ?
  --jpeg_quality INTEGER          How shitty should the compression be
  --filters_dir TEXT              Where to find the filters
  --output TEXT                   Output file name
  --overrides TEXT                Coma separated list of overrides on the form
                                  filter:variable=value
  --effects TEXT                  Coma separated list of the effects you want
                                  to apply,
                                  like motion,noise,saturation,jpeg,
                                  the full list of available effects is
                                  ['motion', 'sharpening', 'contrast', 'jpeg',
                                  'noise', 'saturation']
  --url TEXT                      URL of an image to download and deepfry
  --help                          Show this message and exit.
```

# Examples
You can find in the examples directory 2 images generated with the following command lines:

For my github avatar:
```
./deepfry.py fry --filters deal_with_it,shutterstock --jpeg_quality 8 --noise_type sp --sp_ratio 0.1 --sp_amount 0.3 --image  source.jpg --sharpening 200 --saturation 1.5 --contrast 2
```
For Lena:
```
./deepfry.py fry --filters lasers_2,joint --jpeg_quality 5 --noise_type gauss --image  lena.png --sharpening 100 --saturation 1 --gauss_amount 300 --motion 8
```

# License
```
           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                   Version 2, December 2004

Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

Everyone is permitted to copy and distribute verbatim or modified
copies of this license document, and changing it is allowed as long
as the name is changed.

           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
  TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

 0. You just DO WHAT THE FUCK YOU WANT TO.
```
