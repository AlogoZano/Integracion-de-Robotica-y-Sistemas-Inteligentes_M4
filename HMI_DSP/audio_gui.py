"""Interfaz humano-máquina de procesamiento de audio."""
import librosa
import matplotlib.pyplot as plt
import numpy as np
import pygame
import sounddevice as sd
import soundfile as sf
from customtkinter import (CTk, CTkButton, CTkComboBox, CTkEntry, CTkFrame,
                           CTkLabel, CTkToplevel, filedialog)
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from pydub import AudioSegment
from scipy import signal

audio_path = ""
filtered = 0
filtered_signal = []
sampling_rate = 0

app = CTk()
pygame.mixer.init()

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

app.geometry(f"{screen_width}x{screen_height}+0+0")


def open_audio(file_path):
    """
    Leer archivo .wav, .mp3.

    - Carga de audio con Librosa.
    - Devuelve señal como arreglo de numpy y frecuencia de muestreo
    """
    y, sr = librosa.load(file_path)
    return y, sr


def load_file():
    """
    Cargar archivo a interfaz.

    - Una vez leído el audio con open_audio(), se carga a la interfaz.
    i.e. se grafica.
    """
    global audio_path
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo de audio",
        filetypes=(
            ("Archivos de audio", "*.mp3;*.wav;*.aac"),
            ("Todos los archivos", "*.*"),
        ),
    )

    if file_path:
        print(f"Archivo seleccionado: {file_path}")
        audio_path = file_path
        audio_data, sr = open_audio(file_path=file_path)
        plot_audio_data(audio_data, sr, audio_frame)


def plot_audio_data(audio_data, sr, frame):
    """
    Graficación de señal de audio.

    - Graficar la señal de audio extraída directamente del archivo.
    - Para señal cruda y procesada de igual forma.
    """
    for widget in frame.winfo_children():
        widget.destroy()

    for widget in fft_frame.winfo_children():
        widget.destroy()

    for widget in filter_fft_frame.winfo_children():
        widget.destroy()

    for widget in filter_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(5, 2))

    ax.plot(audio_data)
    ax.set_title("Señal de Audio")
    ax.set_xlabel("Muestra")
    ax.set_ylabel("Amplitud")

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, frame)
    toolbar.update()

    toolbar.grid(row=0, column=0, sticky="nsew")

    canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")

    frame.grid_rowconfigure(0, weight=0)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)


def apply_transform():
    """
    Función activada por "Aplicar transformada".

    - Una vez obtenida la transformada se grafica.
    - Es una función de acción en un botón posterior.
    """
    if len(audio_path):
        print(f"Archivo seleccionado para FFT: {audio_path}")
        audio_data, framerate = open_audio(file_path=audio_path)
        plot_transform(audio_data, framerate, frame=fft_frame)
    else:
        show_warn()


def plot_transform(audio_data, framerate, frame):
    """
    Cálculo de fft y graficación.

    - Se admite el arreglo de audio, frecuencia de muestreo y
      el marco donde se graficará.
    - Se calculan los componentes frecuenciales, se normaliza y grafica.
    """
    n = len(audio_data)
    fft_result = np.fft.fft(audio_data)
    fft_freq = np.fft.fftfreq(n, d=1 / framerate)

    positive_freqs = fft_freq[: n // 2]
    positive_magnitude = np.abs(fft_result)[: n // 2]
    positive_magnitude /= n

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(positive_freqs, positive_magnitude)

    ax.set_title("FFT del Audio")
    ax.set_xlabel("Frecuencia (Hz)")
    ax.set_ylabel("Magnitud")

    canvas_plot = FigureCanvasTkAgg(fig, master=frame)
    canvas_plot.draw()

    toolbar = NavigationToolbar2Tk(canvas_plot, frame)
    toolbar.update()

    toolbar.grid(row=0, column=0, sticky="nsew")

    canvas_plot.get_tk_widget().grid(row=1, column=0, sticky="nsew")

    frame.grid_rowconfigure(0, weight=0)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)


def apply_lowpass_filter(audio_data, framerate, cutoff_freq, order=2):
    """
    Aplicar filtro pasa bajas.

    - Función que genera coeficientes de filtro pasa bajas con
      scipy.signal butter y filtra con signal.filtfilt
    """
    nyquist = 0.5 * framerate
    normal_cutoff = cutoff_freq / nyquist
    b, a = signal.butter(order, normal_cutoff, btype="low", analog=False)
    filtered_audio = signal.filtfilt(b, a, audio_data)

    return filtered_audio


def apply_highpass_filter(audio_data, framerate, cutoff_freq, order=2):
    """
    Aplicar filtro pasa altas.

    - Función que genera coeficientes de filtro pasa altas con
      scipy.signal butter y filtra con signal.filtfilt
    """
    nyquist = 0.5 * framerate
    normal_cutoff = cutoff_freq / nyquist
    b, a = signal.butter(order, normal_cutoff, btype="high", analog=False)
    filtered_audio = signal.filtfilt(b, a, audio_data)
    return filtered_audio


def apply_bandpass_filter(audio_data, framerate, cutoff_freq, order=2):
    """
    Aplicar filtro pasa banda.

    - Función que genera coeficientes de filtro pasa bandas con
      scipy.signal butter y filtra con signal.filtfilt, se necesitan
      dos niveles de frecuencia de corte (alta y baja)
    """
    nyquist = 0.5 * framerate
    low_cutoff = cutoff_freq[0] / nyquist
    high_cuttof = cutoff_freq[1] / nyquist
    b, a = signal.butter(
        order, [low_cutoff, high_cuttof], btype="bandpass", analog=False
    )

    filtered_audio = signal.filtfilt(b, a, audio_data)
    return filtered_audio


def apply_filter(audio_data, sr, filter_type, cutoff, order):
    """
    Aplicar filtro general, selección.

    - Función que organiza los filtros, se llama al seleccionar
      el botón de "Guardar" en la configuración de filtro.
    """
    global filtered
    filtered = 1

    if filter_type == "Pasa bajas":
        return apply_lowpass_filter(audio_data, sr, cutoff, order)
    elif filter_type == "Pasa altas":
        return apply_highpass_filter(audio_data, sr, cutoff, order)
    elif filter_type == "Pasa banda":
        return apply_bandpass_filter(audio_data, sr, cutoff, order)


def configure_filter():
    """
    Función de alto nivel para configurar filtro.

    - Función que llama la ejecución de configuración de filtro.
    - Se ejecuta al presionar el botón "Aplicar filtro"
    """
    global audio_path
    if len(audio_path):
        audio_data, sr = open_audio(file_path=audio_path)
        filter_conf(audio_data=audio_data, sr=sr)
    else:
        show_warn()


def filter_conf(audio_data, sr):
    """
    Configuración de filtro.

    - Ventana para seleccionar parámetros del filtro.
    """
    f_popup = CTkToplevel(app)
    f_popup.title("Configuración de filtro")
    f_popup.geometry("400x550")

    label = CTkLabel(f_popup, text="Configuración de filtro")
    label.pack(pady=10)

    filt_label = CTkLabel(f_popup, text="Selecciona tipo de filtro:")

    filt_label.pack(pady=5)
    filter_type_combo = CTkComboBox(
        f_popup, values=["Pasa bajas", "Pasa altas", "Pasa banda"], width=200
    )
    filter_type_combo.pack(pady=10)

    cutoff_label_1 = CTkLabel(f_popup, text="Frecuencia de corte (Hz):")
    cutoff_label_1.pack(pady=5)
    cutoff_entry_1 = CTkEntry(f_popup, placeholder_text="Ej. 1000", width=200)
    cutoff_entry_1.pack(pady=10)

    cutoff_label_2 = CTkLabel(f_popup, text="Frecuencia de corte alta (Hz):")
    cutoff_entry_2 = CTkEntry(f_popup, placeholder_text="Ej. 3000", width=200)

    order_label = CTkLabel(f_popup, text="Selecciona el orden del filtro:")
    order_label.pack(pady=5)
    val = [str(i) for i in range(1, 6)]
    order_combo = CTkComboBox(f_popup, values=val, width=200)
    order_combo.pack(pady=10)

    def update_cutoff_inputs(choice):
        if choice == "Pasa banda":
            cutoff_label_2.pack(pady=5)
            cutoff_entry_2.pack(pady=10)
            cutoff_label_1.configure(text="Frecuencia de corte baja (Hz):")
        else:
            cutoff_label_2.pack_forget()
            cutoff_entry_2.pack_forget()
            cutoff_label_1.configure(text="Frecuencia de corte (Hz):")

    filter_type_combo.configure(command=update_cutoff_inputs)

    def store_settings():
        filter_type = filter_type_combo.get()
        order = int(order_combo.get())

        try:
            if filter_type == "Pasa banda":
                cutoff1 = float(cutoff_entry_1.get())
                cutoff2 = float(cutoff_entry_2.get())
                cutoff = [cutoff1, cutoff2]
            else:
                cutoff = float(cutoff_entry_1.get())
        except ValueError:
            print("Error: Las frecuencias deben ser números válidos.")
            return

        print(f"Filter Type: {filter_type}")
        print(f"Cut-off Frequency: {cutoff} Hz")
        print(f"Filter Order: {order}")

        f_popup.destroy()

        filtered_audio = apply_filter(
            audio_data=audio_data,
            sr=sr,
            filter_type=filter_type,
            cutoff=cutoff,
            order=order,
        )
        global filtered_signal
        filtered_signal = filtered_audio

        global sampling_rate
        sampling_rate = sr
        plot_audio_data(filtered_audio, sr, filter_frame)

        plot_transform(filtered_audio, sr, filter_fft_frame)

    def cancel():
        f_popup.destroy()

    store_button = CTkButton(f_popup, text="Guardar", command=store_settings)

    store_button.pack(side="left", padx=20, pady=20)

    cancel_button = CTkButton(f_popup, text="Cancelar", command=cancel)

    cancel_button.pack(side="right", padx=20, pady=20)


def show_warn():
    """
    Alerta de falta de audio.

    - Función que genera un "pop-up" de alerta.
    - Generalmente de no audio cargado.
    """
    popup = CTkToplevel(app)
    popup.title("Advertencia")
    popup.geometry("350x150")

    label = CTkLabel(popup, text="¡Se debe de cargar un archivo de audio!")

    label.pack(pady=20)

    close_button = CTkButton(popup, text="Ok", command=popup.destroy)
    close_button.pack(pady=10)


def show_warn_filter():
    """
    Alerta de filtro no aplicado.

    - Función que genera un "pop-up" de alerta.
    - Generalmente de filtro no aplicado aún.
    """
    popup = CTkToplevel(app)
    popup.title("Advertencia")
    popup.geometry("350x150")

    label = CTkLabel(popup, text="¡Primero se debe de aplicar algún filtro!")
    label.pack(pady=20)

    close_button = CTkButton(popup, text="Ok", command=popup.destroy)
    close_button.pack(pady=10)


def play_audio():
    """
    Reproducción de audio.

    - Función que reproduce el audio cargado.
    - Es necesario convertirlo a WAV para la reproducción predeterminada.
    """
    global audio_path
    if len(audio_path):
        try:
            temp_wav = "temp_audio.wav"
            sound = AudioSegment.from_file(audio_path)
            sound.export(temp_wav, format="wav")

            pygame.mixer.init()
            pygame.mixer.music.load(temp_wav)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error reproduciendo audio: {e}")
    else:
        show_warn()


def play_filtered_audio():
    """
    Reproducción de audio procesado.

    - Función que reproduce el audio procesado.
    """
    global filtered_signal
    global sampling_rate

    if filtered_signal is not None:
        try:
            sd.play(filtered_signal, sampling_rate)
        except Exception as e:
            print(f"Error reproduciendo audio filtrado: {e}")
    else:
        print("No hay señal filtrada para reproducir.")
        show_warn_filter()


def delete_audio():
    """Borrar el audio cargado; "Reinicia todo"."""
    global audio_path
    global filtered
    filtered = 0
    if len(audio_path):
        audio_path = ""

        for widget in audio_frame.winfo_children():
            widget.destroy()

        for widget in fft_frame.winfo_children():
            widget.destroy()

        for widget in filter_fft_frame.winfo_children():
            widget.destroy()

        for widget in filter_frame.winfo_children():
            widget.destroy()

    else:
        show_warn()


def store_audio():
    """Función para guardar audio en 4 formatos distintos."""
    global audio_path
    global filtered

    if not len(audio_path):
        show_warn()
        return
    elif len(audio_path) and not filtered:
        show_warn_filter()
        return

    filetypes = [
        ("WAV", "*.wav"),
        ("FLAC", "*.flac"),
        ("OGG", "*.ogg"),
        ("MP3", "*.mp3"),
    ]
    save_path = filedialog.asksaveasfilename(
        title="Guardar", defaultextension=".wav", filetypes=filetypes
    )

    if save_path:
        try:
            sf.write(save_path, filtered_signal, sampling_rate)
            print(f"Audio guardado en: {save_path}")
        except Exception as e:
            print(f"Error al guardar el audio: {e}")


app.grid_columnconfigure((0, 1), weight=1)
app.grid_rowconfigure(0, weight=2)
app.grid_rowconfigure(1, weight=1)
app.grid_rowconfigure(2, weight=1)
app.grid_rowconfigure(3, weight=2)

main_conf = CTkFrame(app, fg_color="black")
main_conf.grid(row=0, column=0, columnspan=2, sticky="nsew")
app.grid_columnconfigure(0, weight=1)

audio_frame = CTkFrame(app, fg_color="white")
audio_frame.grid(row=1, column=0, sticky="nsew")
app.grid_columnconfigure(0, weight=1)

fft_frame = CTkFrame(app, fg_color="white")
fft_frame.grid(row=2, column=0, sticky="nsew")
app.grid_columnconfigure(0, weight=1)

filter_frame = CTkFrame(app, fg_color="white")
filter_frame.grid(row=1, column=1, sticky="nsew")
app.grid_columnconfigure(0, weight=1)

filter_fft_frame = CTkFrame(app, fg_color="white")
filter_fft_frame.grid(row=2, column=1, sticky="nsew")
app.grid_columnconfigure(0, weight=1)

output_frame = CTkFrame(app, fg_color="black")
output_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")
app.grid_columnconfigure(0, weight=1)

# ------------------ CREACIÓN DE BOTONES ------------------#
carga = CTkButton(
    main_conf,
    text="Cargar Archivo",
    width=150,
    height=40,
    fg_color="blue",
    hover_color="gray",
    command=load_file,
)
carga.grid(row=0, column=0, padx=10, pady=20, sticky="ew")

fft = CTkButton(
    main_conf,
    text="Aplicar Transformada",
    width=150,
    height=40,
    fg_color="blue",
    hover_color="gray",
    command=apply_transform,
)
fft.grid(row=0, column=1, padx=10, pady=20, sticky="ew")

filtro = CTkButton(
    main_conf,
    text="Aplicar Filtro",
    width=150,
    height=40,
    fg_color="blue",
    hover_color="gray",
    command=configure_filter,
)
filtro.grid(row=0, column=2, padx=10, pady=20, sticky="ew")

borrar = CTkButton(
    main_conf,
    text="Borrar Archivo",
    width=150,
    height=40,
    fg_color="blue",
    hover_color="gray",
    command=delete_audio,
)
borrar.grid(row=0, column=3, padx=10, pady=20, sticky="ew")

main_conf.grid_columnconfigure((0, 1, 2, 3), weight=1)
main_conf.grid_rowconfigure(0, weight=1)

play_button = CTkButton(
    output_frame,
    text="Reproducir audio",
    width=150,
    height=40,
    fg_color="darkred",
    hover_color="gray",
    command=play_audio,
)
play_button.grid(row=0, column=0, padx=10, pady=20, sticky="ew")

play_filter_button = CTkButton(
    output_frame,
    text="Reproducir audio filtrado",
    width=150,
    height=40,
    fg_color="darkred",
    hover_color="gray",
    command=play_filtered_audio,
)
play_filter_button.grid(row=0, column=1, padx=10, pady=20, sticky="ew")

store = CTkButton(
    output_frame,
    text="Guardar archivo",
    width=150,
    height=40,
    fg_color="green",
    hover_color="gray",
    command=store_audio,
)
store.grid(row=0, column=2, padx=10, pady=20, sticky="ew")

output_frame.grid_columnconfigure((0, 1, 2), weight=1)
output_frame.grid_rowconfigure(0, weight=1)
output_frame.grid_rowconfigure(0, minsize=100)


app.mainloop()
