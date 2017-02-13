import glob, os
#from skimage import io
import cv2, json
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
		self.lif2json(folderIn)
		self.loadFiles(folderIn)
		if self.imageNames:
			img2Json = lambda i: i.replace("."+i.split(".")[-1],"-labels.json")
			for i in self.imageNames:
				self.boxes.append(BoundingBoxes(img2Json(i)).calcBB()) 
			print "Bounding boxes:  ", self.boxes

	#Convert .lif file to .json files if used older version of lable me.
	def lif2json(self,dir):
		for pathAndFilename in glob.iglob(os.path.join(dir, "*.lif")):
			os.rename(pathAndFilename, pathAndFilename.replace(".lif",".json"))


	#Saves to a JSON file that lists image path and rectangles
	def saveTraining(self, outfile):
		images=[]
		for i,img in enumerate(self.imageNames):
			imgi = {}
			imgi["image_path"] = img
			imgi["rects"] = []
			for box in self.boxes[i]:
				rect = {}
				rect["x1"]=box.left()
				rect["x2"]=box.right()
				rect["y1"]=box.top()
				rect["y2"]=box.bottom()
				imgi["rects"].append(rect)
			images.append(imgi)
		with open(outfile,'wb') as f:
			json.dump(images,f, ensure_ascii=True, indent=2)
			f.close()

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