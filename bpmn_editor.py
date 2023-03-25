import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import ImageTk, Image, ImageGrab
import os


class BpmnEditor:
    def __init__(self, window):
        self.window = window
        self.window.title("BPMN Editor")

        self.diagram_img = None  # The base BPMN diagram
        self.diagram = None  # The base BPMN diagram
        self.icon_list = []  # Icon image files added to the diagram
        self.drag_item = 0  # The icon object currently being dragged

        self.window.rowconfigure(0, minsize=800, weight=1)
        self.window.columnconfigure(1, minsize=800, weight=1)

        # Creating a canvas with scrollbars
        vscrollbar = tk.Scrollbar(self.window)
        vscrollbar.grid(row=0, column=2, sticky=tk.NS)
        # Creating a horizontal scrollbar widget
        hscrollbar = tk.Scrollbar(self.window, orient="horizontal")
        hscrollbar.grid(row=1, column=1, sticky=tk.EW)
        # Creating a canvas with the scrollbars attached
        self.canvas = tk.Canvas(self.window, width=800, height=600, yscrollcommand=vscrollbar.set,
                                xscrollcommand=hscrollbar.set)
        self.canvas.grid(row=0, column=1, sticky=tk.NSEW)
        # Configuring the scrollbars to scroll the canvas
        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)

        # Add buttons to the left side
        self.button_icons = []
        self.buttons = []
        self.create_buttons_menu()

        # bind mouse events for dragging and dropping
        self.canvas.bind("<Button-1>", self.drag_start)
        self.canvas.bind("<B1-Motion>", self.drag_move)

    def create_buttons_menu(self):
        """Create the left side menu with buttons."""
        frm_buttons = tk.Frame(self.window, relief=tk.RAISED, bd=2)
        btn_open = tk.Button(frm_buttons, text="Open", command=self.open_file)
        btn_open.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=5)
        btn_save = tk.Button(frm_buttons, text="Save As...", command=self.save_file)
        btn_save.grid(row=1, column=0, sticky=tk.EW, padx=5, pady=5)
        row = 2
        for filename in os.listdir("assets"):
            original_img = Image.open("assets/" + filename)
            resized_img = original_img.resize((35, 35))  # resize image
            img = ImageTk.PhotoImage(resized_img)
            self.button_icons.append(img)
            btn_add_lock = tk.Button(
                frm_buttons, text="Add " + filename, image=img, command=lambda fn=filename: self.add_icon(fn)
            )
            btn_add_lock.grid(row=row, column=0, sticky=tk.EW, padx=5, pady=5)
            self.buttons.append(btn_add_lock)
            row += 1
        frm_buttons.grid(row=0, column=0, sticky=tk.NS)

    def open_file(self):
        """Open a file for editing."""
        filepath = askopenfilename(filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")])
        if not filepath:
            return
        self.canvas.delete("all")  # reset the canvas
        self.diagram_img = Image.open(filepath)
        self.diagram = ImageTk.PhotoImage(self.diagram_img)
        # Todo: resize canvas + maybe resize window?
        # Configuring the canvas to have a scroll region that matches the image size
        self.canvas.config(scrollregion=(0, 0, self.diagram_img.width, self.diagram_img.height))
        self.canvas.create_image(0, 0, image=self.diagram, anchor="nw")

    def save_file(self):
        """Save the file."""
        filepath = asksaveasfilename(defaultextension='.png')
        if not filepath:
            return
        ImageGrab.grab(bbox=(
            self.canvas.winfo_rootx(),
            self.canvas.winfo_rooty(),
            self.canvas.winfo_rootx() + self.canvas.winfo_width(),
            self.canvas.winfo_rooty() + self.canvas.winfo_height()
        )).save(filepath)

    def add_icon(self, icon_name):
        """Add an icon on a canvas."""
        if not self.diagram:  # block while no base image opened
            print("Open base image before adding icon")
            return
        img = Image.open("assets/" + icon_name)
        img.thumbnail((40, 40))
        photo = ImageTk.PhotoImage(img)
        self.icon_list.append(photo)
        self.canvas.create_image(50, 50, image=photo)

    def drag_start(self, event):
        """Find the object to drag."""
        closest_items = self.canvas.find_closest(event.x, event.y)
        if len(closest_items) == 0:
            return
        self.drag_item = closest_items[0]

    def drag_move(self, event):
        """Drag an object."""
        items = self.canvas.find_withtag("all")  # get all item ids
        if len(items) > 1:  # Block moving the base image
            self.canvas.coords(self.drag_item, event.x, event.y)


if __name__ == "__main__":
    root = tk.Tk()
    BpmnEditor(root)
    root.mainloop()
