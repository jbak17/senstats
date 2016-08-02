from Tkinter import *
import ttk
import tkFileDialog
import senstat
import classes

class GUI(object):
    def __init__(self, master):
        self.root = master

        #Main frame to hold all other widgets
        self.mainframe = ttk.Frame(self.root, padding = '3 3 12 12')
        self.mainframe.grid(column = 0, row = 1, sticky = (N,W,E,S))
        self.mainframe.columnconfigure(0, weight = 1)
        self.mainframe.rowconfigure(0, weight = 1)
        self.buildFunctionSelection(self.mainframe)
        self.buildOutputArea(self.mainframe)
        #
        #------------    BUTTONS ---------------
        #
        #directory button
        self.dir_path = StringVar()
        self.dirButton = ttk.Button(self.mainframe, text="select directory", command = self.getpath).grid(column=3, row=1, sticky=SE)
        #submission button
        self.submissions = None
        self.submissions_set = BooleanVar()
        ttk.Button(self.mainframe, text = 'Submissions', command = self.submission_request).grid(column = 3, row = 5, sticky = SE)
        #committee selector button
        self.committee_selector = self.buildCommitteeSelector(self.mainframe)
        #run senstats button
        ttk.Button(self.mainframe, text ='Calculate', command = self.senstat_request).grid(column =3, row = 4, sticky = SE)

        #entry box for path
        directory_entry = ttk.Entry(self.mainframe, width=25, textvariable=self.dir_path)
        directory_entry.grid(column=2, row=1, sticky=(W, E))
        directory_entry.focus()
        ttk.Label(self.mainframe, text = 'Directory:').grid(column=1, row=1, sticky=(W))

        #styling
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        #output area
    def buildOutputArea(self, frame):
        outputFrame = ttk.Frame(frame, padding = (10, 10), relief = 'sunken', width = 200, height = 200)
        self.outstring = StringVar()
        output = ttk.Label(outputFrame, textvariable=self.outstring).grid(row =1, column =1)
        s = ttk.Scrollbar(outputFrame, orient = VERTICAL)
        #outputFrame['yscrollcommand'] = s.set
        #self.outstring.set('Here is the output area.')
        outputFrame.grid(columnspan = 2, column = 1, rowspan = 2, row = 2)


    def getpath(self):
    #opens a dialogue box to enable the election of files
        filez = tkFileDialog.askdirectory(parent= self.mainframe, title='choose the directory containing your committee files:', mustexist=True)
        self.dir_path.set(filez)

    def buildFunctionSelection(self, frame):
        '''
        Takes a frame and creates checkboxes for: Hearings, private meetings and submissions. Results of checkboxes are fed to senstat for preparing output.
        '''
        functionFrame = ttk.Frame(frame, padding = 5)
        self.hansard = IntVar()
        self.private = IntVar()
        self.subs = IntVar()
        c1 = ttk.Checkbutton(functionFrame, text = 'Public hearings', variable = self.hansard).grid(row = 1, sticky = (W))
        c2 = ttk.Checkbutton(functionFrame, text = 'Private meetings', variable = self.private).grid(row = 2, sticky = (W))
        c3 = ttk.Checkbutton(functionFrame, text = 'Submissions', variable = self.subs).grid(row = 3, sticky = (W))
        functionFrame.grid(column = 4, row = 2, sticky = W)

    def buildCommitteeSelector(self, frame):
        '''
        Creates three radio buttons to select whether the reports for the Legislation, References or both committees should be evaluated.
        '''
        #button for running program
        #radiobutton for committee type
        rdframe = ttk.Frame(frame, padding = 5)
        self.var = IntVar()
        r1 = Radiobutton(rdframe, text="Legislation", variable=self.var, value=1)
        r1.pack( anchor = W )

        r2 = Radiobutton(rdframe, text="References", variable=self.var, value=2)
        r2.pack( anchor = W )

        r3 = Radiobutton(rdframe, text="Both", variable=self.var, value=3)
        r3.pack( anchor = W)
        rdframe.grid(column = 3, row = 2, sticky = (W, S))
        return self.var

    def getSubmisssions(self):
        self.submissions = tkFileDialog.askopenfilenames(parent = self.mainframe, title='Select submissions:')
        self.submissions_set.set(1)
        #print submissions

    def senstat_request(self):
        '''
        Collects the string with the directory and the type of committee. These are fed to senstat.py to get the results and set the label outstring with results.
        '''
        path = self.dir_path.get()
        #creates a tuple to be passed to senstat. If selected value is 1 and the user wants the result of those functions.
        request = (self.hansard.get(), self.private.get(), self.subs.get())
        print 'Function request: ' + str(request)
        ctype = self.committee_selector.get() #ctype is an integer.
        #send request and assign string to results.
        results = senstat.main(path, ctype, request)
        self.outstring.set(results)

    def submission_request(self):
        '''
        User selects submissions to consider.
        Results printed out in label area.
        '''
        submissionReader = classes.SubmissionTools()
        stringifier = classes.Outstrings()
        self.getSubmisssions()
        subs = list(self.submissions)
        data = submissionReader.count_subs(subs) #data is tuple
        self.outstring.set(stringifier.submissionsOutString(data))

    def jurisdiction_database_window(self, location):
        '''
        @param: location = string of hearing location.
        Creates a window asking the user to select a jurisdiction.
        '''
        def select():
            var.get()
        top = Toplevel(padx = 10, pady = 10, takefocus = True)
        top.title('Jurisdiction selection:')
        top.height = '400'
        top.width = '400'
        top.relief = 'RIDGE'
        top.lift()
        msg = Message(top, text = 'I was unable to identify the State/Territory of {} in our database. Please select the relevant jurisdiction from the list below.'.format(location))
        msg.grid(column = 2, row = 1, columnspan = 2)
        button = Button(top, text = 'Submit', command = select).grid(row = 2, column = 3)
        choices = ['ACT', 'NT', 'SA', 'WA', 'QLD', 'VIC', 'NSW', 'TAS']
        var = StringVar(top)
        option = OptionMenu(top, var, *choices).grid(row =2, column = 2, sticky = W)

def main():
    root = Tk()
    s = ttk.Style().theme_use('clam')
    root.title('Committee Office monthly report statistics')
    window = GUI(root)
    #window.jurisdiction_database_window('perth')
    root.mainloop()

if __name__ == '__main__':
    main()
