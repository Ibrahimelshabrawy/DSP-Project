import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import random

# =========================
# GLOBAL VARIABLES
# =========================

original_img = None
working_img = None
processed_img = None

PRIMARY_COLOR = "#0f172a"
SECONDARY_COLOR = "#1e293b"
ACCENT_COLOR = "#38bdf8"
BUTTON_COLOR = "#2563eb"

# =========================
# STATUS SYSTEM (AUTO HIDE)
# =========================

def update_status(message, color="#0ea5e9"):
    status_bar_frame.config(bg=color)
    status_bar.config(bg=color)
    status_var.set(message)
    root.after(3000, lambda: reset_status())


def reset_status():
    status_bar_frame.config(bg="#0ea5e9")
    status_bar.config(bg="#0ea5e9")
    status_var.set("Ready")


# =========================
# PROGRESS BAR CONTROL
# =========================

def run_progress(text="Processing..."):
    update_status(text, "#f59e0b")
    progress.start(8)
    root.update()


def stop_progress(text="Completed"):
    progress.stop()
    update_status(text, "#22c55e")


# =========================
# DISPLAY IMAGE
# =========================

def display_image(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_pil = img_pil.resize((420, 420))

    img_tk = ImageTk.PhotoImage(img_pil)

    panel.config(image=img_tk)
    panel.image = img_tk


# =========================
# LOAD IMAGE
# =========================

def load_image():
    global original_img, working_img, processed_img

    path = filedialog.askopenfilename()

    if not path:
        return

    original_img = cv2.imread(path)
    working_img = original_img.copy()
    processed_img = working_img.copy()

    display_image(processed_img)
    update_status("Image Loaded Successfully", "#22c55e")


# =========================
# SAVE IMAGE
# =========================

def save_image():
    global processed_img

    if processed_img is None:
        return

    path = filedialog.asksaveasfilename(defaultextension=".jpg")

    if path:
        cv2.imwrite(path, processed_img)
        update_status("Image Saved Successfully", "#22c55e")


# =========================
# RESET IMAGE
# =========================

def reset_image():
    global working_img, processed_img

    if original_img is None:
        return

    working_img = original_img.copy()
    processed_img = working_img.copy()

    display_image(processed_img)
    update_status("Image Reset", "#22c55e")


# =========================
# HISTOGRAM
# =========================

def show_histogram():
    colors = ('b','g','r')

    for i,col in enumerate(colors):
        hist = cv2.calcHist([processed_img],[i],None,[256],[0,256])
        plt.plot(hist,color=col)

    plt.title("Histogram")
    plt.show()


# =========================
# BEFORE AFTER
# =========================

def compare_images():
    combined = np.hstack((original_img, processed_img))
    cv2.imshow("Before vs After", combined)


# =========================
# FILTERS (NON-DESTRUCTIVE)
# =========================

def apply_filter(choice):
    global processed_img

    base = working_img.copy()

    if choice == "Gray":
        gray = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
        processed_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    elif choice == "Binary":
        gray = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
        processed_img = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

    elif choice == "Blur":
        processed_img = cv2.GaussianBlur(base,(9,9),0)

    elif choice == "Sharpen":
        kernel=np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
        processed_img=cv2.filter2D(base,-1,kernel)

    elif choice == "Salt Noise":
        noisy=base.copy()
        for _ in range(random.randint(300,10000)):
            y=random.randint(0,noisy.shape[0]-1)
            x=random.randint(0,noisy.shape[1]-1)
            noisy[y,x]=255
        processed_img=noisy

    elif choice == "Pepper Noise":
        noisy=base.copy()
        for _ in range(random.randint(300,10000)):
            y=random.randint(0,noisy.shape[0]-1)
            x=random.randint(0,noisy.shape[1]-1)
            noisy[y,x]=0
        processed_img=noisy

    elif choice == "Noise Removal":
        processed_img=cv2.medianBlur(base,5)

    elif choice == "HSV Convert":
        processed_img=cv2.cvtColor(base,cv2.COLOR_BGR2HSV)

    elif choice == "Edge Detection":
        edges=cv2.Canny(base,100,200)
        processed_img=cv2.cvtColor(edges,cv2.COLOR_GRAY2BGR)

    elif choice == "Histogram":
        show_histogram()
        return

    elif choice == "Compare Before/After":
        compare_images()
        return

    display_image(processed_img)
    update_status(choice+" Applied")


# =========================
# TRANSFORMS (PERSISTENT)
# =========================

def apply_transform(choice):
    global working_img, processed_img

    if choice == "Rotate":
        working_img=cv2.rotate(working_img,cv2.ROTATE_90_CLOCKWISE)

    elif choice == "Flip":
        working_img=cv2.flip(working_img,1)

    elif choice == "Resize":
        working_img=cv2.resize(working_img,(300,300))

    processed_img=working_img.copy()
    display_image(processed_img)
    update_status(choice+" Applied")


# =========================
# ROUTER
# =========================

def apply_operation(choice):

    if working_img is None:
        messagebox.showwarning("Warning","Load image first")
        return

    run_progress(choice+" Running")

    if choice in ["Rotate","Flip","Resize"]:
        apply_transform(choice)
    else:
        apply_filter(choice)

    stop_progress(choice+" Completed")


# =========================
# BRIGHTNESS SLIDER
# =========================

def update_brightness(value):
    global processed_img

    if working_img is None:
        return

    beta=int(value)

    processed_img=cv2.convertScaleAbs(working_img,alpha=1,beta=beta)

    display_image(processed_img)
    update_status(f"Brightness: {beta}")


# =========================
# GUI
# =========================

root=tk.Tk()
root.title("Mini Photoshop - DSP Project")
root.geometry("720x820")
root.configure(bg=PRIMARY_COLOR)

header=tk.Label(root,text="Mini Photoshop - DSP Image Editor",
                font=("Segoe UI",20,"bold"),
                fg=ACCENT_COLOR,bg=PRIMARY_COLOR)
header.pack(pady=10)

status_var=tk.StringVar()
status_var.set("Ready")

status_bar_frame=tk.Frame(root,bg="#0ea5e9",height=40)
status_bar_frame.pack(fill="x")

status_bar=tk.Label(status_bar_frame,
                    textvariable=status_var,
                    font=("Segoe UI",13,"bold"),
                    fg="white",
                    bg="#0ea5e9")
status_bar.pack(fill="both")

panel_frame=tk.Frame(root,bg=SECONDARY_COLOR)
panel_frame.pack(pady=10)

panel=tk.Label(panel_frame,bg=SECONDARY_COLOR)
panel.pack()

operations=[
"Gray","Binary","Rotate","Flip","Resize","Blur",
"Sharpen","Salt Noise","Pepper Noise","Noise Removal",
"HSV Convert","Edge Detection","Histogram","Compare Before/After"
]

selected=tk.StringVar()
selected.set("Select Operation")

menu=tk.OptionMenu(root,selected,*operations,command=apply_operation)
menu.config(width=30,font=("Segoe UI",12),
            bg=BUTTON_COLOR,fg="white")
menu.pack(pady=10)

btn_frame=tk.Frame(root,bg=PRIMARY_COLOR)
btn_frame.pack(pady=10)

style=dict(font=("Segoe UI",11,"bold"),
           bg=BUTTON_COLOR,fg="white",
           activebackground=ACCENT_COLOR,width=14)

tk.Button(btn_frame,text="Load Image",
          command=load_image,**style).grid(row=0,column=0,padx=6)

tk.Button(btn_frame,text="Save Image",
          command=save_image,**style).grid(row=0,column=1,padx=6)

tk.Button(btn_frame,text="Reset Image",
          command=reset_image,**style).grid(row=0,column=2,padx=6)

progress=ttk.Progressbar(root,orient="horizontal",
                         length=400,mode="indeterminate")
progress.pack(pady=10)

brightness_slider=tk.Scale(root,
                           from_=-100,to=100,
                           orient="horizontal",
                           label="Brightness Control",
                           length=300,
                           command=update_brightness)
brightness_slider.pack(pady=10)

root.mainloop()