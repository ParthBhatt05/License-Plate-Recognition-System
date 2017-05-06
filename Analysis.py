import cv2
import Chars
import Plates
import sqlite3
import numpy as np
import tkinter

global path
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
    Database = sqlite3.connect('Plates.db')
    err = [0] * 11
    tot = 0
    imgOriginalScene = cv2.imread(path)
    if imgOriginalScene is None:
        tkinter.messagebox.showwarning("Error", "image cannot read from file")
        np.os.system("pause")
        return
    cv2.imshow("Original Image", imgOriginalScene)
    n = cv2.waitKey(0)
    cv2.destroyWindow("Original Image")
    master = tkinter.Tk()
    tkinter.Label(master, text="Enter the Original Plate").grid(row=0)
    e1 = tkinter.Entry(master)
    e1.grid(row=0, column=1)
    tkinter.Button(master, text='Okay', command=master.quit).grid(row=1, column=0, sticky=tkinter.W, pady=4)
    tkinter.mainloop()
    strplate = str(e1.get())
    err[0] = 1
    for k in range(1, 11):
        Chars.knnvalue = int(k)
        Result = Chars.Train()
        if Result == False:
            tkinter.messagebox.showwarning("Error", "KNN training was not successful")
            return
        ArrayPossiblePlates = Chars.Detect(Plates.Detect(imgOriginalScene))
        if len(ArrayPossiblePlates) == 0:
            print("\nno license plates were detected\n")
        else:
            ArrayPossiblePlates.sort(key=lambda possiblePlate: len(possiblePlate.strChars), reverse=True)
            for licPlate in ArrayPossiblePlates:
                if len(licPlate.strChars) >= 5:
                    x = imgOriginalScene.copy()
                    Delineate(x, licPlate)
                    plate = str(licPlate.strChars)
                    cv2.imshow("Cropped Image", x)
                    q = cv2.waitKey(0)
                    if (q != 27 and q != 0):
                        cv2.destroyWindow("Original Image")
                        cv2.destroyWindow("Cropped Image")
                        tkinter.messagebox.showinfo("license plate read from image is ", licPlate.strChars)
                        if len(strplate) <= len(plate):
                            for i in range(len(strplate)):
                                if (strplate[i] == 'O' and plate[i] == '0'):
                                    err[k] = err[k] + 1
                                    err[k] = err[k] - 1
                                elif (strplate[i] != plate[i]):
                                    err[k] = err[k] + 1
                            err[k] = err[k] + len(plate) - len(strplate)
                        elif len(strplate) > len(plate):
                            for i in range(len(plate)):
                                if (strplate[i] != plate[i]):
                                    err[k] = err[k] + 1
                            err[k] = err[k] + len(strplate) - len(plate)
                        err[k] = float(err[k] / len(strplate))
                        tkinter.messagebox.showinfo("for k =" + str(k), "error in detection is " + str(err[k]))
                        Cursort = Database.execute(
                            "INSERT INTO Analysis(plateval,errorval,k) VALUES ('" + strplate + "'," + float(
                                err[k]) + "," + k + ")")
                        Database.commit();
        tot = float(tot + err[k])
    tot = float(tot / 6)
    least = err.index(min(err))
    print("total average error is " + str(tot))
    print("least error observed is " + str(min(err)) + " for k = " + str(least) + "")


if __name__ == "__main__":
    main()
