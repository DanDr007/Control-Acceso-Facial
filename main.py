import tkinter as tk
from tkinter import messagebox, filedialog
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
# CARGAR / GUARDAR
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


# ==========================
# DATOS
# ==========================

usuarios = cargar_usuarios()

ultimo_frame_rgb = None
ultima_cara = None

# ==========================
# TKINTER
# ==========================

ventana = tk.Tk()
ventana.title("Control de Acceso Facial")
ventana.geometry("900x700")

label_video = tk.Label(ventana)
label_video.pack()

# ==========================
# ENTRY NOMBRE
# ==========================

tk.Label(
    ventana,
    text="Nombre"
).pack()

entry_nombre = tk.Entry(
    ventana,
    width=40
)
entry_nombre.pack(pady=5)

# ==========================
# LISTA USUARIOS
# ==========================

lista_usuarios = tk.Listbox(
    ventana,
    width=50,
    height=8
)

lista_usuarios.pack(pady=10)


def actualizar_lista():

    lista_usuarios.delete(0, tk.END)

    for usuario in usuarios:

        lista_usuarios.insert(
            tk.END,
            usuario["nombre"]
        )


# ==========================
# CAMARA
# ==========================

camara = cv2.VideoCapture(0)

# ==========================
# DETECCION
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

        frame_pequeño = cv2.resize(
            rgb,
            (0, 0),
            fx=0.25,
            fy=0.25
        )

        caras = face_recognition.face_locations(
            frame_pequeño
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
        or
        ultima_cara is None
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
# REGISTRAR WEBCAM
# ==========================

def registrar():

    nombre = entry_nombre.get().strip()

    if not nombre:

        messagebox.showwarning(
            "Error",
            "Introduce un nombre"
        )
        return

    for usuario in usuarios:

        if usuario["nombre"].lower() == nombre.lower():

            messagebox.showwarning(
                "Error",
                "Ese usuario ya existe"
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
# REGISTRAR IMAGEN
# ==========================

def registrar_imagen():

    nombre = entry_nombre.get().strip()

    if not nombre:

        messagebox.showwarning(
            "Error",
            "Introduce un nombre"
        )

        return

    for usuario in usuarios:

        if usuario["nombre"].lower() == nombre.lower():

            messagebox.showwarning(
                "Error",
                "Ese usuario ya existe"
            )

            return

    ruta = filedialog.askopenfilename(
        title="Seleccionar imagen",
        filetypes=[
            ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.webp")
        ]
    )

    if not ruta:
        return

    try:

        imagen = face_recognition.load_image_file(
            ruta
        )

        caras = face_recognition.face_locations(
            imagen
        )

        if len(caras) == 0:

            messagebox.showwarning(
                "Error",
                "No se detectó ninguna cara"
            )

            return

        if len(caras) > 1:

            messagebox.showwarning(
                "Error",
                "La imagen contiene más de una cara"
            )

            return

        encoding = face_recognition.face_encodings(
            imagen,
            [caras[0]]
        )

        if not encoding:

            messagebox.showwarning(
                "Error",
                "No se pudo generar el encoding"
            )

            return

        usuarios.append(
            {
                "nombre": nombre,
                "encoding": encoding[0]
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
            f"{nombre} registrado desde imagen"
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )

# ==========================
# ELIMINAR
# ==========================

def eliminar():

    seleccion = lista_usuarios.curselection()

    if not seleccion:
        return

    indice = seleccion[0]

    nombre = usuarios[indice]["nombre"]

    respuesta = messagebox.askyesno(
        "Confirmación",
        f"¿Eliminar a {nombre}?"
    )

    if not respuesta:
        return

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
    mejor_distancia = 1.0

    for usuario in usuarios:

        distancia = face_recognition.face_distance(
            [usuario["encoding"]],
            encoding_actual
        )[0]

        if distancia < mejor_distancia:

            mejor_distancia = distancia
            mejor_nombre = usuario["nombre"]

    if mejor_nombre is not None and mejor_distancia < 0.5:

        messagebox.showinfo(
            "Acceso concedido",
            f"Usuario autorizado:\n\n{mejor_nombre}\n\nDistancia: {mejor_distancia:.3f}"
        )

    else:

        messagebox.showwarning(
            "Acceso denegado",
            "Usuario no autorizado"
        )

# ==========================
# BOTONES
# ==========================

frame_botones = tk.Frame(
    ventana
)
frame_botones.pack(pady=10)

tk.Button(
    frame_botones,
    text="Registrar Webcam",
    command=registrar
).pack(
    side="left",
    padx=5
)

tk.Button(
    frame_botones,
    text="Registrar Imagen",
    command=registrar_imagen
).pack(
    side="left",
    padx=5
)

tk.Button(
    frame_botones,
    text="Verificar",
    command=verificar
).pack(
    side="left",
    padx=5
)

tk.Button(
    frame_botones,
    text="Eliminar",
    command=eliminar
).pack(
    side="left",
    padx=5
)

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