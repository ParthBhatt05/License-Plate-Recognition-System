import cv2
import numpy as np
import math
import Main
import Preprocess

global knnvalue
kNearest = cv2.ml.KNearest_create()

MAX_CHANGE_IN_AREA = 0.5
MAX_CHANGE_IN_WIDTH = 0.8
MAX_CHANGE_IN_HEIGHT = 0.2
MIN_PIXEL_WIDTH = 2
MIN_PIXEL_HEIGHT = 8
MAX_ANGLE = 12.0
MIN_ASPECT_RATIO = 0.25
MAX_ASPECT_RATIO = 1.0
MIN_PIXEL_AREA = 80
MIN_DIAGONAL = 0.3
MAX_DIAGONAL = 5.0
MIN_CONTOUR_AREA = 100

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

def Train():
    Classifications = np.loadtxt("classifications.txt",np.float32)
    FlattenedImages = np.loadtxt("flattened_images.txt",np.float32)
    Classifications = Classifications.reshape((Classifications.size, 1))
    kNearest.setDefaultK(int(knnvalue))
    kNearest.train(FlattenedImages, cv2.ml.ROW_SAMPLE, Classifications)

def Check(possibleChar):
    if (possibleChar.intRectangleArea > MIN_PIXEL_AREA and possibleChar.intRectangleWidth > MIN_PIXEL_WIDTH and possibleChar.intRectangleHeight > MIN_PIXEL_HEIGHT and MIN_ASPECT_RATIO < possibleChar.AspectRatio and possibleChar.AspectRatio < MAX_ASPECT_RATIO):
        return True
    else:
        return False

def Distance(firstChar, secondChar):
    intX = abs(firstChar.intCenterX - secondChar.intCenterX)
    intY = abs(firstChar.intCenterY - secondChar.intCenterY)
    return math.sqrt((intX ** 2) + (intY ** 2))

def Angle(firstChar, secondChar):
    Adj = float(abs(firstChar.intCenterX - secondChar.intCenterX))
    Opp = float(abs(firstChar.intCenterY - secondChar.intCenterY))
    if Adj != 0.0:
        AngleInRad = math.atan(Opp / Adj)
    else:
        AngleInRad = 1.5708
    AngleInDeg = AngleInRad * (180.0 / math.pi)
    return AngleInDeg

def Search(imgThresh):
    ArrayPossibleChars = []
    imgContours, contours, Hierarchy = cv2.findContours(imgThresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        pc = PossibleChar(contour)
        if Check(pc):
            ArrayPossibleChars.append(pc)
    return ArrayPossibleChars

def Matches(possibleChar, ArrayChars):
    ArrayMatchingChars = []
    for possibleMatchingChar in ArrayChars:
        if possibleMatchingChar == possibleChar:
            continue
        DistanceBetweenChars = Distance(possibleChar, possibleMatchingChar)
        AngleBetweenChars = Angle(possibleChar, possibleMatchingChar)
        ChangeInArea = float(abs(possibleMatchingChar.intRectangleArea - possibleChar.intRectangleArea)) / float(possibleChar.intRectangleArea)
        ChangeInWidth = float(abs(possibleMatchingChar.intRectangleWidth - possibleChar.intRectangleWidth)) / float(possibleChar.intRectangleWidth)
        ChangeInHeight = float(abs(possibleMatchingChar.intRectangleHeight - possibleChar.intRectangleHeight)) / float(possibleChar.intRectangleHeight)
        if (DistanceBetweenChars < (possibleChar.Diagonal * MAX_DIAGONAL) and
            AngleBetweenChars < MAX_ANGLE and
            ChangeInArea < MAX_CHANGE_IN_AREA and
            ChangeInWidth < MAX_CHANGE_IN_WIDTH and
            ChangeInHeight < MAX_CHANGE_IN_HEIGHT):
            ArrayMatchingChars.append(possibleMatchingChar)
    return ArrayMatchingChars

def MatchList(ArrayPossibleChars):
    ArrayofArray_MatchingChars = []
    for possibleChar in ArrayPossibleChars:
        ArrayMatchingChars = Matches(possibleChar, ArrayPossibleChars)
        ArrayMatchingChars.append(possibleChar)
        if len(ArrayMatchingChars) < 3:
            continue
        ArrayofArray_MatchingChars.append(ArrayMatchingChars)
        recursiveArrayofArray_MatchingChars = MatchList(list(set(ArrayPossibleChars) - set(ArrayMatchingChars)))
        for rArrayMatchingChars in recursiveArrayofArray_MatchingChars:
            ArrayofArray_MatchingChars.append(rArrayMatchingChars)
        break
    return ArrayofArray_MatchingChars

def Overlap(ArrayMatchingChars):
    ArrayMatchingChars2 = list(ArrayMatchingChars)
    for currentChar in ArrayMatchingChars:
        for otherChar in ArrayMatchingChars:
            if currentChar != otherChar:
                if Distance(currentChar, otherChar) < (currentChar.Diagonal * MIN_DIAGONAL):
                    if currentChar.intRectangleArea < otherChar.intRectangleArea:
                        if currentChar in ArrayMatchingChars2:
                            ArrayMatchingChars2.remove(currentChar)
                    else:
                        if otherChar in ArrayMatchingChars2:
                            ArrayMatchingChars2.remove(otherChar)
    return ArrayMatchingChars2

def Recognize(imgThresh, ArrayMatchingChars):
    strChars = ""
    height, width = imgThresh.shape
    imgThreshColor = np.zeros((height, width, 3), np.uint8)
    ArrayMatchingChars.sort(key = lambda matchingChar: matchingChar.intCenterX)
    cv2.cvtColor(imgThresh, cv2.COLOR_GRAY2BGR, imgThreshColor)
    for currentChar in ArrayMatchingChars:
        pt1 = (currentChar.intRectangleX, currentChar.intRectangleY)
        pt2 = ((currentChar.intRectangleX + currentChar.intRectangleWidth), (currentChar.intRectangleY + currentChar.intRectangleHeight))
        cv2.rectangle(imgThreshColor, pt1, pt2, Main.GREEN, 2)
        imgROI = imgThresh[currentChar.intRectangleY : currentChar.intRectangleY + currentChar.intRectangleHeight,
                           currentChar.intRectangleX : currentChar.intRectangleX + currentChar.intRectangleWidth]
        imgROIResized = cv2.resize(imgROI, (20, 30))
        ROIResized = imgROIResized.reshape((1, 600))
        ROIResized = np.float32(ROIResized)
        x, Results, y, z = kNearest.findNearest(ROIResized, int(knnvalue))
        strCurrentChar = str(chr(int(Results[0][0])))
        strChars = strChars + strCurrentChar
    return strChars

def Detect(ArrayPossiblePlates):
    if len(ArrayPossiblePlates) == 0:
        return ArrayPossiblePlates
    for possiblePlate in ArrayPossiblePlates:
        possiblePlate.imgGrayscale, possiblePlate.imgThresh = Preprocess.Process(possiblePlate.imgPlate)
        possiblePlate.imgThresh = cv2.resize(possiblePlate.imgThresh, (0, 0), fx = 1.6, fy = 1.6)
        thresholdValue, possiblePlate.imgThresh = cv2.threshold(possiblePlate.imgThresh, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        ArrayofArray_MatchingCharacters = MatchList(Search(possiblePlate.imgThresh))
        if (len(ArrayofArray_MatchingCharacters) == 0):
            possiblePlate.strChars = ""
            continue
        for i in range(0, len(ArrayofArray_MatchingCharacters)):
            ArrayofArray_MatchingCharacters[i].sort(key = lambda matchingChar: matchingChar.intCenterX)
            ArrayofArray_MatchingCharacters[i] = Overlap(ArrayofArray_MatchingCharacters[i])
        intLenOfLongestArrayChars = 0
        intIndex = 0
        for i in range(0, len(ArrayofArray_MatchingCharacters)):
            if len(ArrayofArray_MatchingCharacters[i]) > intLenOfLongestArrayChars:
                intLenOfLongestArrayChars = len(ArrayofArray_MatchingCharacters[i])
                intIndex = i
        longestArrayMatchingCharsInPlate = ArrayofArray_MatchingCharacters[intIndex]
        possiblePlate.strChars = Recognize(possiblePlate.imgThresh, longestArrayMatchingCharsInPlate)
    return ArrayPossiblePlates