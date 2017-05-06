import cv2
import math
import Preprocess
import Chars
import numpy as np
import random
import System
import tkinter

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
    ListPossibleChars = []
    intCount = 0
    imgThreshCopy = imgThresh.copy()
    imgContours, contours, npaHierarchy = cv2.findContours(imgThreshCopy, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for i in range(0, len(contours)):
        cv2.drawContours(imgContours, contours, i, System.WHITE)
    pc = PossibleChar(contours[i])
    if Chars.Check(pc):
        intCount = intCount + 1
        ListPossibleChars.append(pc)
    tkinter.messagebox.showinfo("", "step 2 - len(contours) = " + str(
        len(contours) + "\n step 2 - intCountOfPossibleChars = " + str(intCount)))
    cv2.imshow("2a", imgContours)
    return ListPossibleChars


def Extract_Plate(imgOriginal, ListMatchingChars):
    pp = PossiblePlate()
    ListMatchingChars.sort(key=lambda matchingChar: matchingChar.intCenterX)
    PlateCenterX = (ListMatchingChars[0].intCenterX + ListMatchingChars[
        len(ListMatchingChars) - 1].intCenterX) / 2.0
    PlateCenterY = (ListMatchingChars[0].intCenterY + ListMatchingChars[
        len(ListMatchingChars) - 1].intCenterY) / 2.0
    ptPlateCenter = PlateCenterX, PlateCenterY
    intPlateWidth = int((ListMatchingChars[len(ListMatchingChars) - 1].intRectangleX + ListMatchingChars[
        len(ListMatchingChars) - 1].intRectangleWidth - ListMatchingChars[0].intRectangleX) * WIDTH_PADDING)
    intTotalOfCharHeights = 0
    for matchingChar in ListMatchingChars:
        intTotalOfCharHeights = intTotalOfCharHeights + matchingChar.intRectangleHeight
    AverageCharHeight = intTotalOfCharHeights / len(ListMatchingChars)
    intPlateHeight = int(AverageCharHeight * HEIGHT_PADDING)
    Opposite = ListMatchingChars[len(ListMatchingChars) - 1].intCenterY - ListMatchingChars[0].intCenterY
    Hypotenuse = Chars.Distance(ListMatchingChars[0], ListMatchingChars[len(ListMatchingChars) - 1])
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
    ListPossiblePlates = []
    height, width, numChannels = imgOriginalScene.shape
    cv2.destroyAllWindows()
    cv2.imshow("0", imgOriginalScene)
    imgGrayscaleScene, imgThreshScene = Preprocess.Process(imgOriginalScene)
    cv2.imshow("1a", imgGrayscaleScene)
    cv2.imshow("1b", imgThreshScene)
    ListPossibleCharsInScene = findPossibleCharsInScene(imgThreshScene)
    tkinter.messagebox.showinfo("", "step 2 - length of List Of Possible Chars In Scene) = " + str(
        len(ListPossibleCharsInScene)))
    imgContours = np.zeros((height, width, 3), np.uint8)
    contours = []
    for possibleChar in ListPossibleCharsInScene:
        contours.append(possibleChar.contour)
    cv2.drawContours(imgContours, contours, -1, System.WHITE)
    cv2.imshow("2b", imgContours)
    ListofList_MatchingCharsInScene = Chars.MatchList(ListPossibleCharsInScene)
    tkinter.messagebox.showinfo("", "step 3 - Count Of List Of Lists Of Matching Chars In Scene = " + str(
        len(ListofList_MatchingCharsInScene)))
    imgContours = np.zeros((height, width, 3), np.uint8)
    for ListOfMatchingChars in ListofList_MatchingCharsInScene:
        intRandomBlue = random.randint(0, 255)
        intRandomGreen = random.randint(0, 255)
        intRandomRed = random.randint(0, 255)
        contours = []
        for matchingChar in ListOfMatchingChars:
            contours.append(matchingChar.contour)
        cv2.drawContours(imgContours, contours, -1, (intRandomBlue, intRandomGreen, intRandomRed))
    cv2.imshow("3", imgContours)
    for ListMatchingChars in ListofList_MatchingCharsInScene:
        possiblePlate = Extract_Plate(imgOriginalScene, ListMatchingChars)
        if possiblePlate.imgPlate is not None:
            ListPossiblePlates.append(possiblePlate)
    cv2.imshow("4a", imgContours)
    for i in range(0, len(ListPossiblePlates)):
        p2fRectPoints = cv2.boxPoints(ListPossiblePlates[i].rrLocationOfPlateInScene)
        cv2.line(imgContours, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), System.RED, 1)
        cv2.line(imgContours, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), System.RED, 1)
        cv2.line(imgContours, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), System.RED, 1)
        cv2.line(imgContours, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), System.RED, 1)
        cv2.imshow("4a", imgContours)
        tkinter.messagebox.showinfo("", "possible plate " + str(i))
        cv2.imshow("4b", ListPossiblePlates[i].imgPlate)
        cv2.waitKey(0)
    return ListPossiblePlates
