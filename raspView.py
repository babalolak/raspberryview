import json, shlex, subprocess,os, sys

#KB Update.  Calling Docker process instead of alpr from command line.
class PlateReader:


    def __init__(self, folder=None):

        self.dir=folder
        #webcam subprocess args
        webcam_command = "fswebcam -r 640x480 -S 20 --no-banner --quiet alpr.jpg"
        self.webcam_command_args = shlex.split(webcam_command)

        #alpr subprocess args
        #Note the 'us' country code has a bug that causes Docker 
        #to not find the image in the mounted volume.  This may affect accuracy!
        alpr_command = "docker run -it --rm -v"+self.dir+":/data:ro openalpr -c eu -d --json alpr.jpg"#alpr -c eu -t hr -n 300 -j alpr.jpg"
        self.alpr_command_args = shlex.split(alpr_command)


    def webcam_subprocess(self):
        return subprocess.Popen(self.webcam_command_args, stdout=subprocess.PIPE)


    def alpr_subprocess(self, pic=None):
        if pic is not None:
            alpr_command = "docker run -it --rm -v"+self.dir+":/data:ro openalpr -c eu -d --json " + pic
            self.alpr_command_args = shlex.split(alpr_command)
        return subprocess.Popen(self.alpr_command_args, stdout=subprocess.PIPE)


    def alpr_json_results(self,pic=None):

        if pic is None:
            self.webcam_subprocess().communicate()
        alpr_out, alpr_error = self.alpr_subprocess(pic).communicate()

        if not alpr_error is None:
            return None, alpr_error
        elif "No license plates found." in alpr_out:
            return None, None

        try:
            return json.loads("{"+alpr_out.split('{',1)[1]), None#json.loads(alpr_out), None
        except ValueError, e:
            return None, e        

    def read_dir(self):
        files = os.listdir(self.dir)
        for pic in files:
            yield pic

    def read_pics(self, pic=None):
        alpr_json, alpr_error = self.alpr_json_results(pic)

        if not alpr_error is None:
            print alpr_error
            return

        if alpr_json is None:
            print "No results!"
            return
        
        results = alpr_json["results"]

        if results == []:
            print "Unable to recognize licence plate!\n"
            return
        ordinal = 0
        for result in results:
            candidates = result["candidates"]
            max_conf = 85
            if candidates:
                max_conf = candidates[0]["confidence"]
            for candidate in candidates:
                # if candidate["matches_template"] == 1:
                if candidate["confidence"] >= max_conf:
                    max_conf= candidate["confidence"] 
                    ordinal += 1
                    print "Guess {0:d}: {1:s} {2:.2f}%\n".format(ordinal, candidate["plate"], candidate["confidence"])

    def read_plates(self):
        if self.dir is None:
            self.read_pics()
        else:
            for pic in self.read_dir():
                print "Current pic: ", pic
                self.read_pics(pic)
def main(argv=None):
    arg = None
    if argv is not None:
        try:
        ###ADD CHECK FOR PROPER ARGUMENTS
            arg = argv[1]
        except Exception, e:
            print "Problem with sys arguments",e
            return
        plate_reader = PlateReader(arg)
        plate_reader.read_plates()

if __name__=="__main__":
    main(sys.argv)
    # plate_reader = PlateReader()
    # plate_reader.read_plates()
