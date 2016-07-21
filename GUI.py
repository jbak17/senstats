from Tkinter import *
import ttk
import Tkinter,tkFileDialog

def getPath():
#opens a dialogue box to enable the election of files
    filez = tkFileDialog.askdirectory(parent=root,title='Choose the directory containing your committee files:', mustexist=True)
    dir_path.set(filez)

root = Tk()
root.title('Committee Office monthly report statistics')

#sets up a main window into which everything else is held.
mainframe = ttk.Frame(root, padding = '3 3 12 12')
mainframe.grid(column = 0, row = 0, sticky = (N, W, E, S))
#configure settings just tell the frame to resize if the window size is changed by the user.
mainframe.columnconfigure(0, weight = 1)
mainframe.rowconfigure(0, weight = 1)

dir_path = StringVar()
#entry box for path
directory_entry = ttk.Entry(mainframe, width=25, textvariable=dir_path)
directory_entry.grid(column=2, row=1, sticky=(W, E))
#Label for entry box
ttk.Label(mainframe, text = 'Directory:').grid(column=1, row=1, sticky=(W, E))
#button for entry box
ttk.Button(mainframe, text="Select directory", command = getPath).grid(column=3, row=1, sticky=SE)

#button for running program
ttk.Button(mainframe, text ='Calculate').grid(column =3, row = 3, sticky = SE)
#radiobutton for committee type
rdFrame = ttk.Frame(mainframe, padding = 5)
var = IntVar()
R1 = Radiobutton(rdFrame, text="Legislation", variable=var, value=1)
R1.pack( anchor = W )

R2 = Radiobutton(rdFrame, text="References", variable=var, value=2)
R2.pack( anchor = W )

R3 = Radiobutton(rdFrame, text="Both", variable=var, value=3)
R3.pack( anchor = W)
rdFrame.grid(column = 3, row = 2, sticky = (W, S))

outstring = StringVar()
output = Label(mainframe, textvariable=outstring).grid(columnspan = 2, column = 1, row = 1, rowspan = 2)
#output.pack(anchor =W)

root.mainloop()
