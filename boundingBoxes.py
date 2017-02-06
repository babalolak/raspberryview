import json,os
import dlib

class BoundingBoxes(object):

    def __init__(self, fileIn=None):
        if fileIn:
            self.dataFile(fileIn)

    def dataFile(self,fileIn):
        if os.path.exists(unicode(fileIn)):
            print "Getting Bounding Boxes in ", fileIn
            with open(fileIn) as f:
                self.load(json.load(f))
    def load(self, data):#ilename):

            # self.load(json.load(f, object_hook=json_util.object_hook))
            # data = json.load(f)
            imgid = data.get('_id',"")
            title = data.get('title')
           
            imagePath = data.get('imagePath')
            #imageData = b64decode(data.get('imageData',""))
            lineColor = data.get('lineColor')
            fillColor = data.get('fillColor')
            dateCreated = data.get('dateCreated')
            lastModified = data.get('lastModified')
            # shapes = ((s['_id'],s['category'], s['imgId'], s['points'], s['line_color'], s['fill_color'], s['dateCreated'], s['lastModified'])\
            #     for s in data['shapes'])
            shapes = (s['points']for s in data['shapes'])

            # Only replace data after everything is loaded.
            self.iD = str(imgid)
            self.title = title
            self.shapes = shapes
            self.imagePath = imagePath
            # self.imageData = imageData
            self.lineColor = lineColor
            self.fillColor = fillColor
            self.dateCreated = dateCreated
                    # if not self.iD:
                    #     self.iD = self.toDb(conn)
            # except Exception, e:
            #     raise LabelFileError(e)

    #Calculates the bounding boxes for 
    def calcBB(self):
        bbs = []
        for shape in self.shapes:
            x = [e[0] for e in shape]# for e in tup]
            y = [e[1] for e in shape]
            # bbs.append(dict(left=int(min(x)), top=int(max(y)), right=int(max(x)), bottom=int(min(y))))
            bbs.append(dlib.rectangle(left=int(min(x)), top=int(max(y)), right=int(max(x)), bottom=int(min(y))))

        return bbs