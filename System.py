import cv2
import sqlite3
import Chars
import Plates
import datetime
import Train
import tkinter.messagebox
import numpy as np

BLACK = (0.0, 0.0, 0.0)
WHITE = (255.0, 255.0, 255.0)
GREEN = (0.0, 255.0, 0.0)
RED = (0.0, 0.0, 255.0)
BLUE = (255.0, 0.0, 0.0)

global path


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
    y1 = int(p2fRectPoints[0][1])
    x0 = int(p2fRectPoints[0][0])
    y0 = int(p2fRectPoints[2][1])
    x1 = int(p2fRectPoints[2][0])
    return imgOriginalScene[y0 + 1:y1 - 1, x0 + 1:x1 - 1]


def main():
    Chars.knnvalue = 1
    Result = Chars.Train()
    if Result == False:
        tkinter.messagebox.showwarning("Error", "KNN training was not successful")
        return
    imgOriginalScene = cv2.imread(path)
    if imgOriginalScene is None:
        tkinter.messagebox.showwarning("Error", "Invalid Image")
        np.os.system("pause")
        return
    ListPossiblePlates = Chars.Detect(Plates.Detect(imgOriginalScene))
    if len(ListPossiblePlates) == 0:
        cv2.imshow("imgOriginalScene", imgOriginalScene)
        print("\nno license plates were detected\n")
        cv2.destroyWindow("imgOriginalScene")
    else:
        Database = sqlite3.connect('Plates.db')
        ListPossiblePlates.sort(key=lambda possiblePlate: len(possiblePlate.strChars), reverse=True)
        for licPlate in ListPossiblePlates:
            if len(licPlate.strChars) >= 5:
                x = imgOriginalScene.copy()
                temp = Delineate(x, licPlate)
                cv2.imshow("Original Image", x)
                q = cv2.waitKey(0)
                if (q != 27 and q != 0):
                    Fine = 0
                    cv2.destroyWindow("Original Image")
                    Cursor = Database.execute("SELECT * from Details where PLATE='" + licPlate.strChars + "'")
                    Cursorr = Database.execute("SELECT count(*) from Details where PLATE='" + licPlate.strChars + "'")
                    (number_of_rows,) = Cursorr.fetchone()
                    if (number_of_rows == 1):
                        for row in Cursor:
                            tkinter.messagebox.showinfo("Plate:" + str(row[0]), "Name:" + str(row[1]))
                            Name = str(row[1])
                    else:
                        tkinter.messagebox.showinfo("Plate:" + licPlate.strChars + "not registered",
                                                    "Enter the Details")
                        master = tkinter.Tk()
                        tkinter.Label(master, text="Name").grid(row=0)
                        tkinter.Label(master, text="Phone Number").grid(row=1)
                        tkinter.Label(master, text="Address").grid(row=2)
                        tkinter.Label(master, text="License").grid(row=3)
                        tkinter.Label(master, text="Vehicle").grid(row=4)
                        e1 = tkinter.Entry(master)
                        e2 = tkinter.Entry(master)
                        e3 = tkinter.Entry(master)
                        e4 = tkinter.Entry(master)
                        e5 = tkinter.Entry(master)
                        e1.grid(row=0, column=1)
                        e2.grid(row=1, column=1)
                        e3.grid(row=2, column=1)
                        e4.grid(row=3, column=1)
                        e5.grid(row=4, column=1)
                        tkinter.Button(master, text='Submit', command=master.quit).grid(row=5, column=0,
                                                                                        sticky=tkinter.W,
                                                                                        pady=4)
                        tkinter.mainloop()
                        Name = str(e1.get())
                        Phoneno = str(e2.get())
                        Address = str(e3.get())
                        License = str(e4.get())
                        Vehicle = str(e5.get())
                        Cursort = Database.execute(
                            "INSERT INTO Details(PLATE,NAME,PHONE_No,License,Address,Vehicle_Type) VALUES ('" + licPlate.strChars + "','" + Name + "'," + Phoneno + ",'" + License + "','" + Address + "','" + Vehicle + "')")
                        Database.commit()
                    master2 = tkinter.Tk()
                    tkinter.Label(master2, text="Enter the Offense Committed").grid(row=0)
                    e1 = tkinter.Entry(master2)
                    e1.grid(row=0, column=1)
                    tkinter.Button(master2, text='Submit', command=master2.quit).grid(row=1, column=0, sticky=tkinter.W,
                                                                                      pady=4)
                    tkinter.mainloop()
                    Offense = str(e1.get()).lower()
                    Cursorq = Database.execute("SELECT fine from Offense where Offense='" + Offense + "'")
                    Fine = str(Cursorq.fetchone()).replace(",", "")
                    Cursoru = Database.execute(
                        "INSERT INTO Fine (PLATE,NAME,FINE,TIME) VALUES ('" + licPlate.strChars + "','" + str(
                            Name) + "'," + Fine + ",'" + str(datetime.datetime.now()) + "')")
                    Database.commit()
                elif (q == 0):
                    cv2.imwrite('temp.png', temp)
                    cv2.destroyWindow("Cropped Image")
                    Train.Train_Data("temp.png")
    Database.close()
    return


if __name__ == "__main__":
    main()
