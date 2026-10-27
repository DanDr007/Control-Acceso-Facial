import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition
ventana= tk.Tk()
ventana.title("Lista de botones")
ventana.geometry("400x300")
capturas=[]
aux=[]
label = tk.Label(ventana)
label.pack()
camara = cv2.VideoCapture(0)
def actualizar():
    capturas.clear()
    ret,frame= camara.read()
    if ret:
        
        ##_, frame = cv2.threshold(frame,127,255,cv2.THRESH_BINARY)
        ##frame= cv2.Canny(frame, 100, 200)
        frame = cv2.GaussianBlur(frame,(3, 3),0)
        captura = None
        gris= cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gris = cv2.equalizeHist(gris)
        captura = gris.copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        caras = face_recognition.face_locations(frame)
        for cara in caras:
            top, right, bottom, left = cara
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 50), 2)
            capturas.append(captura[top:bottom, left:right])
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        label.config(image=img)
        label.image = img
    ventana.after(15, actualizar)
def cara():
    for label in aux:
        label.destroy()

    aux.clear()
    for captura in capturas:
        label2 = tk.Label(ventana)
        img2= ImageTk.PhotoImage(Image.fromarray(captura))
        label2.config(image=img2)
        label2.image = img2
        label2.pack()
        aux.append(label2)
        
boton=tk.Button(ventana, text="Capturar cara", command=cara)
boton.pack()
actualizar()
def cerrar():
    camara.release()
    ventana.destroy()

ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.mainloop()