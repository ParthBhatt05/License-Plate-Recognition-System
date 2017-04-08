import sys
import numpy as np
import cv2
import Preprocess
import math
import Chars

MIN_CONTOUR_AREA = 100
RESIZED_IMAGE_WIDTH = 100
RESIZED_IMAGE_HEIGHT = 100

class PossibleChar:
    def __init__(self, _contour):
        self.contour = _contour
        self.Rectangle = cv2.boundingRect(self.contour)
        [intX, intY, intWidth, intHeight] = self.Rectangle
        self.intRectangleX = intX
        self.intRectangleY = intY
        self.intRectangleWidth = intWidth
        self.intRectangleHeight = intHeight
        self.intRectangleArea = self.intRectangleWidth * self.intRectangleHeight
        self.intCenterX = (self.intRectangleX + self.intRectangleX + self.intRectangleWidth) / 2
        self.intCenterY = (self.intRectangleY + self.intRectangleY + self.intRectangleHeight) / 2
        self.Diagonal = math.sqrt((self.intRectangleWidth ** 2) + (self.intRectangleHeight ** 2))
        self.AspectRatio = float(self.intRectangleWidth) / float(self.intRectangleHeight)

class PossiblePlate:
    def __init__(self):
        self.imgPlate = None
        self.imgGrayscale = None
        self.imgThresh = None
        self.Location = None
        self.strChars = ""

def Train_Data(train):
    f1= open("flattened_imagesa.txt", 'ab')
    f2= open("classificationsa.txt", 'ab')
    intClassifications = []
    intValidChars = [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9'),
                     ord('A'), ord('B'), ord('C'), ord('D'), ord('E'), ord('F'), ord('G'), ord('H'), ord('I'), ord('J'),
                     ord('K'), ord('L'), ord('M'), ord('N'), ord('O'), ord('P'), ord('Q'), ord('R'), ord('S'), ord('T'),
                     ord('U'), ord('V'), ord('W'), ord('X'), ord('Y'), ord('Z')]
    train = cv2.imread(str(train))
    npaFlattenedImages = np.empty((0, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
    imgGray, temp = Preprocess.Process(train)
    imgContours, npaContours, npaHierarchy = cv2.findContours(temp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    i=1
    for npaContour in npaContours:
        pc = PossibleChar(npaContour)
        if Chars.Check(pc):
            [intX, intY, intW, intH] = cv2.boundingRect(npaContour)
            test=train.copy()
            cv2.rectangle(test, (intX, intY), (intX + intW, intY + intH), (255, 0, 0), 1)
            cv2.imshow("Cropped Image", cv2.resize(train[intY:intY + intH, intX:intX + intW],(intW, intH)))
            cv2.imshow("test", test.copy())
            intChar = cv2.waitKey(0)
            cv2.destroyWindow("Cropped Image")
            if intChar == 27:
                sys.exit()
            elif intChar == 0:
                print("invalid CONTOR "+str(i)+" , skipping")
                i=i+1
            elif intChar in intValidChars:
                intClassifications.append(intChar)
                npaFlattenedImage = cv2.resize(temp[intY:intY + intH, intX:intX + intW],(RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT)).reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
                npaFlattenedImages = np.append(npaFlattenedImages, npaFlattenedImage, 0)
    fltClassifications = np.array(intClassifications,np.float32)
    npaClassifications = fltClassifications.reshape((fltClassifications.size, 1))
    np.savetxt(f2, npaClassifications)
    np.savetxt(f1, npaFlattenedImages)
    f1.close()
    f2.close()
    return

def main ():
    Train_Data("Train.png")
    #Train_Data("Chars.jpg")

if __name__ == "__main__":
    main()