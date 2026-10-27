import tkinter as tk
from tkinter import messagebox
import cv2
import face_recognition
import pickle
from pathlib import Path
from PIL import Image, ImageTk

# ==========================
# CONFIGURACION
# ==========================

BASE_DIR = Path(__file__).resolve().parent
ARCHIVO_USUARIOS = BASE_DIR / "usuarios.pkl"

# ==========================
# DATOS
# ==========================

def cargar_usuarios():
    try:
        with open(ARCHIVO_USUARIOS, "rb") as f:
            return pickle.load(f)
    except:
        return []

def guardar_usuarios():
    with open(ARCHIVO_USUARIOS, "wb") as f:
        pickle.dump(usuarios, f)

usuarios = cargar_usuarios()

# ==========================
# TKINTER
# ==========================

ventana = tk.Tk()
ventana.title("Control de Acceso Facial")
ventana.geometry("900x700")

label_video = tk.Label(ventana)
label_video.pack()

tk.Label(
    ventana,
    text="Nombre"
).pack()

entry_nombre = tk.Entry(ventana)
entry_nombre.pack()

lista_usuarios = tk.Listbox(
    ventana,
    width=40,
    height=8
)

lista_usuarios.pack(pady=10)

# ==========================
# VARIABLES
# ==========================

camara = cv2.VideoCapture(0)

ultimo_frame_rgb = None
ultima_cara = None

# ==========================
# LISTBOX
# ==========================

def actualizar_lista():

    lista_usuarios.delete(0, tk.END)

    for usuario in usuarios:

        lista_usuarios.insert(
            tk.END,
            usuario["nombre"]
        )

# ==========================
# WEBCAM
# ==========================

def actualizar():

    global ultimo_frame_rgb
    global ultima_cara

    ret, frame = camara.read()

    if ret:

        frame = cv2.flip(frame, 1)

        frame = cv2.resize(
            frame,
            (640, 480)
        )

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        ultimo_frame_rgb = rgb.copy()
        ultima_cara = None

        pequeño = cv2.resize(
            rgb,
            (0, 0),
            fx=0.25,
            fy=0.25
        )

        caras = face_recognition.face_locations(
            pequeño
        )

        for top, right, bottom, left in caras:

            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            ultima_cara = (
                top,
                right,
                bottom,
                left
            )

            cv2.rectangle(
                rgb,
                (left, top),
                (right, bottom),
                (0, 255, 0),
                2
            )

        img = ImageTk.PhotoImage(
            Image.fromarray(rgb)
        )

        label_video.config(image=img)
        label_video.image = img

    ventana.after(30, actualizar)

# ==========================
# OBTENER ENCODING
# ==========================

def obtener_encoding_actual():

    if (
        ultimo_frame_rgb is None
        or ultima_cara is None
    ):
        return None

    encodings = face_recognition.face_encodings(
        ultimo_frame_rgb,
        [ultima_cara]
    )

    if not encodings:
        return None

    return encodings[0]

# ==========================
# REGISTRAR
# ==========================

def registrar():

    nombre = entry_nombre.get().strip()

    if not nombre:

        messagebox.showwarning(
            "Error",
            "Introduce un nombre"
        )

        return

    encoding = obtener_encoding_actual()

    if encoding is None:

        messagebox.showwarning(
            "Error",
            "No se detectó ninguna cara"
        )

        return

    usuarios.append(
        {
            "nombre": nombre,
            "encoding": encoding
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

    encoding_actual = obtener_encoding_actual()

    if encoding_actual is None:

        messagebox.showwarning(
            "Error",
            "No se detectó ninguna cara"
        )

        return

    mejor_nombre = None

    for usuario in usuarios:

        distancia = face_recognition.face_distance(
            [usuario["encoding"]],
            encoding_actual
        )[0]

        if distancia < 0.5:

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
            "NO AUTORIZADO"
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
# CERRAR
# ==========================

def cerrar():

    camara.release()
    ventana.destroy()

ventana.protocol(
    "WM_DELETE_WINDOW",
    cerrar
)

actualizar_lista()
actualizar()

ventana.mainloop()