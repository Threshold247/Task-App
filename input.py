import tkinter.scrolledtext
from tkinter import *
from database import Database

window = Tk()
window.title("Task app")
window.config(padx=50, pady=50)
# create canvas
canvas = Canvas(width=200, height=200)

task_image = PhotoImage(file="Image/task.png")
canvas.create_image(100, 100, image=task_image)
canvas.grid(row=0, column=0, columnspan=2)
my_database = Database()


# function to clear entry box when mouse is clicked
def clear_description(event):
    description_entry.delete("0", "end")


# function to clear entry box when mouse is clicked
def clear_date(event):
    date_entry.delete("0", "end")


def is_checked():
    add_reminder.getboolean(s="True")


# function for the button
def add_data():
    # connect to database and add entries from the entry boxes to server
    task_status = ""
    task_description = description_entry.get()
    task_date = date_entry.get()
    task_reminder = check_1.get()
    print(task_description)
    print(task_date)
    if task_reminder == 0:
        task_status = "False"
    elif task_reminder == 1:
        task_status = "True"
    my_database.adding_data(task_description=task_description, date=task_date, reminder=task_status)


# Label
description_label = Label(text="Task description")
description_label.grid(row=1, column=0)
date_label = Label(text="Date")
date_label.grid(row=2, column=0)
reminder_label = Label(text="Reminder")
reminder_label.grid(row=3, column=0)

# Entries
description_entry = Entry(width=35)
description_entry.grid(row=1, column=1)
description_entry.insert(0, "Enter text here")
# bind left mouse click to clear text
description_entry.bind('<Button-1>', clear_description)
date_entry = Entry(width=35)
date_entry.grid(row=2, column=1)
date_entry.insert(0, "format YYYY/MM/DD")
# bind left mouse click to clear text
date_entry.bind('<Button-1>', clear_date)

# Checkbox
# check to see if checkbox is clicked
check_1 = tkinter.IntVar()
# create a button with a variable to hold status of checkbox i.e on(1) or off(0)
add_reminder = Checkbutton(variable=check_1)
add_reminder.grid(row=3, column=1)


# Button
add_task = Button(bg="red", text="Add task", command=add_data)
add_task.grid(row=4, columnspan=2)


# Scroll bar
scroll_bar = tkinter.scrolledtext.ScrolledText(width=35,  height=10)


# Listbox
listbox = Listbox(window, width=35)
my_list = my_database.get_data()
count = 0
for item in my_list:
    count += 1
    description = item[1]
    date = item[2]
    listbox.insert(count, f"{description}: {date}")
listbox.grid(row=5, columnspan=3)




window.mainloop()
