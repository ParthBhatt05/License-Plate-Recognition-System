import cv2
import math
import Preprocess
import Chars

WIDTH_PADDING = 1.3
HEIGHT_PADDING = 1.5

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

def findPossibleCharsInScene(imgThresh):
    ArrayPossibleChars = []
    intCount = 0
    imgThreshCopy = imgThresh.copy()
    imgContours, contours, npaHierarchy = cv2.findContours(imgThreshCopy, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for i in range(0, len(contours)):
        pc = PossibleChar(contours[i])
        if Chars.Check(pc):
            intCount = intCount + 1
            ArrayPossibleChars.append(pc)
    return ArrayPossibleChars

def Extract_Plate(imgOriginal, ArrayMatchingChars):
    pp = PossiblePlate()
    ArrayMatchingChars.sort(key=lambda matchingChar: matchingChar.intCenterX)
    PlateCenterX = (ArrayMatchingChars[0].intCenterX + ArrayMatchingChars[
        len(ArrayMatchingChars) - 1].intCenterX) / 2.0
    PlateCenterY = (ArrayMatchingChars[0].intCenterY + ArrayMatchingChars[
        len(ArrayMatchingChars) - 1].intCenterY) / 2.0
    ptPlateCenter = PlateCenterX, PlateCenterY
    intPlateWidth = int((ArrayMatchingChars[len(ArrayMatchingChars) - 1].intRectangleX + ArrayMatchingChars[
        len(ArrayMatchingChars) - 1].intRectangleWidth - ArrayMatchingChars[0].intRectangleX) * WIDTH_PADDING)
    intTotalOfCharHeights = 0
    for matchingChar in ArrayMatchingChars:
        intTotalOfCharHeights = intTotalOfCharHeights + matchingChar.intRectangleHeight
    AverageCharHeight = intTotalOfCharHeights / len(ArrayMatchingChars)
    intPlateHeight = int(AverageCharHeight * HEIGHT_PADDING)
    Opposite = ArrayMatchingChars[len(ArrayMatchingChars) - 1].intCenterY - ArrayMatchingChars[0].intCenterY
    Hypotenuse = Chars.Distance(ArrayMatchingChars[0], ArrayMatchingChars[len(ArrayMatchingChars) - 1])
    CorrectionRad = math.asin(Opposite / Hypotenuse)
    CorrectionDeg = CorrectionRad * (180.0 / math.pi)
    pp.Location = (tuple(ptPlateCenter), (intPlateWidth, intPlateHeight), CorrectionDeg)
    rotationMatrix = cv2.getRotationMatrix2D(tuple(ptPlateCenter), CorrectionDeg, 1.0)
    height, width, numChannels = imgOriginal.shape
    imgRotated = cv2.warpAffine(imgOriginal, rotationMatrix, (width, height))
    imgCropped = cv2.getRectSubPix(imgRotated, (intPlateWidth, intPlateHeight), tuple(ptPlateCenter))
    pp.imgPlate = imgCropped
    return pp

def Detect(imgOriginalScene):
    ArrayPossiblePlates = []
    cv2.destroyAllWindows()
    imgGrayscaleScene, imgThreshScene = Preprocess.Process(imgOriginalScene)
    ArrayPossibleCharsInScene = findPossibleCharsInScene(imgThreshScene)
    ArrayofArray_MatchingCharsInScene = Chars.MatchList(ArrayPossibleCharsInScene)
    for ArrayMatchingChars in ArrayofArray_MatchingCharsInScene:
        possiblePlate = Extract_Plate(imgOriginalScene, ArrayMatchingChars)
        if possiblePlate.imgPlate is not None:
            ArrayPossiblePlates.append(possiblePlate)
    return ArrayPossiblePlates