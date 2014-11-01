import cv2
import sys
from decide import *
import numpy as np
sys.path.append("..")
from tinyfacerec.subspace import fisherfaces
from tinyfacerec.util import normalize, asRowMatrix, read_images
from tinyfacerec.visual import subplot


class EnvironmentVariables:
    def __init__(self):
        self.faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
        self.profileCascade = cv2.CascadeClassifier("haarcascade_profileface.xml")
        self.video_capture = cv2.VideoCapture(0)
        self.classlabel = []
        self.currentAd = cv2.imread('photos/groupmanwoman.png',1)
        self.images = []
        self.model = None
        self.prediction = 0
        #self.readCSV()
        
    def readCSV(self):
        f = open("attdb.csv", "r")
        for line in f:
            A = line.split("\s")
            self.classlabel.append(A[0])
            self.images.append(A[1])
        f.close()
        self.model = cv2.createEigenFaceRecognizer()
        self.model.train(self.images, self.classlabel)

    def isChild(self, face):
        x, y = face.size()
        area = x * y
        
    def captureVariables(self):
        numState = []
        ratioState = []
        ratio = 0
        numFace = 0
        while True:
            # Capture frame-by-frame
            ret, frame = self.video_capture.read()

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            facesFront = self.faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                #flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )

            facesProfile = self.profileCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                #flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )
            numFace = len(facesFront) + len(facesProfile)
            print str(numFace)
            if(len(numState) < 4):
                numState.append(numFace)
                ratioState.append(0.5)
            else:
                a = deltaR(ratioState)
                b = delta(numState)
                numState = []
                ratioState = []
                if(a >= 0.6):
                    numFace = b
                ratio = a
            fisher()  
            d = Decide(ratio, numFace)
            self.currentAd = d.getFilePath()
            # Draw a rectangle around the faces
            for (x, y, w, h) in facesFront:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Display the resulting frame
            cv2.imshow('Advertisement', cv2.imread(self.currentAd,1))
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything is done, release the capture
        self.video_capture.release()
        cv2.destroyAllWindows()
    
def fisher():
        # read images
    [X,y] = read_images("base")
    # perform a full pca
    [D, W, mu] = fisherfaces(asRowMatrix(X), y)
    #import colormaps
    import matplotlib.cm as cm
    # turn the first (at most) 16 eigenvectors into grayscale
    # images (note: eigenvectors are stored by column!)
    E = []
    for i in xrange(min(W.shape[1], 16)):
	    e = W[:,i].reshape(X[0].shape)
	    E.append(normalize(e,0,255))
    # plot them and store the plot to "python_fisherfaces_fisherfaces.pdf"
    subplot(title="Fisherfaces AT&T Facedatabase", images=E, rows=4, cols=4, sptitle="Fisherface", colormap=cm.jet, filename="python_fisherfaces_fisherfaces.png")

    from tinyfacerec.subspace import project, reconstruct

    E = []
    for i in xrange(min(W.shape[1], 16)):
	    e = W[:,i].reshape(-1,1)
	    P = project(e, X[0].reshape(1,-1), mu)
	    R = reconstruct(e, P, mu)
	    # reshape and append to plots
	    R = R.reshape(X[0].shape)
	    E.append(normalize(R,0,255))
    # plot them and store the plot to "python_reconstruction.pdf"
    subplot(title="Fisherfaces Reconstruction Yale FDB", images=E, rows=4, cols=4, sptitle="Fisherface", colormap=cm.gray, filename="python_fisherfaces_reconstruction.png")

def delta(someList):
    avg = reduce(lambda x,y: x+ y, someList) / len(someList)
    return avg 

def deltaR(ratioList):
    avg = reduce(lambda x,y: x+ y, ratioList) / len(ratioList)
    return avg 
 

if __name__=="__main__":
    eV = EnvironmentVariables()
    eV.captureVariables()



    
    
