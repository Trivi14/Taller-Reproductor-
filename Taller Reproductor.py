import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import pygame
from mutagen.mp3 import MP3
import os

class Cancion:
    def __init__(self, titulo, ruta):
        self.titulo = titulo
        self.ruta = ruta
        self.duracion = self._obtener_duracion()

    def _obtener_duracion(self):
        try:
            audio = MP3(self.ruta)
            return audio.info.length
        except:
            return 0

    def obtener_duracion_formateada(self):
        minutos = int(self.duracion // 60)
        segundos = int(self.duracion % 60)
        return f"{minutos:02d}:{segundos:02d}"

class ListaReproduccion:
    def __init__(self):
        self.canciones = []

    def agregar_cancion(self, cancion, posicion=None):
        if posicion is None:
            self.canciones.append(cancion)  #Add to End
        else:
            self.canciones.insert(posicion, cancion)  #Add at specified position

    def eliminar_cancion(self, indice):
        if 0 <= indice < len(self.canciones):
            del self.canciones[indice]

    def obtener_lista(self):
        return self.canciones

    def obtener_cancion(self, indice):
        if 0 <= indice < len(self.canciones):
            return self.canciones[indice]
        return None

class ReproductorMP3:
    def __init__(self, master):
        self.master = master
        self.master.title("Reproductor MP3")
        self.playlist = ListaReproduccion()

        pygame.init()
        pygame.mixer.init()

        #Main frame
        self.frame_principal = tk.Frame(self.master)
        self.frame_principal.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        #Treeview Tracklist
        self.tree = ttk.Treeview(self.frame_principal, columns=('Título', 'Duración'), show='headings')
        self.tree.heading('Título', text='Título')
        self.tree.heading('Duración', text='Duración')
        self.tree.column('Título', width=300)
        self.tree.column('Duración', width=100)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        #Scrollbar for the Treeview
        self.scrollbar = ttk.Scrollbar(self.frame_principal, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        #Control button frame
        self.frame_botones = tk.Frame(self.master)
        self.frame_botones.pack(fill=tk.X, padx=10, pady=5)

        #Control buttons
        self.btn_agregar = tk.Button(self.frame_botones, text="Agregar Canción", command=self.agregar_cancion)
        self.btn_agregar.pack(side=tk.LEFT, padx=5)

        self.btn_eliminar = tk.Button(self.frame_botones, text="Eliminar Canción", command=self.eliminar_cancion)
        self.btn_eliminar.pack(side=tk.LEFT, padx=5)

        self.btn_reproducir = tk.Button(self.frame_botones, text="Reproducir", command=self.reproducir_cancion)
        self.btn_reproducir.pack(side=tk.LEFT, padx=5)

        self.btn_pausar = tk.Button(self.frame_botones, text="Pausar", command=self.pausar_cancion)
        self.btn_pausar.pack(side=tk.LEFT, padx=5)

        self.btn_detener = tk.Button(self.frame_botones, text="Detener", command=self.detener_cancion)
        self.btn_detener.pack(side=tk.LEFT, padx=5)

        #Buttons to move forward and backward in time
        self.btn_atrasar = tk.Button(self.frame_botones, text="Retroceder 5s", command=lambda: self.cambiar_tiempo(-5))
        self.btn_atrasar.pack(side=tk.LEFT, padx=5)

        self.btn_adelantar = tk.Button(self.frame_botones, text="Adelantar 5s", command=lambda: self.cambiar_tiempo(5))
        self.btn_adelantar.pack(side=tk.LEFT, padx=5)

        #Buttons to change songs
        self.btn_anterior = tk.Button(self.frame_botones, text="Canción Anterior", command=self.reproducir_cancion_anterior)
        self.btn_anterior.pack(side=tk.LEFT, padx=5)

        self.btn_siguiente = tk.Button(self.frame_botones, text="Siguiente Canción", command=self.reproducir_cancion_siguiente)
        self.btn_siguiente.pack(side=tk.LEFT, padx=5)

        #Slider for the progress bar
        self.slider = tk.Scale(self.master, from_=0, to=100, orient=tk.HORIZONTAL, label="Progreso", length=300, command=self.cambiar_tiempo_slider)
        self.slider.pack(pady=10)

        #Labels to show total duration and current time
        self.lbl_duracion_total = tk.Label(self.master, text="Duración: 00:00")
        self.lbl_duracion_total.pack(side=tk.LEFT, padx=5)

        self.lbl_tiempo_actual = tk.Label(self.master, text="Tiempo: 00:00")
        self.lbl_tiempo_actual.pack(side=tk.RIGHT, padx=5)

        #Tag to display the current song
        self.lbl_actual = tk.Label(self.master, text="No hay canción seleccionada")
        self.lbl_actual.pack(pady=5)

        self.esta_reproduciendo = False
        self.current_song = None
        self.current_position = 0  #Maintain Current Position

        #Progress bar update
        self.master.after(1000, self.actualizar_progreso)

    def agregar_cancion(self):
        ruta = filedialog.askopenfilename(title="Seleccionar archivo", filetypes=[("Archivos MP3", "*.mp3")])
        if ruta:
            titulo = os.path.basename(ruta)
            nueva_cancion = Cancion(titulo, ruta)
            posicion = simpledialog.askinteger("Agregar Canción", "Agregar al inicio (0), al final (-1) o en posición (número)?", minvalue=-1, maxvalue=len(self.playlist.canciones))
            if posicion is not None:
                if posicion == -1:  #Add at the end
                    self.playlist.agregar_cancion(nueva_cancion)
                elif posicion >= 0:  #Add in a specific position
                    self.playlist.agregar_cancion(nueva_cancion, posicion)
                self.actualizar_lista()

    def eliminar_cancion(self):
        seleccion = self.tree.selection()
        if seleccion:
            indice = int(seleccion[0]) - 1
            self.playlist.eliminar_cancion(indice)
            self.actualizar_lista()

    def reproducir_cancion(self):
        seleccion = self.tree.selection()
        if seleccion:
            indice = int(seleccion[0]) - 1
            cancion = self.playlist.obtener_cancion(indice)
            if cancion:
                self.lbl_actual.config(text=f"Reproduciendo: {cancion.titulo}")
                try:
                    pygame.mixer.music.load(cancion.ruta)
                    pygame.mixer.music.play(start=self.current_position)
                    self.esta_reproduciendo = True
                    self.current_song = cancion
                    self.slider.config(to=cancion.duracion)
                    self.lbl_duracion_total.config(text=f"Duración: {cancion.obtener_duracion_formateada()}")
                    self.lbl_tiempo_actual.config(text="Tiempo: 00:00")
                except pygame.error as e:
                    messagebox.showerror("Error", f"No se pudo reproducir la canción: {str(e)}")
        else:
            messagebox.showinfo("Información", "No se ha seleccionado ninguna canción")

    def reproducir_cancion_anterior(self):
        if self.current_song:
            indice_actual = self.playlist.canciones.index(self.current_song)
            if indice_actual > 0:
                self.reproducir_cancion_en_pos(indice_actual - 1)

    def reproducir_cancion_siguiente(self):
        if self.current_song:
            indice_actual = self.playlist.canciones.index(self.current_song)
            if indice_actual < len(self.playlist.canciones) - 1:
                self.reproducir_cancion_en_pos(indice_actual + 1)

    def reproducir_cancion_en_pos(self, indice):
        cancion = self.playlist.obtener_cancion(indice)
        if cancion:
            self.lbl_actual.config(text=f"Reproduciendo: {cancion.titulo}")
            try:
                pygame.mixer.music.load(cancion.ruta)
                pygame.mixer.music.play(start=self.current_position)
                self.esta_reproduciendo = True
                self.current_song = cancion
                self.slider.config(to=cancion.duracion)
                self.lbl_duracion_total.config(text=f"Duración: {cancion.obtener_duracion_formateada()}")
                self.lbl_tiempo_actual.config(text="Tiempo: 00:00")
            except pygame.error as e:
                messagebox.showerror("Error", f"No se pudo reproducir la canción: {str(e)}")

    def pausar_cancion(self):
        if self.esta_reproduciendo:
            pygame.mixer.music.pause()
            self.esta_reproduciendo = False

    def detener_cancion(self):
        if self.esta_reproduciendo:
            pygame.mixer.music.stop()
            self.esta_reproduciendo = False
            self.current_position = 0  #Restart the position on stop

    def cambiar_tiempo(self, segundos):
        if self.current_song:
            self.current_position += segundos
            if self.current_position < 0:
                self.current_position = 0
            if self.current_position > self.current_song.duracion:
                self.current_position = self.current_song.duracion
            pygame.mixer.music.play(start=self.current_position)

    def cambiar_tiempo_slider(self, valor):
        self.current_position = float(valor)
        if self.current_song:
            pygame.mixer.music.play(start=self.current_position)

    def actualizar_lista(self):
        self.tree.delete(*self.tree.get_children())
        for i, cancion in enumerate(self.playlist.obtener_lista()):
            self.tree.insert('', 'end', iid=i + 1, values=(cancion.titulo, cancion.obtener_duracion_formateada()))

    def actualizar_progreso(self):
        if self.esta_reproduciendo and self.current_song:
            tiempo_actual = pygame.mixer.music.get_pos() / 1000 + self.current_position  #Add the current position
            self.slider.set(tiempo_actual)  #Update the slider
            self.lbl_tiempo_actual.config(text=f"Tiempo: {int(tiempo_actual // 60):02d}:{int(tiempo_actual % 60):02d}")

        self.master.after(1000, self.actualizar_progreso)  #Refresh every second

if __name__ == "__main__":
    root = tk.Tk()
    app = ReproductorMP3(root)
    root.mainloop()