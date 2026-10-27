import tkinter as tk
from tkinter import messagebox
import cv2
import face_recognition
import pickle
from PIL import Image, ImageTk
from pathlib import Path


# ==========================
# CONFIGURACION
# ==========================

BASE_DIR = Path(__file__).resolve().parent
ARCHIVO_USUARIOS = BASE_DIR / "usuarios.pkl"


# ==========================
# CARGAR / GUARDAR
# ==========================

def cargar_usuarios():
    if ARCHIVO_USUARIOS.exists():
        with open(ARCHIVO_USUARIOS, "rb") as archivo:
            return pickle.load(archivo)
    return []


def guardar_usuarios():
    with open(ARCHIVO_USUARIOS, "wb") as archivo:
        pickle.dump(usuarios, archivo)


# ==========================
# VENTANA
# ==========================

ventana = tk.Tk()
ventana.title("Control de Acceso Facial")
ventana.geometry("900x700")


label_video = tk.Label(ventana)
label_video.pack()


# ==========================
# VARIABLES
# ==========================

usuarios = cargar_usuarios()

cara_actual = None
encoding_actual = None

camara = cv2.VideoCapture(0)


# ==========================
# LISTA DE USUARIOS
# ==========================

lista_usuarios = tk.Listbox(
    ventana,
    width=40,
    height=8
)

lista_usuarios.pack(pady=10)


def actualizar_lista():

    lista_usuarios.delete(
        0,
        tk.END
    )

    for usuario in usuarios:

        lista_usuarios.insert(
            tk.END,
            usuario["nombre"]
        )


# ==========================
# ENTRY NOMBRE
# ==========================

tk.Label(
    ventana,
    text="Nombre:"
).pack()

entry_nombre = tk.Entry(ventana)
entry_nombre.pack()


# ==========================
# WEBCAM
# ==========================

def actualizar():

    global cara_actual
    global encoding_actual

    ret, frame = camara.read()

    if ret:

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        caras = face_recognition.face_locations(rgb)

        encoding_actual = None
        cara_actual = None

        for cara in caras:

            top, right, bottom, left = cara

            cv2.rectangle(
                rgb,
                (left, top),
                (right, bottom),
                (0, 255, 0),
                2
            )

            cara_actual = rgb[
                top:bottom,
                left:right
            ]

            enc = face_recognition.face_encodings(
                rgb,
                [cara]
            )

            if enc:
                encoding_actual = enc[0]

            break

        img = ImageTk.PhotoImage(
            Image.fromarray(rgb)
        )

        label_video.config(image=img)
        label_video.image = img

    ventana.after(
        10,
        actualizar
    )


# ==========================
# REGISTRAR
# ==========================

def registrar():

    global encoding_actual

    nombre = entry_nombre.get().strip()

    if not nombre:

        messagebox.showwarning(
            "Error",
            "Introduce un nombre"
        )
        return

    if encoding_actual is None:

        messagebox.showwarning(
            "Error",
            "No se detectó ninguna cara"
        )
        return

    usuarios.append(
        {
            "nombre": nombre,
            "encoding": encoding_actual
        }
    )

    guardar_usuarios()
    actualizar_lista()

    entry_nombre.delete(
        0,
        tk.END
    )

    messagebox.showinfo(
        "Correcto",
        f"{nombre} registrado"
    )


# ==========================
# ELIMINAR
# ==========================

def eliminar():

    seleccion = lista_usuarios.curselection()

    if not seleccion:
        return

    indice = seleccion[0]

    usuarios.pop(indice)

    guardar_usuarios()
    actualizar_lista()


# ==========================
# VERIFICAR
# ==========================

def verificar():

    global encoding_actual

    if encoding_actual is None:

        messagebox.showwarning(
            "Error",
            "No se detectó ninguna cara"
        )

        return

    mejor_nombre = None

    for usuario in usuarios:

        resultado = face_recognition.compare_faces(
            [usuario["encoding"]],
            encoding_actual
        )

        if resultado[0]:

            mejor_nombre = usuario["nombre"]
            break

    if mejor_nombre:

        messagebox.showinfo(
            "Acceso",
            f"Autorizado: {mejor_nombre}"
        )

    else:

        messagebox.showwarning(
            "Acceso",
            "Persona NO autorizada"
        )


# ==========================
# BOTONES
# ==========================

frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=10)

tk.Button(
    frame_botones,
    text="Registrar",
    command=registrar
).pack(side="left", padx=5)

tk.Button(
    frame_botones,
    text="Eliminar",
    command=eliminar
).pack(side="left", padx=5)

tk.Button(
    frame_botones,
    text="Verificar",
    command=verificar
).pack(side="left", padx=5)


# ==========================
# CIERRE
# ==========================

def cerrar():

    camara.release()
    ventana.destroy()


ventana.protocol(
    "WM_DELETE_WINDOW",
    cerrar
)

actualizar()
actualizar_lista()

ventana.mainloop()