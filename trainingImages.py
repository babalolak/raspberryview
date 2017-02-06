import glob, os
#from skimage import io
import cv2
from boundingBoxes import BoundingBoxes

class TrainingImages(object):

	def __init__(self,folderIn=None,imagesOnly=False):
		self.imageNames = []
		self.images = []
		self.boxes = []
		if imagesOnly:
			if folderIn:
				self.loadFiles(folderIn)
		elif folderIn:
			self.loadTraining(folderIn)	

	def loadFiles(self,folderIn):
		if os.path.exists(unicode(folderIn)):
		
			self.imageNames.extend(item for i in (glob.glob(folderIn+'/*.%s' % ext) for ext in ["jpg","gif","png","tga"]) for item in i)
			self.images.extend(cv2.imread(item) for item in self.imageNames)
			print "Loaded training images.  First image title:  ", self.imageNames[0]
		else:
			print "No such folder found in file system.  Check name:  ", folderIn

	def loadTraining(self,folderIn):
		self.loadFiles(folderIn)
		if self.imageNames:
			img2Json = lambda i: i.replace("."+i.split(".")[-1],"-labels.lif")
			for i in self.imageNames:
				self.boxes.append(BoundingBoxes(img2Json(i)).calcBB()) 
			print "Bounding boxes:  ", self.boxes
		
	#Utillity to check for folder existence
	def exists(self, filename):
 		return os.path.exists(unicode(filename))

###SAMPLE CODE TO SAVE IMAGES!!!
# from PIL import Image
# im = Image.fromarray(A)
# im.save("your_file.jpeg")
# import cv2
# im = cv2.imread("abc.tiff")
# print type(im)