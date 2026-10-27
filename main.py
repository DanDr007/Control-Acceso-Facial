import tkinter as tk
from pathlib import Path
import cv2
from PIL import Image, ImageTk
import face_recognition
BASE_DIR = Path(__file__).resolve().parent
RUTA_CARAS= BASE_DIR / "caras"
ventana= tk.Tk()
ventana.title("Lista de botones")
ventana.geometry("600x600")
capturas=[]
capturas2=[]
encodings=[]
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
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        captura = frame.copy()
        caras = face_recognition.face_locations(frame)
        
        
        for cara in caras:
            top, right, bottom, left = cara
            encoding= face_recognition.face_encodings(frame,[cara])
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 50), 2)
            capturas.append(captura[top:bottom, left:right])
            encodings.append(encoding)
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        label.config(image=img)
        label.image = img
    ventana.after(15, actualizar)
def cara():
    global capturas2
    capturas2=capturas.copy()
    for label in aux:
        label.destroy()

    aux.clear()
    for captura in capturas2:
        label2 = tk.Label(ventana)
        img2= ImageTk.PhotoImage(Image.fromarray(captura))
        label2.config(image=img2)
        label2.image = img2
        label2.pack()
        aux.append(label2)
def guardar_capturas(capturas):
    for i, captura in enumerate(capturas):
        nombre_archivo = f"{RUTA_CARAS}/captura_{i}.jpg"
        cv2.imwrite(nombre_archivo, captura)

def coincidencias(capturas):
    coincidencias = []
    for i in range(len(capturas)):
        cara1 = face_recognition.load_image_file(f"{RUTA_CARAS}/captura_{i}.jpg")
        codificacion_cara1 = face_recognition.face_encodings(cara1)[0]
        codificacion_caraActual = face_recognition.face_encodings(encodings[0])[0]
        resultado = face_recognition.compare_faces([codificacion_cara1], codificacion_caraActual)
        if resultado[0]:
            coincidencias.append(i)
    if coincidencias:
        mensaje = "Se encontraron coincidencias entre las siguientes capturas:\n"
        for i in coincidencias:
            mensaje += f"Captura {i}\n"
    else:
        mensaje = "No se encontraron coincidencias entre las capturas."
    ventana_coincidencias = tk.Toplevel(ventana)
    ventana_coincidencias.title("Coincidencias")
    label_mensaje = tk.Label(ventana_coincidencias, text=mensaje)
    label_mensaje.pack()
boton=tk.Button(ventana, text="Capturar cara", command=cara)
btnGuardar = tk.Button(ventana, text="Guardar capturas", command=lambda: guardar_capturas(capturas2))
boton.pack()
btnGuardar.pack()
btnCoincidencias = tk.Button(ventana, text="Ver coincidencias", command=lambda: coincidencias(capturas2))
btnCoincidencias.pack()
actualizar()
def cerrar():
    camara.release()
    ventana.destroy()

ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.mainloop()