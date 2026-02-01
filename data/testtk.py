from tkinter import *
from tkinter.ttk import *


# creating Tk window
master = Tk()

# creating a Fra, e which can expand according
# to the size of the window
pane = Frame(master)
pane.pack(fill = BOTH, expand = True)

# button widgets which can also expand and fill
# in the parent widget entirely
# Button 1
b1 = Button(pane, text = "Click me !")
b1.pack(side=TOP, fill = BOTH, expand = True)

# Button 2
b2 = Button(pane, text = "Click me too")
b2.pack(side=BOTTOM, fill = BOTH, expand = True)

# Execute Tkinter
master.mainloop()