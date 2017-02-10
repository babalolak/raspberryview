#!/usr/bin/python
# The contents of this file are in the public domain. See LICENSE_FOR_EXAMPLE_PROGRAMS.txt
#
# This example program shows how you can use dlib to make an object
#   detector for things like faces, pedestrians, and any other semi-rigid
#   object.  In particular, we go though the steps to train the kind of sliding
#   window object detector first published by Dalal and Triggs in 2005 in the
#   paper Histograms of Oriented Gradients for Human Detection.
#
import os
import sys, getopt
import glob

import dlib
from trainingImages import TrainingImages 
#Replaced with cv2, may slightly reduce overhead
# from skimage import io
import cv2
import numpy as np

#This is a generic object detection trainer.
#This programs takes a training directory with images and json files of the 
#naming convention <imagename>.<jpg/png/tga/gif> and <imagename>-labels.lif 
#respectively. The json files (in this case with a '.lif' extension THIS 
#WILL CHANGE) were and can be created with pyLabelKB program to produce
#annotated bounding boxes of the objects in the training images.
#At the command line, pass the top directory that contains ./training and 
#./testing directories. 

class PlateDetector(object):

    @staticmethod
    def train(train,model,test,flips,C,threads,verbose):

        # Now let's do the training.  The train_simple_object_detector() function has a
        # bunch of options, all of which come with reasonable default values.  The next
        # few lines goes over some of these options.
        options = dlib.simple_object_detector_training_options()

        #**********************REMOVE!!!!!!!!!!!!!!!!!******************
        #Since faces are left/right symmetric we can tell the trainer to train a
        # symmetric detector.  This helps it get the most value out of the training
        # data.
        options.add_left_right_image_flips = flips

        # The trainer is a kind of support vector machine and therefore has the usual
        # SVM C parameter.  In general, a bigger C encourages it to fit the training
        # data better but might lead to overfitting.  You must find the best C value
        # empirically by checking how well the trained detector works on a test set of
        # images you haven't trained on.  Don't just leave the value set at 5.  Try a
        # few different C values and see what works best for your data.
        options.C = C
        # Tell the code how many CPU cores your computer has for the fastest training.
        options.num_threads = threads
        options.be_verbose = verbose


        # You just need to put your images into a list. TrainingImages takes a folder
        #and extracts the images and bounding boxes for each image
        trainingSet = TrainingImages(train)
        images = trainingSet.images

        # Then for each image you make a list of rectangles which give the pixel
        # locations of the edges of the boxes.
        # And then you aggregate those lists of boxes into one big list and then call
        # train_simple_object_detector().
        boxes = trainingSet.boxes

        testImages = images
        testBoxes = boxes
        if test != train:
            testSet = TrainingImages(test)
            testImages = testSet.images
            testBoxes = testSet.boxes

        count = 1
        width = 0
        height = 0

        ##Calculating boxes, aspect ratios etc.  ***May need to adjust logic
        ##to accommodate ambiguity.
        ##Also saving new masked images to disk to verify the correct
        ##annotations are being detected.
        if not os.path.exists(train+"/masked"):
            os.makedirs(train+"/masked")
        aspRatios = []
        flatARs = []
        dictARs = {}
        for j,i in enumerate(boxes):
            curImageName = trainingSet.imageNames[j]
            print "Image: ", curImageName
            newImage = images[j].copy()
            aRs = []
            for box in i:
                cv2.rectangle(newImage, (box.top(),box.left()), (box.bottom(),box.right()), (255, 255, 255), thickness=-3)
                width += box.width()
                height += box.height()
                ar = float(box.width())/float(box.height())
                aRs.append(ar)
                dictARs[ar]=box
                flatARs.append(ar)
                count += 1
                print "Box:   ",box, "\t Area:  ",box.area(), "\tAR:  ",aRs

            aspRatios.append(aRs)
            print "\nAspect Ratios:  ",aspRatios, "\nDictionary: ", dictARs
            baseName = curImageName.split("/")[-1]
            newImageName =  train+"/masked/"+(baseName).replace(".jpg","-boxes.jpg")
            print "\nSaving:  ", newImageName,"\n"
            cv2.imwrite(newImageName,newImage)
        
        ##Calculating the mean and standard deviation (May not need mean
        ##not currently using it...)
        aRMean = np.mean(flatARs,0)
        aRStd = np.std(flatARs,0)

        print "Aspect Ratio Mean:  ", aRMean, "  Std:  ", aRStd
            
        target_size = float(width/count)*float(height/count)
        #Update the sliding window size based on input data
        width, height = PlateDetector.bestWindow(boxes, target_size=target_size)
        targetSize= int(width*height)
        targetAr= float(width)/height
        options.detection_window_size = targetSize
        print "New Width: ", width, "\tNew Height", height,"!!!"
        print "Target size:  ", targetSize, "  Target AR:  ", targetAr
        
        ##Deleting boxes with aspect ratios that are above or below the target
        ##aspect ratio plus one standard deviation.  bestWindow estimates a target
        ##aspect ratio close to (but not exactly) the mean.  This logic was borrowed
        ##from a dlib C++ HOG training example.  Not sure why they didn't just use the 
        ##mean, but this seems to work fine.
        for i,imgArs in enumerate(aspRatios):
            for boxArs in imgArs:
                if (boxArs > (targetAr +aRStd)) or (boxArs < (targetAr -aRStd)):
                    print "Deleting box ",dictARs[boxArs]
                    boxes[i].remove(dictARs[boxArs])
                    print "New boxes:  ",boxes

        #Train
        detector = dlib.train_simple_object_detector(images, boxes, options)
        # We could save this detector to disk by uncommenting the following.
        detector.save(model)

        # Now let's look at its HOG filter!
        # win_det.set_image(detector)
        # dlib.hit_enter_to_continue()
        win_det = dlib.image_window()
        win_det.set_image(detector)

        # Note that you don't have to use the XML based input to
        # test_simple_object_detector().  If you have already loaded your training
        # images and bounding boxes for the objects then you can call it as shown
        # below.
        print("\nTraining accuracy: {}".format(
            dlib.test_simple_object_detector(testImages, testBoxes, detector)))


    # Now let's run the detector over the images in the faces folder and display the
    # results.
    @staticmethod
    def detect(detector, objFolder):

        #assert isinstance(detector, dlib.simple_object_detector), "{} Must be a dlib.simple_object_detector!".format(detector)
        assert detector
        detector = dlib.simple_object_detector(detector)

        print "Showing detections on the images in {}.".format(objFolder)
        # win = dlib.image_window()
        if not os.path.exists(objFolder+"/detections"):
            os.makedirs(objFolder+"/detections")

        for f in glob.glob(os.path.join(objFolder, "*.jpg")):
            print("Processing file: {}".format(f))
            img = cv2.imread(f)
            dets = detector(img)
            baseName = f.split("/")[-1]
            print("Number of plates detected: {}".format(len(dets)))
            for k, d in enumerate(dets):
                print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
                    k, d.left(), d.top(), d.right(), d.bottom()))
              
                newImage =  objFolder+"/detections/"+baseName.replace(".jpg","-detection-"+str(k)+".jpg")
                print "Saving:  ", newImage
                cv2.imwrite(newImage,img[d.left():d.right(),d.top():d.bottom(),:])
                cv2.rectangle(img, (d.top(),d.left()), (d.bottom(),d.right()), (255, 255, 255), thickness=-3)
            maskedImage = objFolder+"/detections/"+baseName.replace(".jpg","-mask.jpg")
            print "Saving:  ", maskedImage
            cv2.imwrite(maskedImage, img)
                
                # cv2.imshow("image", img);

            # win.clear_overlay()
            # win.set_image(img)
            # win.add_overlay(dets)
            dlib.hit_enter_to_continue()
            

    @staticmethod
    def bestWindow(boxes, target_size):
        #width*#height == target_size
        #width/#height == the average aspect ratio of the elements of boxes.
        count = 1
        width = []
        height = []
        for i in boxes:
            for box in i:
                width.append(box.width())
                height.append(box.height())
                count += 1
                print "Box:   ",box, "\t Area:  ",box.area(), "\tAR:  ",float(box.width())/float(box.height())
        avgW = float(sum(width))/len(width)#int(float(width)/float(count))
        avgH = float(sum(height))/len(height)#int(float(height)/float(count))
        size = avgW*avgH
        scale = (target_size/size)**0.5
        print "Avg Width:  ",avgW, "\tAvg Height:  ", avgH, "\t Size:  ", size,"\tScale:  ", scale
      
        newW = int(avgW*scale + 0.5)
        newH = int(avgH*scale + 0.5)
        
        #Make sure the width and height never round to zero.
        if newW == 0:
            newW = 1
        if newH == 0:
            newH = 1

        return newW,newH


def main(argv):

    objFolder = argv[0]
    if not os.path.exists(unicode(objFolder)):
        print "DIRECTORY {} NOT FOUND!".format(objFolder)
        sys.exit(2)
    
    trainDir = (objFolder+"/training").replace("//","/")
    model = 'detector.svm'
    testDir = trainDir
    verbose = True
    C = 5
    threads = 4
    flip = True
    detector = None

    try:
        opts, args = getopt.getopt(argv[1:],"ht:m:v:d:",["test=","model=","threads=","fit=","verbose=","symmetric=","detect="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print '\nobjDetector.py <directory> [-t] <options> [-v] ... '
            print "-t, --testdir <directory>\t Specify the test direcoty, defaults to the training directory."
            print "-m, --model <modelOutput>\t Specifies the name of the detector model output. Defaults to 'detector.svm'"
            print "-v,--verbose <True/False>\t Verbose output during training and testing."
            print "--threads <num threads>\t Specify the number of cores on the machine to optimize training. Defaults to 4."
            print "--fit <num>\t Specific the C parameter for the SVM, defaults to 5."
            print "--symmetric <True/False>\t Boolean, specify whether to make SVM training left/right symmtric."
            print "\n-d, --detect <modelInput>\t This runs a detector on the specified directory. With the model specified"
            sys.exit()

        elif opt.lower() in ("-t", "--test"):
            testDir = arg

        elif opt.lower() in ("-m", "--model"):
            model = arg
        elif opt.lower() in ("-v", "--verbose"):
            if(arg.lower() == "false"):
                verbose = False
            else:
                verbose= True
        elif opt.lower() =="--threads":
            threads = int(arg)
        elif opt.lower() == "--fit":
            C = int(arg)
        elif opt.lower() == "--symmetric":
            if(arg.lower() == "false"):
                flip = False
            else:
                flip = True
        elif opt.lower() in ("-d","--detect"):
            detector = arg

    if detector:
        PlateDetector.detect(detector,objFolder)
        sys.exit(0)

    PlateDetector.train(trainDir,model,testDir,flip,C,threads,verbose)
##REIMPLEMENT USING THIS!!!!
    # Parse command line arguments and return the hyperparameter dictionary H.
    # H first loads the --hypes hypes.json file and is further updated with
    # additional arguments as needed.
    # '''
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--weights', default=None, type=str)
    # parser.add_argument('--gpu', default=None, type=int)
    # parser.add_argument('--hypes', required=True, type=str)
    # parser.add_argument('--logdir', default='output', type=str)
    # args = parser.parse_args()
    # with open(args.hypes, 'r') as f:
    #     H = json.load(f)
    # if args.gpu is not None:
    #     H['solver']['gpu'] = args.gpu
    # if len(H.get('exp_name', '')) == 0:
    #     H['exp_name'] = args.hypes.split('/')[-1].replace('.json', '')
    # H['save_dir'] = args.logdir + '/%s_%s' % (H['exp_name'],
    #     datetime.datetime.now().strftime('%Y_%m_%d_%H.%M'))
    # if args.weights is not None:
    #     H['solver']['weights'] = args.weights
    # train(H, test_images=[])

if __name__=="__main__":

    if len(sys.argv) < 2:
        print(
            "Give the path to the directory that contains training data as the argument to this "
            "program. For example:\n"
            "python ./objDectory.py ./data")
        exit()

    main(sys.argv[1:])

