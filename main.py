import tkinter as tk
import cv2
from PIL import Image, ImageTk
ventana= tk.Tk()
ventana.title("Lista de botones")
ventana.geometry("400x300")
label = tk.Label(ventana)
label.pack()
camara = cv2.VideoCapture(0)
def actualizar():
    ret,frame= camara.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        label.config(image=img)
        label.image = img
    ventana.after(30, actualizar)
actualizar()
def cerrar():
    camara.release()
    ventana.destroy()

ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.mainloop()