from Tkinter import *
import ttk
import Tkinter,tkFileDialog

class GUI(object):
    def __init__(self, master):
        self.root = master
        self.mainframe = ttk.Frame(self.root, padding = '3 3 12 12')
        self.mainframe.grid(column = 0, row = 0, sticky = (N, W, E, S))
        self.mainframe.columnconfigure(0, weight = 1)
        self.mainframe.rowconfigure(0, weight = 1)
        self.dirButton = ttk.Button(self.mainframe, text="select directory", command = self.getpath).grid(column=3, row=1, sticky=SE)
        self.buildCommitteeSelector(self.mainframe)
        dir_path = StringVar()

        #entry box for path
        directory_entry = ttk.Entry(self.mainframe, width=25, textvariable=dir_path)
        directory_entry.grid(column=2, row=1, sticky=(W, E))
        #label for entry box
        ttk.Label(self.mainframe, text = 'directory:').grid(column=1, row=1, sticky=(W))
        #button for entry box

        outstring = StringVar()
        output = Label(self.mainframe, textvariable=outstring).grid(columnspan = 2, column = 1, row = 1, rowspan = 2)
        #output.pack(anchor =w)

    def getpath(self):
    #opens a dialogue box to enable the election of files
        filez = tkfiledialog.askdirectory(parent=root,title='choose the directory containing your committee files:', mustexist=true)
        dir_path.set(filez)

    def buildCommitteeSelector(self, frame):
        #button for running program
        ttk.Button(frame, text ='calculate').grid(column =3, row = 3, sticky = SE)
        #radiobutton for committee type
        rdframe = ttk.Frame(frame, padding = 5)
        var = IntVar()
        r1 = Radiobutton(rdframe, text="legislation", variable=var, value=1)
        r1.pack( anchor = W )

        r2 = Radiobutton(rdframe, text="references", variable=var, value=2)
        r2.pack( anchor = W )

        r3 = Radiobutton(rdframe, text="both", variable=var, value=3)
        r3.pack( anchor = W)
        rdframe.grid(column = 3, row = 2, sticky = (W, S))

def main():
    root = Tk()
    root.title('Committee Office monthly report statistics')
    window = GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
