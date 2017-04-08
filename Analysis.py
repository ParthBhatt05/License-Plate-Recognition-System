import cv2
import Chars
import Plates
import csv

BLACK = (0.0, 0.0, 0.0)
WHITE = (255.0, 255.0, 255.0)
GREEN = (0.0, 255.0, 0.0)
RED = (0.0, 0.0, 255.0)
BLUE = (255.0, 0.0, 0.0)

showSteps = False

class PossiblePlate:
    def __init__(self):
        self.imgPlate = None
        self.imgGrayscale = None
        self.imgThresh = None
        self.Location = None
        self.strChars = ""

def Delineate(imgOriginalScene, licPlate):
    p2fRectPoints = cv2.boxPoints(licPlate.Location)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), BLUE, 1)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), BLUE, 1)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), BLUE, 1)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), BLUE, 1)

def main():
    err= [0] * 11
    tot=0
    imgOriginalScene = cv2.imread("7.png")
    cv2.imshow("Original Image", imgOriginalScene)
    n=cv2.waitKey(0)
    cv2.destroyWindow("imgOriginalScene")
    strplate = str(input("Enter the original plate: "))
    err[0] = 1
    for k in range (1,11):
        print("for k =" +str(k)+"\n")
        Chars.knnvalue=int(k)
        Chars.Train()
        ArrayPossiblePlates = Chars.Detect(Plates.Detect(imgOriginalScene))
        if len(ArrayPossiblePlates) == 0:
            print ("\nno license plates were detected\n")
        else:
            ArrayPossiblePlates.sort(key = lambda possiblePlate: len(possiblePlate.strChars), reverse = True)
            for licPlate in ArrayPossiblePlates:
                    if len(licPlate.strChars) >= 5:
                        x=imgOriginalScene.copy()
                        Delineate(x, licPlate)
                        plate=str(licPlate.strChars)
                        cv2.imshow("Original Image", x)
                        q=cv2.waitKey(0)
                        if (q!=27 and q!=0):
                            cv2.destroyWindow("Original Image")
                            cv2.destroyWindow("Cropped Image")
                            print("\nlicense plate read from image = " + licPlate.strChars + "\n")
                            if len(strplate)<=len(plate):
                                for i in range(len(strplate)):
                                    if (strplate[i]=='O' and plate[i]=='0'):
                                        err[k] = err[k] +1
                                        err[k] = err[k] - 1
                                    elif (strplate[i] != plate[i]):
                                        err[k] = err[k] + 1
                                err[k]=err[k]+len(plate)-len(strplate)
                            elif len(strplate)>len(plate):
                                for i in range(len(plate)):
                                    if (strplate[i]!=plate[i]):
                                        err[k]=err[k]+1
                                err[k] = err[k] + len(strplate) - len(plate)
                            err[k] = float (err[k] / len(strplate))
                            print("error in detection is "+str(err[k]))
        tot=float(tot+err[k])
    tot=float(tot/6)
    least=err.index(min(err))
    print("total average error is " +str(tot))
    print("least error observed is " +str(min(err))+ " for k = "+str(least)+"")
    err[0] = strplate
    with open("output.csv", "a+") as f:
        writer = csv.writer(f)
        writer.writerows(map(lambda x: [x], err))
    f.close()

if __name__ == "__main__":
    main()