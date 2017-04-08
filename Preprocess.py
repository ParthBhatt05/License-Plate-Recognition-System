import cv2

FILTER_SIZE = (5, 5)
BLOCK_SIZE = 19
THRESH_WEIGHT = 9

def Extract(imgOriginal):
    imgHue, imgSaturation, imgValue = cv2.split(cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV))
    return imgValue

def Max_Contrast(imgGrayscale):
    imgTopHat = cv2.morphologyEx(imgGrayscale, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
    imgBlackHat = cv2.morphologyEx(imgGrayscale, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
    return cv2.subtract(cv2.add(imgGrayscale, imgTopHat), imgBlackHat)

def Process(imgOriginal):
    imgGrayscale = Extract(imgOriginal)
    imgThresh = cv2.adaptiveThreshold(cv2.GaussianBlur(Max_Contrast(imgGrayscale), FILTER_SIZE, 0), 255.0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, BLOCK_SIZE, THRESH_WEIGHT)
    return imgGrayscale, imgThresh