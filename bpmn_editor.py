import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import ImageTk, Image, ImageGrab, ImageDraw
import os
import math

import time

class ToolTip(object):
    def __init__(self, widget, text='Widget info'):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        self.x = self.y = 0

    def showtip(self):
        "Display text in tooltip window"
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove all Window Manager (wm) decorations
        tw.wm_geometry("+%d+%d" % (self.x, self.y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()

    def check_if_tooltip_should_be_shown(self, event):
        if self.tooltip_window or not self.text:
            return
        self.x, self.y, _, _ = self.widget.bbox("insert")
        self.x += self.widget.winfo_rootx() + 25
        self.y += self.widget.winfo_rooty() + 20
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry("+%d+%d" % (self.x, self.y))
        label = tk.Label(self.tooltip_window, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def check_if_tooltip_should_be_hidden(self, event):
        if self.tooltip_window:
            self.hidetip()

    def create_tooltip(widget, text):
        tool_tip = ToolTip(widget, text)
        widget.bind("<Enter>", tool_tip.check_if_tooltip_should_be_shown)
        widget.bind("<Leave>", tool_tip.check_if_tooltip_should_be_hidden)

class DraggableResizableTextBox:
    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.text_box = tk.Canvas(parent, **kwargs)
        self.text_box.bind("<Button-1>", self.start_move)
        self.text_box.bind("<ButtonRelease-1>", self.stop_move)
        self.text_box.bind("<B1-Motion>", self.do_move)
        self.text_box.bind("<Double-Button-1>", self.edit_mode)
        self.text_box.bind("<Button-3>", self.start_resize)
        self.text_box.bind("<B3-Motion>", self.do_resize)
        self.text_box.bind("<ButtonRelease-3>", self.stop_resize)
        self.text_box.bind("<KeyPress>", self.add_char)
        self.text_box.bind("<BackSpace>", self.del_char)

        self.text_content = ''
        self.text_id = self.text_box.create_text((5, 5), text=self.text_content, anchor='nw', width=185)

        self.text_box.config(highlightthickness=1, highlightbackground="red")
        self.text_box.config(bd=0)

        self.text_box["bg"] = "#ffffff"
        self.text_box["highlightbackground"] = "#ff0000"
        self.text_box["highlightthickness"] = 2

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        dx = event.x - self.x
        dy = event.y - self.y
        self.text_box.place(x=self.text_box.winfo_x() + dx, y=self.text_box.winfo_y() + dy)

    def start_resize(self, event):
        self.width = self.text_box.winfo_width()
        self.height = self.text_box.winfo_height()

    def stop_resize(self, event):
        self.width = None
        self.height = None

    def do_resize(self, event):
        self.text_box.configure(width=event.x, height=event.y)

    def edit_mode(self, event):
        self.text_box.focus_set()

    def add_char(self, event):
        self.text_content += event.char
        self.text_box.itemconfig(self.text_id, text=self.text_content)

    def del_char(self, event):
        self.text_content = self.text_content[:-1]
        self.text_box.itemconfig(self.text_id, text=self.text_content)

    def add_to_canvas(self, x, y):
        self.text_box.place(x=x, y=y)


class BpmnEditor:
    def __init__(self, window):
        self.textboxes = []
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

        self.window.rowconfigure(0, minsize=650, weight=1)
        self.window.columnconfigure(1, minsize=650, weight=1)

        # Creating a canvas
        self.canvas = tk.Canvas(self.window, width=650, height=650)
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
        frame = tk.Frame(self.window, highlightbackground="#a3a3a3", highlightthickness=5)
        count = 1

        count = self.add_side_bar_button(frame, "Textbox", "", self.add_textbox, count, 'Add textbox')

        # Add open base file button
        count = self.add_side_bar_button(frame, "Open", "", self.open_file, count, 'Open a file')
        # Add save button
        count = self.add_side_bar_button(frame, "Save As...", "", self.save_file, count, 'Save the file')


        # Add icon buttons
        count = self.add_label(count, frame, "Icons")
        for filename in os.listdir("assets/button_icons"):
            original_img = Image.open("assets/button_icons/" + filename)
            resized_img = original_img.resize((35, 35))  # resize image
            img = ImageTk.PhotoImage(resized_img)
            self.button_icons.append(img)
            count = self.add_side_bar_button(frame, "Add " + filename, img, lambda fn=filename: self.add_icon(fn), count, 'Add an icon')


        # Drawing button
        count = self.add_label(count, frame, "Draw")
        myimg = Image.new('RGBA', (35, 35))
        draw = ImageDraw.Draw(myimg)
        draw.line((0, 14, 35, 14), fill="red", width=3)
        line_icon = ImageTk.PhotoImage(myimg)
        self.button_icons.append(line_icon)  # created image needs to exist in mem, don't delete this line
        count = self.add_side_bar_button(frame, "arrow", line_icon, self.enable_draw_mode, count, 'Draw a line')

        # Eraser button
        count = self.add_label(count, frame, "Erase")
        eraser_img = Image.new('RGBA', (35, 35), (255, 255, 255, 0))
        eraser_draw = ImageDraw.Draw(eraser_img)
        eraser_draw.line([10, 10, 25, 25], fill="black", width=3)
        eraser_draw.line([25, 10, 10, 25], fill="black", width=3)
        eraser_icon = ImageTk.PhotoImage(eraser_img)
        self.button_icons.append(eraser_icon)  # created image needs to exist in mem, don't delete this line
        count = self.add_side_bar_button(frame, "Eraser", eraser_icon, self.enable_erase_mode, count, "Erase a line")

        frame.grid(row=0, column=0, sticky=tk.NS)

    def add_textbox(self):
        if not self.diagram:  # block while no base image opened
            print("Open base image before adding textbox")
            return
        textbox = DraggableResizableTextBox(self.canvas, bd=2, width=200, height=100, relief='solid', borderwidth=2, highlightcolor='red',
                                            highlightthickness=1)
        textbox.add_to_canvas(50, 50)
        self.textboxes.append(textbox)  # append to the list of textboxes

    def add_label(self, count, frame, text):
        label = tk.Label(frame, text=text)
        label.grid(row=count, column=0, sticky=tk.EW, padx=5, pady=(5, 0))
        return count + 1

    def add_side_bar_button(self, frame, text, image, command, count, tooltip_text):
        if image:
            # Button with icon
            button = ttk.Button(frame, text=text, image=image, command=command)
            self.create_tooltip(button, tooltip_text)  # Add tooltip to the button
        else:
            # Button with no icon
            button = ttk.Button(frame, text=text, command=command)
            self.create_tooltip(button, tooltip_text)  # Add tooltip to the button
        button.grid(row=count, column=0, sticky=tk.EW, padx=5, pady=5)
        self.buttons.append(button)
        return count + 1

    def create_tooltip(self,widget, text):
        tool_tip = ToolTip(widget, text)
        widget.bind("<Enter>", tool_tip.check_if_tooltip_should_be_shown)
        widget.bind("<Leave>", tool_tip.check_if_tooltip_should_be_hidden)

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
        img = Image.open("assets/button_icons/" + icon_name)
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
            # This will try to snap the dragged item to the closest icon
            snap_threshold = 30
            drag_item_pos = self.canvas.coords(self.drag_item)
            closest_icon = None
            closest_icon_distance = None

            for item in self.canvas.find_all():
                if item != self.drag_item and item not in self.drawn_line_obj_nrs:
                    item_pos = self.canvas.coords(item)
                    distance = math.sqrt((item_pos[0] - drag_item_pos[0]) ** 2 + (item_pos[1] - drag_item_pos[1]) ** 2)

                    if closest_icon_distance is None or distance < closest_icon_distance:
                        closest_icon_distance = distance
                        closest_icon = item

            if closest_icon is not None and closest_icon_distance <= snap_threshold and not self.snapped:
                closest_icon_pos = self.canvas.coords(closest_icon)
                offset = self.canvas.bbox(self.drag_item)[2] - 15 - self.canvas.bbox(self.drag_item)[0]
                self.canvas.coords(self.drag_item, closest_icon_pos[0] + offset, closest_icon_pos[1])
                self.snapped = True
            else:
                self.canvas.coords(self.drag_item, event.x, event.y)
                self.snapped = False

    def drag_release(self, event):
        self.anchor = None

    def enable_draw_mode(self):
        if not self.diagram:  # block while no base image opened
            print("Open base image before drawing")
            return

        if self.state != "draw":
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

    def enable_erase_mode(self):
        if not self.diagram:  # block while no base image opened
            print("Open base image before erasing")
            return

        if self.state != "erase":
            self.state = "erase"
            self.window.config(cursor="X_cursor")
            print("state is", self.state)
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            self.canvas.bind('<ButtonPress-1>', self.erase_element)
        else:
            self.default_mode()

    # TODO textbox can not be remove, the click listener is not working because its on the canvas, not on textbox
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
