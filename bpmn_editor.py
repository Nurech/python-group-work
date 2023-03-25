import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import ImageTk, Image, ImageGrab


def open_file():
    """Open a file for editing."""
    global img  # Making img a global variable, might not be needed
    global photo  # Making photo a global variable, otherwise gets garbage-collected
    filepath = askopenfilename(
        filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    img = Image.open(filepath)
    photo = ImageTk.PhotoImage(img)
    # Configuring the canvas to have a scroll region that matches the image size
    canvas.config(scrollregion=(0, 0, img.width, img.height))
    canvas.create_image(0, 0, image=photo, anchor="nw")


def save_file():
    """Save the file."""
    filepath = asksaveasfilename(defaultextension='.png')
    if not filepath:
        return
    ImageGrab.grab(bbox=(
        canvas.winfo_rootx(),
        canvas.winfo_rooty(),
        canvas.winfo_rootx() + canvas.winfo_width(),
        canvas.winfo_rooty() + canvas.winfo_height()
    )).save(filepath)
    #img.save(filepath)


def add_lock():
    # load another image for testing
    img = Image.open("images/lock.png")
    img.thumbnail((50, 50))
    photo = ImageTk.PhotoImage(img)
    added_images.append(img)
    added_photos.append(photo)
    canvas.create_image(50, 50, image=photo)


def add_unlock():
    # load another image for testing
    img = Image.open("images/unlock.png")
    img.thumbnail((50, 50))
    photo = ImageTk.PhotoImage(img)
    added_images.append(img)
    added_photos.append(photo)
    canvas.create_image(50, 50, image=photo)


def drag_start(event):
    global drag_item
    drag_item = canvas.find_closest(event.x, event.y)[0]


def drag_move(event):
    global drag_item
    canvas.coords(drag_item, event.x, event.y)


added_images = []
added_photos = []
window = tk.Tk()
window.title("BPMN Editor")

window.rowconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=800, weight=1)

# Creating a vertical scrollbar widget
vscrollbar = tk.Scrollbar(window)
vscrollbar.grid(row=0, column=2, sticky="ns")

# Creating a horizontal scrollbar widget
hscrollbar = tk.Scrollbar(window, orient="horizontal")
hscrollbar.grid(row=1, column=1, sticky="ew")

# Creating a canvas with the scrollbars attached
canvas = tk.Canvas(window, width=800, height=600, yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)
canvas.grid(row=0, column=1, sticky="nsew")

# Configuring the scrollbars to scroll the canvas
vscrollbar.config(command=canvas.yview)
hscrollbar.config(command=canvas.xview)

frm_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
btn_open = tk.Button(frm_buttons, text="Open", command=open_file)
btn_save = tk.Button(frm_buttons, text="Save As...", command=save_file)
btn_add_lock = tk.Button(frm_buttons, text="Add lock", command=add_lock)
btn_add_unlock = tk.Button(frm_buttons, text="Add unlock", command=add_unlock)
btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_save.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
btn_add_lock.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
btn_add_unlock.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
frm_buttons.grid(row=0, column=0, sticky="ns")
# bind mouse events for dragging and dropping
canvas.bind("<Button-1>", drag_start)
canvas.bind("<B1-Motion>", drag_move)

window.mainloop()
