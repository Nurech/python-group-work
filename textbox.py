import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont

# This adds a text box to the canvas
class TextBoxDialog:
    def __init__(self, editor):
        self.editor = editor
        self.dialog = tk.Toplevel(self.editor.master)
        self.dialog.geometry('300x200')
        self.dialog.minsize(300, 200)
        self.dialog.title("Add Text")

        self.font = ("Arial", 14)
        self.text_box = tk.Text(self.dialog, height=5, width=30, font=self.font)
        self.text_box.pack(fill=tk.BOTH, expand=True)

        self.button_frame = ttk.Frame(self.dialog)
        self.button_frame.pack(fill=tk.X)

        self.add_button = ttk.Button(self.button_frame, text="Add Text", command=self.add_text)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.cancel_button = ttk.Button(self.button_frame, text="Cancel", command=self.cancel)
        self.cancel_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.canvas = self.editor.canvas

    def add_text(self):
        text = self.text_box.get(1.0, tk.END).strip()
        if text == "":
            self.add_button.config(state='disabled')
        else:
            self.draw_text_image(text)
            self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()

 # This is the function that draws the text box
    def draw_text_image(self, text):
        font = ImageFont.truetype("arial.ttf", 14)
        lines = text.split("\n")
        max_width = 0
        total_height = 0
        for line in lines:
            line_width, line_height = font.getsize(line)
            max_width = max(max_width, line_width)
            total_height += line_height

        img = Image.new("RGBA", (max_width + 20, total_height + 20), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # The for loops below draw the red lines around the text box
        for i in range(5, img.size[0] - 5, 10):
            draw.line([(i, 5), (i+5, 5)], fill="red", width=2)
            draw.line([(i, img.size[1] - 5), (i+5, img.size[1] - 5)], fill="red", width=2)

        for i in range(5, img.size[1] - 5, 10):
            draw.line([(5, i), (5, i+5)], fill="red", width=2)
            draw.line([(img.size[0] - 5, i), (img.size[0] - 5, i+5)], fill="red", width=2)


        current_height = 10
        for line in lines:
            draw.text((10, current_height), line, fill="red", font=font)
            current_height += font.getsize(line)[1]

        photo = ImageTk.PhotoImage(img)

        img_id = self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, image=photo)
        self.editor.icon_list.append(photo)
