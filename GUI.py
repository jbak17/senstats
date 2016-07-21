from Tkinter import *
import ttk
import Tkinter,tkFileDialog
import senstat

class GUI(object):
    def __init__(self, master):
        self.root = master
        #Main frame to hold all other widgets
        self.mainframe = ttk.Frame(self.root, padding = '3 3 12 12')
        self.mainframe.grid(column = 0, row = 0, sticky = (N, W, E, S))
        self.mainframe.columnconfigure(0, weight = 1)
        self.mainframe.rowconfigure(0, weight = 1)
        self.mainframe.pack()

        #buttons
        self.dir_path = StringVar()
        self.dirButton = ttk.Button(self.mainframe, text="select directory", command = self.getpath).grid(column=3, row=1, sticky=SE)
        self.committee_selector = self.buildCommitteeSelector(self.mainframe)
        ttk.Button(self.mainframe, text ='calculate', command = self.calculate).grid(column =3, row = 3, sticky = SE)

        #entry box for path
        directory_entry = ttk.Entry(self.mainframe, width=25, textvariable=self.dir_path)
        directory_entry.grid(column=2, row=1, sticky=(W, E))
        ttk.Label(self.mainframe, text = 'directory:').grid(column=1, row=1, sticky=(W))

        self.outstring = StringVar()
        self.output = ttk.Label(self.mainframe, textvariable=self.outstring).grid(columnspan = 2, column = 1, row = 1, rowspan = 2)
        #self.output.pack(anchor =W)

    def getpath(self):
    #opens a dialogue box to enable the election of files
        filez = tkFileDialog.askdirectory(parent= self.mainframe, title='choose the directory containing your committee files:', mustexist=True)
        self.dir_path.set(filez)

    def buildCommitteeSelector(self, frame):
        '''
        '''#button for running program
        #radiobutton for committee type
        rdframe = ttk.Frame(frame, padding = 5)
        self.var = IntVar()
        r1 = Radiobutton(rdframe, text="legislation", variable=self.var, value=1)
        r1.pack( anchor = W )

        r2 = Radiobutton(rdframe, text="references", variable=self.var, value=2)
        r2.pack( anchor = W )

        r3 = Radiobutton(rdframe, text="both", variable=self.var, value=3)
        r3.pack( anchor = W)
        rdframe.grid(column = 3, row = 2, sticky = (W, S))
        return self.var

    def calculate(self):
        '''
        Collects the string with the directory and the type of committee. These are fed to senstat.py to get the results and set the label outstring with results.
        '''
        path = self.dir_path.get()
        ctype = self.committee_selector.get() #ctype is an integer.
        results = senstat.hearings(path, ctype)
        self.outstring.set(results)

def main():
    root = Tk()
    root.title('Committee Office monthly report statistics')
    window = GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
