import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import ImageTk, Image, ImageGrab, ImageDraw
import os
import math


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
        self.anchor = None  # Which side of a line is anchored to the mouse

        self.window.rowconfigure(0, minsize=800, weight=1)
        self.window.columnconfigure(1, minsize=800, weight=1)

        # Creating a canvas
        self.canvas = tk.Canvas(self.window, width=800, height=600)
        self.canvas.grid(row=0, column=1, sticky=tk.NSEW)

        # Drawing stuff
        self.canvas.old_coords = None
        self.drawn_line_obj_nrs = []
        self.drawn_line_coordinates = dict()
        self.state = "drag"

        # Add buttons to the left side
        self.button_icons = []
        self.buttons = []
        self.create_buttons_menu()

        # bind mouse events for dragging and dropping
        self.default_mode()

        # cache of actions
        self.actions = []

    def create_buttons_menu(self):
        """Create the left side menu with buttons."""
        frame = tk.Frame(self.window, relief=tk.RAISED, bd=2)

        # Add open base file button
        self.add_side_bar_button(frame, "Open", "", self.open_file)
        # Add save button
        self.add_side_bar_button(frame, "Save As...", "", self.save_file)

        # Add icon buttons
        for filename in os.listdir("assets"):
            original_img = Image.open("assets/" + filename)
            resized_img = original_img.resize((35, 35))  # resize image
            img = ImageTk.PhotoImage(resized_img)
            self.button_icons.append(img)
            self.add_side_bar_button(frame, "Add " + filename, img, lambda fn=filename: self.add_icon(fn))

        # Drawing button
        myimg = Image.new('RGBA', (35, 35))
        draw = ImageDraw.Draw(myimg)
        draw.line((0, 14, 35, 14), fill="red", width=3)
        line_icon = ImageTk.PhotoImage(myimg)
        self.button_icons.append(line_icon)   # created image needs to exist in mem, don't delete this line
        self.add_side_bar_button(frame, "arrow", line_icon, self.enable_draw_mode)

        # Eraser button
        eraser_img = Image.new('RGBA', (35, 35), (255, 255, 255, 0))
        eraser_draw = ImageDraw.Draw(eraser_img)
        eraser_draw.line([10, 10, 25, 25], fill="black", width=3)
        eraser_draw.line([25, 10, 10, 25], fill="black", width=3)
        eraser_icon = ImageTk.PhotoImage(eraser_img)
        self.button_icons.append(eraser_icon)  # created image needs to exist in mem, don't delete this line
        self.add_side_bar_button(frame, "Eraser", eraser_icon, self.enable_erase_mode)


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
        self.canvas.delete(tk.ALL)  # reset the canvas
        self.drawn_line_obj_nrs = []
        self.drawn_line_coordinates = dict()
        self.diagram_img = Image.open(filepath)
        self.diagram = ImageTk.PhotoImage(self.diagram_img)
        self.canvas.config(width=self.diagram_img.width, height=self.diagram_img.height)
        self.base_obj_nr = self.canvas.create_image(0, 0, image=self.diagram, anchor=tk.NW)

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

    @staticmethod
    def calculate_dist(c1, c2):
        return math.sqrt(((c1[0] - c2[0]) ** 2) + ((c1[1] - c2[1]) ** 2))

    def drag_move(self, event):
        """Drag an object."""
        if self.drag_item == self.base_obj_nr:
            return
        if self.drag_item in self.drawn_line_obj_nrs:
            if self.anchor is None:
                coords = self.drawn_line_coordinates[self.drag_item]
                d1 = self.calculate_dist([event.x, event.y], [coords[0], coords[1]])
                d2 = self.calculate_dist([event.x, event.y], [coords[2], coords[3]])
                if d1 > d2:
                    self.anchor = "start"
                else:
                    self.anchor = "end"
            if self.anchor == "start":
                coords = self.drawn_line_coordinates[self.drag_item]
                self.canvas.coords(self.drag_item, coords[0], coords[1], event.x, event.y)
                self.drawn_line_coordinates[self.drag_item] = [coords[0], coords[1], event.x, event.y]
            elif self.anchor == "end":
                coords = self.drawn_line_coordinates[self.drag_item]
                self.canvas.coords(self.drag_item, event.x, event.y, coords[2], coords[3])
                self.drawn_line_coordinates[self.drag_item] = [event.x, event.y, coords[2], coords[3]]
        else:
            self.canvas.coords(self.drag_item, event.x, event.y)

    def drag_release(self, event):
        self.anchor = None

    def enable_draw_mode(self):
        if not self.diagram:  # block while no base image opened
            print("Open base image before drawing")
            return

        if self.state != "draw":
            for button in self.buttons:
                if button['text'] == 'arrow':
                    button.config(relief="sunken")
            self.state = "draw"
            print("state is", self.state)
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            self.canvas.bind('<ButtonPress-1>', self.draw_line)
            self.canvas.bind('<ButtonRelease-1>', self.draw_line)
            self.window.config(cursor="cross")
        else:
            self.default_mode()

    def draw_line(self, event):
        if self.state == "draw":
            self.window.config(cursor="cross")
            if event.type == tk.EventType.ButtonPress:
                self.canvas.old_coords = event.x, event.y
            elif event.type == tk.EventType.ButtonRelease:
                x, y = event.x, event.y
                x1, y1 = self.canvas.old_coords
                obj_nr = self.canvas.create_line(x, y, x1, y1, dash=(4, 2), width=3, fill='red')
                self.drawn_line_obj_nrs.append(obj_nr)
                self.drawn_line_coordinates[obj_nr] = [x, y, x1, y1]
                self.default_mode()

    def default_mode(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<Button-1>", self.drag_start)
        self.canvas.bind("<B1-Motion>", self.drag_move)
        self.canvas.bind("<ButtonRelease-1>", self.drag_release)
        self.state = "drag"
        self.window.config(cursor="arrow")
        self.canvas.old_coords = None
        for button in self.buttons:
            button.config(relief="raised")

    def enable_erase_mode(self):
        if not self.diagram:  # block while no base image opened
            print("Open base image before erasing")
            return

        if self.state != "erase":
            for button in self.buttons:
                if button['text'] == 'Eraser':
                    button.config(relief="sunken")
            self.state = "erase"
            self.window.config(cursor="X_cursor")
            print("state is", self.state)
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            self.canvas.bind('<ButtonPress-1>', self.erase_element)
        else:
            self.default_mode()

    def erase_element(self, event):
        if self.state == "erase":
            closest_item = self.canvas.find_closest(event.x, event.y)[0]
            if self.base_obj_nr != closest_item:
                self.canvas.delete(closest_item)
                self.default_mode()
            else:
                print("cannot delete the base image")

if __name__ == "__main__":
    root = tk.Tk()
    BpmnEditor(root)
    root.mainloop()
