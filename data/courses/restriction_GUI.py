from tkinter import *
from tkinter.ttk import *

from numpy.ma.core import logical_or

LOGICAL_AND = "∧"
LOGICAL_OR = "∨"


class Application(Frame):

    def __init__(self):
        self.root = Tk()
        self.configure_root()
        super().__init__(self.root)

        self.left_frame = Frame(self.root)
        self.right_frame = Frame(self.root)

        self.left_frame.pack(side="left")
        self.right_frame.pack(side="right")

        self.active_restrictions_label = Label(self.right_frame, text="Active Restrictions", font=("Helvetica", 16, "bold"))
        self.active_restrictions_label.pack(side="top", pady=0, padx=20, anchor="center", expand=True)

        self.added_descriptions_text_var = StringVar()
        self.added_descriptions = Label(self.right_frame, textvariable=self.added_descriptions_text_var, justify="center", font=("Courier", 12))
        self.added_descriptions.pack(pady=0, padx=20)

        self.course_title_text = Label(self.left_frame, text="Course Title")
        self.course_title_text["font"] = ("Helvetica", 20, "bold")
        self.pack_left(self.course_title_text)

        self.restriction_text = Label(self.left_frame, text="Restriction goes here")
        self.pack_left(self.restriction_text)

        self.entry_box_string_var = StringVar()
        self.course_entry_box = Text(self.left_frame, width=20, height=5)
        self.pack_left(self.course_entry_box)

        self.make_restriction_type_radiobuttons()

        self.confirm_button = Button(self.left_frame, text="Add", command=self.submit_course)
        self.pack_left(self.confirm_button)

        self.pack()

    def pack_left(self, ui_obj):
        ui_obj.pack(padx=20, pady=20, anchor="w")

    def configure_root(self):
        self.root.title("UCONN Course Visualizer Restriction Editor")
        self.root.geometry("1000x500")

    def make_restriction_type_radiobuttons(self):
        # Tkinter string variable
        # able to store any string value
        self.current_restriction = StringVar(self.left_frame, "prereq")

        # Dictionary to create multiple buttons
        values = {"Prerequisite": "prereq",
                  "Concurrent Prerequisite": "concurrency",
                  "Corequisite": "coreq",
                  "Block": "block",
                  "Credit Limit": "credit_limit",
                  "Recommendation": "recommend",
                  "Major Restriction": "only_major",
                  "School Restriction": "school"
                  }

        # Loop is used to create multiple Radiobuttons
        # rather than creating each button separately
        for (text, value) in values.items():
            radio = Radiobutton(self.left_frame, text = text, variable = self.current_restriction, value = value)
            radio.pack(padx=50, anchor="w")

    def submit_course(self):
        restriction_text = self.course_entry_box.get("1.0", "end").strip()

        if not restriction_text:
            return

        restriction_text = restriction_text.replace("\n", f" {LOGICAL_OR} ").upper()

        if not self.added_descriptions_text_var.get():
            new_text = restriction_text
        else:
            new_text = self.added_descriptions_text_var.get() + "\n\n" + LOGICAL_AND + "\n\n" + restriction_text

        self.added_descriptions_text_var.set(new_text)


        self.course_entry_box.delete("1.0", "end")

app = Application()
app.mainloop()