import tkinter
import tkinter.constants
import tkinter.filedialog
import Analysis


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
        Analysis.path = str(filename)
        Analysis.main()
        exit(0)


def main():
    root = tkinter.Tk()
    TkFileDialogExample(root).pack()
    root.mainloop()


if __name__ == '__main__':
    main()
