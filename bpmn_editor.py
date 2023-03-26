import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import ImageTk, Image, ImageGrab
import os


class BpmnEditor:
    def __init__(self, window):
        self.window = window
        self.window_name = "BPMN Editor"
        self.window.title(self.window_name)
        self.window.resizable(0, 0)  # Make the window size fixed (user can not change the window size)

        self.diagram_img = None  # The base BPMN diagram
        self.diagram = None  # The base BPMN diagram
        self.base_obj_nr = 0  # tkinter reference to the diagram
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

        # Drawing stuff
        self.canvas.old_coords = None
        self.state = "drag"

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
        frame = tk.Frame(self.window, relief=tk.RAISED, bd=2)

        self.add_side_bar_button(frame, "Open", "", self.open_file)
        self.add_side_bar_button(frame, "Save As...", "", self.save_file)

        for filename in os.listdir("assets"):
            original_img = Image.open("assets/" + filename)
            resized_img = original_img.resize((35, 35))  # resize image
            img = ImageTk.PhotoImage(resized_img)
            self.button_icons.append(img)
            self.add_side_bar_button(frame, "Add " + filename, img, lambda fn=filename: self.add_icon(fn))

        self.add_side_bar_button(frame, "arrow", "", self.enable_draw_mode)
        self.add_side_bar_button(frame, "+", "", self.scale_up)
        self.add_side_bar_button(frame, "-", "", self.scale_down)

        frame.grid(row=0, column=0, sticky=tk.NS)

    def add_side_bar_button(self, frame, name, img, action):
        # Button with no icon
        button = tk.Button(frame, text=name, command=action)
        if img:
            # Button with icon
            button = tk.Button(frame, text=name, image=img, command=action)
        button.grid(row=len(self.buttons) + 1, column=0, sticky=tk.EW, padx=5, pady=5)
        self.buttons.append(button)

    def open_file(self):
        """Open a file for editing."""
        filepath = askopenfilename(filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")])
        if not filepath:
            return
        self.canvas.delete("all")  # reset the canvas
        self.diagram_img = Image.open(filepath)
        self.diagram = ImageTk.PhotoImage(self.diagram_img)
        self.canvas.config(
            scrollregion=(0, 0, self.diagram_img.width, self.diagram_img.height),  # scrollregion might not be necessary
            width=self.diagram_img.width, height=self.diagram_img.height
        )
        self.base_obj_nr = self.canvas.create_image(0, 0, image=self.diagram, anchor="nw")

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
        print("state is", self.state)
        if self.state == "drag":
            closest_items = self.canvas.find_closest(event.x, event.y)
            if len(closest_items) == 0:
                return
            self.drag_item = closest_items[0]

    def drag_move(self, event):
        """Drag an object."""
        items = self.canvas.find_withtag("all")  # get all item ids
        if len(items) > 1 and self.drag_item != self.base_obj_nr:  # Block moving the base image
            self.canvas.coords(self.drag_item, event.x, event.y)

    # TODO
    def scale_down(self):
        print("scale down all elements")

    # TODO
    def scale_up(self):
        print("scale up all elements")

    def enable_draw_mode(self):
        if self.state != "draw":
            for button in self.buttons:
                if button['text'] == 'arrow':
                    button.config(relief="sunken")
            self.state = "draw"
            print("state is", self.state)
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.bind('<ButtonPress-1>', self.draw_line)
            self.canvas.bind('<ButtonRelease-1>', self.draw_line)
            self.window.config(cursor="cross")
        else:
            self.stop_drawing_mode()

    def draw_line(self, event):
        if self.state == "draw":
            self.window.config(cursor="cross")
            if str(event.type) == 'ButtonPress':
                self.canvas.old_coords = event.x, event.y

            elif str(event.type) == 'ButtonRelease':
                x, y = event.x, event.y
                x1, y1 = self.canvas.old_coords
                self.canvas.create_line(x, y, x1, y1)
                self.stop_drawing_mode()

    def stop_drawing_mode(self):
        self.canvas.bind("<Button-1>", self.drag_start)
        self.canvas.bind("<B1-Motion>", self.drag_move)

        self.state = "drag"
        self.window.config(cursor="arrow")
        self.canvas.old_coords = None
        for button in self.buttons:
            if button['text'] == 'arrow':
                button.config(relief="raised")


if __name__ == "__main__":
    root = tk.Tk()
    BpmnEditor(root)
    root.mainloop()
