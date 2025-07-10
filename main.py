import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from core.style_transfer import apply_style
import threading
import os

class NSTApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Artistic Style Mixer")
        self.master.geometry("1000x700")
        self.content_img = None
        self.style_img = None
        self.result_path = None

        tk.Label(master, text="Artistic Style Mixer", font=("Arial", 22)).pack(pady=10)

        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Load Content", command=self.select_content).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Load Style", command=self.select_style).grid(row=0, column=1, padx=10)
        tk.Button(button_frame, text="Start Stylizing", command=self.start_process).grid(row=0, column=2, padx=10)

        self.preview_frame = tk.Frame(master)
        self.preview_frame.pack(pady=20)

        self.lbl_content = tk.Label(self.preview_frame, text="Original")
        self.lbl_content.grid(row=0, column=0)

        self.lbl_style = tk.Label(self.preview_frame, text="Style")
        self.lbl_style.grid(row=0, column=1)

        self.lbl_result = tk.Label(self.preview_frame, text="Stylized")
        self.lbl_result.grid(row=0, column=2)

        self.img_content = tk.Label(self.preview_frame)
        self.img_content.grid(row=1, column=0, padx=20)

        self.img_style = tk.Label(self.preview_frame)
        self.img_style.grid(row=1, column=1, padx=20)

        self.img_result = tk.Label(self.preview_frame)
        self.img_result.grid(row=1, column=2, padx=20)

    def select_content(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            self.content_img = path
            self.display_image(path, self.img_content)
            messagebox.showinfo("Content Loaded", f"Loaded: {os.path.basename(path)}")

    def select_style(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            self.style_img = path
            self.display_image(path, self.img_style)
            messagebox.showinfo("Style Loaded", f"Loaded: {os.path.basename(path)}")

    def start_process(self):
        if not self.content_img or not self.style_img:
            messagebox.showwarning("Input Required", "Please upload both images.")
            return

        def worker():
            self.update_title("Processing...")
            self.toggle_buttons("disable")
            try:
                output = apply_style(self.content_img, self.style_img)
                self.result_path = output
                self.display_image(output, self.img_result)
                messagebox.showinfo("Done", f"Saved at:\n{output}")
                self.update_title("Stylizing Complete")
            except Exception as err:
                messagebox.showerror("Error", str(err))
            finally:
                self.toggle_buttons("normal")

        threading.Thread(target=worker).start()

    def display_image(self, img_path, label, size=(300, 300)):
        try:
            img = Image.open(img_path).resize(size)
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo)
            label.image = photo
        except Exception as err:
            print(f"Error displaying {img_path}: {err}")

    def toggle_buttons(self, state):
        for widget in self.master.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, tk.Button):
                    child.config(state=state)

    def update_title(self, message):
        self.master.title(f"Artistic Style Mixer - {message}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NSTApp(root)
    root.mainloop()
