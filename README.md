# raspberryview

An embedded image recognition processor.

Current prototype is a command line image license plate reader.  Derived from PyALPR: https://github.com/lukagabric/PyALPR/blob/master/README.md

###Dependencies:

####Docker 
Pull the OpenALPR docker image from Docker Hub.
``` shell
docker pull openalpr/openalpr
```

###Usage:
``` shell
# Run with an the name of a directory containing test images.
python -m raspView <image-directory-name>
# Run with a webcam setup 
python -m raspView
```
