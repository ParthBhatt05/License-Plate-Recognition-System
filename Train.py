import sys
import numpy as np
import cv2
import Preprocess
import math
import Chars
import tkinter
import tkinter.constants
import tkinter.filedialog

MIN_CONTOUR_AREA = 100
RESIZED_IMAGE_WIDTH = 100
RESIZED_IMAGE_HEIGHT = 100


class TkFileDialogExample(tkinter.Frame):
    def __init__(self, root):
        tkinter.Frame.__init__(self, root)
        button_opt = {'fill': tkinter.constants.BOTH, 'padx': 5, 'pady': 5}
        tkinter.Button(self, text='Open File', command=self.askopenfile).pack(**button_opt)
        self.file_opt = options = {}
        options['defaultextension'] = '.png'
        options['filetypes'] = [('all files', '.*'), ('image files', '.png', '.jpg')]
        self.dir_opt = options = {}
        options['mustexist'] = False

    def askopenfile(self):
        filename = tkinter.filedialog.askopenfilename(**self.file_opt)
        Train_Data(str(filename))
        exit(0)


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
    try:
        f1 = open("flattened_images.txt", 'ab')
    except:
        tkinter.messagebox.showwarning("Error", "unable to open flattened_images.txt")
        np.os.system("pause")
        return False
    try:
        f2 = open("classifications.txt", 'ab')
    except:
        tkinter.messagebox.showwarning("Error", "unable to open classifications.txt")
        np.os.system("pause")
        return False
    intClassifications = []
    intValidChars = [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9'),
                     ord('A'), ord('B'), ord('C'), ord('D'), ord('E'), ord('F'), ord('G'), ord('H'), ord('I'), ord('J'),
                     ord('K'), ord('L'), ord('M'), ord('N'), ord('O'), ord('P'), ord('Q'), ord('R'), ord('S'), ord('T'),
                     ord('U'), ord('V'), ord('W'), ord('X'), ord('Y'), ord('Z')]
    train = cv2.imread(str(train))
    npaFlattenedImages = np.empty((0, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
    imgGray, temp = Preprocess.Process(train)
    imgContours, npaContours, npaHierarchy = cv2.findContours(temp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    i = 1
    for npaContour in npaContours:
        pc = PossibleChar(npaContour)
        if Chars.Check(pc):
            [intX, intY, intW, intH] = cv2.boundingRect(npaContour)
            test = train.copy()
            cv2.rectangle(test, (intX, intY), (intX + intW, intY + intH), (255, 0, 0), 1)
            cv2.imshow("Cropped Image", cv2.resize(train[intY:intY + intH, intX:intX + intW], (intW, intH)))
            cv2.imshow("test", test.copy())
            intChar = cv2.waitKey(0)
            cv2.destroyWindow("Cropped Image")
            if intChar == 27:
                sys.exit()
            elif intChar == 0:
                tkinter.messagebox.showinfo("Error", "invalid CONTOR " + str(i) + " , skipping")
                i = i + 1
            elif intChar in intValidChars:
                intClassifications.append(intChar)
                npaFlattenedImage = cv2.resize(temp[intY:intY + intH, intX:intX + intW],
                                               (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT)).reshape(
                    (1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
                npaFlattenedImages = np.append(npaFlattenedImages, npaFlattenedImage, 0)
    fltClassifications = np.List(intClassifications, np.float32)
    npaClassifications = fltClassifications.reshape((fltClassifications.size, 1))
    np.savetxt(f2, npaClassifications)
    np.savetxt(f1, npaFlattenedImages)
    f1.close()
    f2.close()
    return


def main():
    root = tkinter.Tk()
    TkFileDialogExample(root).pack()
    root.mainloop()


if __name__ == "__main__":
    main()
