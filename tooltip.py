import tkinter as tk


# Inspired by https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
class ToolTip(object):
    def __init__(self, widget):
        self.waittime = 500  # ms
        self.wraplength = 180  # pixels
        self.widget = widget
        self.text = ""
        self.tooltipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        self.text = text
        if self.tooltipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + self.widget.winfo_rooty() + 27
        # creates a toplevel window
        self.tooltipwindow = tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        tw.wm_overrideredirect(True)

        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tooltipwindow
        self.tooltipwindow = None
        if tw:
            tw.destroy()


def createToolTip(widget, text):
    toolTip = ToolTip(widget)

    def enter(event):
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 20
        toolTip.x = x
        toolTip.y = y
        # Schedule to show the tooltip in 500 ms
        toolTip.id = widget.after(500, toolTip.showtip, text)

    def leave(event):
        x = event.x_root + 25
        y = event.y_root + 20
        if abs(x - toolTip.x) < 25 and abs(y - toolTip.y) < 20:
            return
        widget.after_cancel(toolTip.id)  # cancel scheduled tooltip
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
