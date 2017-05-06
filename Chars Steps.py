import cv2
import numpy as np
import math
import System
import Preprocess
import tkinter
import random

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
    try:
        Classifications = np.loadtxt("classifications.txt", np.float32)
    except:
        tkinter.messagebox.showwarning("Error", "unable to open classifications.txt")
        np.os.system("pause")
        return False
    try:
        FlattenedImages = np.loadtxt("flattened_images.txt", np.float32)
    except:
        tkinter.messagebox.showwarning("Error", "unable to open flattened_images.txt")
        np.os.system("pause")
        return False
    Classifications = Classifications.reshape((Classifications.size, 1))
    kNearest.setDefaultK(int(knnvalue))
    kNearest.train(FlattenedImages, cv2.ml.ROW_SAMPLE, Classifications)


def Check(possibleChar):
    if (
                                possibleChar.intRectangleArea > MIN_PIXEL_AREA and possibleChar.intRectangleWidth > MIN_PIXEL_WIDTH and possibleChar.intRectangleHeight > MIN_PIXEL_HEIGHT and MIN_ASPECT_RATIO < possibleChar.AspectRatio and possibleChar.AspectRatio < MAX_ASPECT_RATIO):
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
    ListPossibleChars = []
    imgContours, contours, Hierarchy = cv2.findContours(imgThresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        pc = PossibleChar(contour)
        if Check(pc):
            ListPossibleChars.append(pc)
    return ListPossibleChars


def Matches(possibleChar, ListChars):
    ListMatchingChars = []
    for possibleMatchingChar in ListChars:
        if possibleMatchingChar == possibleChar:
            continue
        DistanceBetweenChars = Distance(possibleChar, possibleMatchingChar)
        AngleBetweenChars = Angle(possibleChar, possibleMatchingChar)
        ChangeInArea = float(abs(possibleMatchingChar.intRectangleArea - possibleChar.intRectangleArea)) / float(
            possibleChar.intRectangleArea)
        ChangeInWidth = float(abs(possibleMatchingChar.intRectangleWidth - possibleChar.intRectangleWidth)) / float(
            possibleChar.intRectangleWidth)
        ChangeInHeight = float(abs(possibleMatchingChar.intRectangleHeight - possibleChar.intRectangleHeight)) / float(
            possibleChar.intRectangleHeight)
        if (DistanceBetweenChars < (possibleChar.Diagonal * MAX_DIAGONAL) and
                    AngleBetweenChars < MAX_ANGLE and
                    ChangeInArea < MAX_CHANGE_IN_AREA and
                    ChangeInWidth < MAX_CHANGE_IN_WIDTH and
                    ChangeInHeight < MAX_CHANGE_IN_HEIGHT):
            ListMatchingChars.append(possibleMatchingChar)
    return ListMatchingChars


def MatchList(ListPossibleChars):
    ListofList_MatchingChars = []
    for possibleChar in ListPossibleChars:
        ListMatchingChars = Matches(possibleChar, ListPossibleChars)
        ListMatchingChars.append(possibleChar)
        if len(ListMatchingChars) < 3:
            continue
        ListofList_MatchingChars.append(ListMatchingChars)
        recursiveListofList_MatchingChars = MatchList(list(set(ListPossibleChars) - set(ListMatchingChars)))
        for rListMatchingChars in recursiveListofList_MatchingChars:
            ListofList_MatchingChars.append(rListMatchingChars)
        break
    return ListofList_MatchingChars


def Overlap(ListMatchingChars):
    ListMatchingChars2 = list(ListMatchingChars)
    for currentChar in ListMatchingChars:
        for otherChar in ListMatchingChars:
            if currentChar != otherChar:
                if Distance(currentChar, otherChar) < (currentChar.Diagonal * MIN_DIAGONAL):
                    if currentChar.intRectangleArea < otherChar.intRectangleArea:
                        if currentChar in ListMatchingChars2:
                            ListMatchingChars2.remove(currentChar)
                    else:
                        if otherChar in ListMatchingChars2:
                            ListMatchingChars2.remove(otherChar)
    return ListMatchingChars2


def Recognize(imgThresh, ListMatchingChars):
    strChars = ""
    height, width = imgThresh.shape
    imgThreshColor = np.zeros((height, width, 3), np.uint8)
    ListMatchingChars.sort(key=lambda matchingChar: matchingChar.intCenterX)
    cv2.cvtColor(imgThresh, cv2.COLOR_GRAY2BGR, imgThreshColor)
    for currentChar in ListMatchingChars:
        pt1 = (currentChar.intRectangleX, currentChar.intRectangleY)
        pt2 = ((currentChar.intRectangleX + currentChar.intRectangleWidth),
               (currentChar.intRectangleY + currentChar.intRectangleHeight))
        cv2.rectangle(imgThreshColor, pt1, pt2, System.GREEN, 2)
        imgROI = imgThresh[currentChar.intRectangleY: currentChar.intRectangleY + currentChar.intRectangleHeight,
                 currentChar.intRectangleX: currentChar.intRectangleX + currentChar.intRectangleWidth]
        imgROIResized = cv2.resize(imgROI, (20, 30))
        ROIResized = imgROIResized.reshape((1, 600))
        ROIResized = np.float32(ROIResized)
        x, Results, y, z = kNearest.findNearest(ROIResized, int(knnvalue))
        strCurrentChar = str(chr(int(Results[0][0])))
        strChars = strChars + strCurrentChar
    cv2.imshow("10", imgThreshColor)
    return strChars


def Detect(ListPossiblePlates):
    contours = []
    intPlateCount = 0
    if len(ListPossiblePlates) == 0:
        return ListPossiblePlates
    for possiblePlate in ListPossiblePlates:
        possiblePlate.imgGrayscale, possiblePlate.imgThresh = Preprocess.Process(possiblePlate.imgPlate)
        cv2.imshow("5a", possiblePlate.imgPlate)
        cv2.imshow("5b", possiblePlate.imgGrayscale)
        cv2.imshow("5c", possiblePlate.imgThresh)
        possiblePlate.imgThresh = cv2.resize(possiblePlate.imgThresh, (0, 0), fx=1.6, fy=1.6)
        thresholdValue, possiblePlate.imgThresh = cv2.threshold(possiblePlate.imgThresh, 0.0, 255.0,
                                                                cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        cv2.imshow("5d", possiblePlate.imgThresh)
        ListofList_MatchingCharacters = MatchList(Search(possiblePlate.imgThresh))
        height, width, numChannels = possiblePlate.imgPlate.shape
        imgContours = np.zeros((height, width, 3), np.uint8)
        del contours[:]
        for possibleChar in Search(possiblePlate.imgThresh):
            contours.append(possibleChar.contour)
        cv2.drawContours(imgContours, contours, -1, System.WHITE)
        cv2.imshow("6", imgContours)
        imgContours = np.zeros((height, width, 3), np.uint8)
        del contours[:]
        for ListMatchingChars in ListofList_MatchingCharacters:
            intRandomBlue = random.randint(0, 255)
            intRandomGreen = random.randint(0, 255)
            intRandomRed = random.randint(0, 255)
            for matchingChar in ListMatchingChars:
                contours.append(matchingChar.contour)
            cv2.drawContours(imgContours, contours, -1, (intRandomBlue, intRandomGreen, intRandomRed))
        cv2.imshow("7", imgContours)
        if (len(ListofList_MatchingCharacters) == 0):
            tkinter.messagebox.showinfo("", "Characters found in plate number " + str(
                intPlateCount) + " = (none)")
            intPlateCount = intPlateCount + 1
            cv2.destroyWindow("8")
            cv2.destroyWindow("9")
            cv2.destroyWindow("10")
            cv2.waitKey(0)
            possiblePlate.strChars = ""
            continue
        for i in range(0, len(ListofList_MatchingCharacters)):
            ListofList_MatchingCharacters[i].sort(key=lambda matchingChar: matchingChar.intCenterX)
            ListofList_MatchingCharacters[i] = Overlap(ListofList_MatchingCharacters[i])
        imgContours = np.zeros((height, width, 3), np.uint8)
        for ListOfMatchingChars in ListofList_MatchingCharacters:
            intRandomBlue = random.randint(0, 255)
            intRandomGreen = random.randint(0, 255)
            intRandomRed = random.randint(0, 255)
            del contours[:]
            for matchingChar in ListOfMatchingChars:
                contours.append(matchingChar.contour)
            cv2.drawContours(imgContours, contours, -1, (intRandomBlue, intRandomGreen, intRandomRed))
        cv2.imshow("8", imgContours)
        intLenOfLongestListChars = 0
        intIndex = 0
        for i in range(0, len(ListofList_MatchingCharacters)):
            if len(ListofList_MatchingCharacters[i]) > intLenOfLongestListChars:
                intLenOfLongestListChars = len(ListofList_MatchingCharacters[i])
                intIndex = i
        longestListMatchingCharsInPlate = ListofList_MatchingCharacters[intIndex]
        imgContours = np.zeros((height, width, 3), np.uint8)
        del contours[:]
        for matchingChar in longestListMatchingCharsInPlate:
            contours.append(matchingChar.contour)
        cv2.drawContours(imgContours, contours, -1, System.WHITE)
        cv2.imshow("9", imgContours)
        possiblePlate.strChars = Recognize(possiblePlate.imgThresh, longestListMatchingCharsInPlate)
        tkinter.messagebox.showinfo("", "Characters found in plate number " + str(
            intPlateCount) + " = " + possiblePlate.strChars)
        intPlateCount = intPlateCount + 1
        cv2.waitKey(0)
    return ListPossiblePlates
