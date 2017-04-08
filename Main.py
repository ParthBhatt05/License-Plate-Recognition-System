import cv2
import sqlite3
import Chars
import Plates
import datetime
import Train

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
    y1=int(p2fRectPoints[0][1])
    x0=int(p2fRectPoints[0][0])
    y0=int(p2fRectPoints[2][1])
    x1=int(p2fRectPoints[2][0])
    return imgOriginalScene[y0+1:y1-1,x0+1:x1-1]

def main():
    Chars.knnvalue=1
    Result = Chars.Train()
    if Result == False:
        print ("\nerror: KNN traning was not successful\n")
        return
    imgOriginalScene = cv2.imread("3.png")
    ArrayPossiblePlates = Chars.Detect(Plates.Detect(imgOriginalScene))
    if len(ArrayPossiblePlates) == 0:
        cv2.imshow("imgOriginalScene", imgOriginalScene)
        print ("\nno license plates were detected\n")
        cv2.destroyWindow("imgOriginalScene")
    else:
        Database = sqlite3.connect('Plates.db')
        ArrayPossiblePlates.sort(key = lambda possiblePlate: len(possiblePlate.strChars), reverse = True)
        for licPlate in ArrayPossiblePlates:
                if len(licPlate.strChars) >= 5:
                    x=imgOriginalScene.copy()
                    temp=Delineate(x, licPlate)
                    print("\nlicense plate read from image = " + licPlate.strChars + "\n")
                    cv2.imshow("Original Image", x)
                    q=cv2.waitKey(0)
                    if (q!=27 and q!=0):
                        cv2.destroyWindow("Original Image")
                        Cursor = Database.execute("SELECT * from Details where PLATE='" + licPlate.strChars + "'")
                        Cursorr = Database.execute("SELECT count(*) from Details where PLATE='" + licPlate.strChars + "'")
                        (number_of_rows,) = Cursorr.fetchone()
                        if (number_of_rows == 1):
                            for row in Cursor:
                                print("licPlate = ", row[0])
                                print("Name = ", row[1])
                                Name = row [1]
                        else:
                            Name = input('Enter your name: ')
                            Phoneno = input('Enter your phone no.: ')
                            Address = input('Enter your address: ')
                            License = input('Enter your license no: ')
                            Vehicle = input('Enter vehicle type: ')
                            Cursort = Database.execute( "INSERT INTO Details(PLATE,NAME,PHONE_No,License,Address,Vehicle_Type) VALUES ('"+licPlate.strChars+"','"+Name+"',"+Phoneno+",'"+License+"','"+Address+"','"+Vehicle+"')")
                            Database.commit()
                        Fine = input('Enter the fine for the ticket: ')
                        Cursorf=Database.execute("INSERT INTO Fine (PLATE,NAME,FINE,TIME) VALUES ('"+licPlate.strChars+"','"+Name+"','"+Fine+"','"+str(datetime.datetime.now())+"')")
                        Database.commit()
                    elif (q== 0):
                        cv2.imwrite('temp.png', temp)
                        cv2.destroyWindow("Cropped Image")
                        Train.Train_Data("temp.png")
    Database.close()
    return

if __name__ == "__main__":
    main()