import tkinter as tk
from tkinter import filedialog
import pyaudio
import wave
import threading
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import noisereduce as nr  
from pydub import AudioSegment
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import librosa
import json
import scipy

arayüz = tk.Tk()
arayüz.title("Ses Analiz Uygulaması")
arayüz.geometry("800x650")
arayüz.resizable(False, False)
arayüz.config(bg="light slate gray")

kayıtlı_sesler_listesi = []
geçmiş_listesi = []
recording = False
audio = pyaudio.PyAudio()
json_dosyası = "ses_dosyalari.json"

def ses_dosyalarını_yaz():
    with open(json_dosyası, "w") as dosya:
        json.dump(kayıtlı_sesler_listesi, dosya)

def ses_dosyalarını_yükle():
    global kayıtlı_sesler_listesi
    if os.path.exists(json_dosyası):
        with open(json_dosyası, "r") as dosya:
            kayıtlı_sesler_listesi = json.load(dosya)
    else:
        kayıtlı_sesler_listesi = []

def pencere_ortala(pencere, genislik, yukseklik):
    ekran_genislik = pencere.winfo_screenwidth()
    ekran_yükseklik = pencere.winfo_screenheight()
    x_koordinat = int((ekran_genislik - genislik) / 2)
    y_koordinat = int((ekran_yükseklik - yukseklik) / 2)
    pencere.geometry(f"{genislik}x{yukseklik}+{x_koordinat}+{y_koordinat}")

def ses_kaydet():
    def kayit():
        global recording
        recording = True
        def kayit_islemi():
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            CHUNK = 1024
            
            WAVE_OUTPUT_FILENAME = f"recording_{int(time.time())}.wav"
            stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            frames = []
            while recording:
                data = stream.read(CHUNK)
                frames.append(data)
            stream.stop_stream()
            stream.close()
            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            kayıtlı_sesler_listesi.append(WAVE_OUTPUT_FILENAME)
            geçmiş_listesi.append(f"Kayıt eklendi: {WAVE_OUTPUT_FILENAME}")
            
        t = threading.Thread(target=kayit_islemi)
        t.start()

    def durdur():
        global recording
        recording = False
        kayit_penceresi.destroy()

    kayit_penceresi = tk.Toplevel()
    kayit_penceresi.title("Ses Kaydet")
    kayit_penceresi.config(bg="light steel blue")
    pencere_ortala(kayit_penceresi, 400, 200)  
    baslat_buton = tk.Button(kayit_penceresi, text="Kaydı Başlat", command=kayit, bg="light blue", fg="black", font="Times 15", width=15)
    baslat_buton.pack(pady=20)
    durdur_buton = tk.Button(kayit_penceresi, text="Kaydı Durdur", command=durdur, bg="light blue", fg="black", font="Times 15", width=15)
    durdur_buton.pack(pady=20)

def ses_yükle():
    def yükle():
        file_paths = filedialog.askopenfilenames(filetypes=[("WAV Files", "*.wav")])
        for file_path in file_paths:
            if os.path.exists(file_path):
                kayıtlı_sesler_listesi.append(file_path)
                geçmiş_listesi.append(f"Yüklenmiş: {file_path}")
        güncelle_listbox()
        
    def güncelle_listbox():
        yükleme_listbox.delete(0, tk.END)
        for ses in kayıtlı_sesler_listesi:
            yükleme_listbox.insert(tk.END, ses)

    yükleme_penceresi = tk.Toplevel()
    yükleme_penceresi.title("Ses Yükle")
    yükleme_penceresi.config(bg="light coral")
    pencere_ortala(yükleme_penceresi, 400, 300)

    yükleme_listbox = tk.Listbox(yükleme_penceresi)
    yükleme_listbox.pack(fill="both", expand=True)

    yükle_buton = tk.Button(yükleme_penceresi, text="Yükle", command=yükle, bg="indian red", fg="black", font="Times 15", width=15)
    yükle_buton.pack(pady=20)

def ses_sil():
    def sil():
        selected_indices = [i for i, var in enumerate(checkbox_vars) if var.get() == 1]
        for index in selected_indices:
            ses = kayıtlı_sesler_listesi[index]
            if os.path.exists(ses):
                os.remove(ses)
                geçmiş_listesi.append(f"Silindi: {ses}")
        global kayıtlı_sesler_listesi
        kayıtlı_sesler_listesi = [ses for i, ses in enumerate(kayıtlı_sesler_listesi) if i not in selected_indices]
        güncelle_checkbuttons()
        silme_penceresi.destroy()

    def güncelle_checkbuttons():
        for widget in silme_penceresi.winfo_children():
            widget.destroy()
        checkbox_vars.clear()
        for i, ses in enumerate(kayıtlı_sesler_listesi):
            var = tk.IntVar()
            checkbox_vars.append(var)
            chk = tk.Checkbutton(silme_penceresi, text=ses, variable=var, bg="light salmon")
            chk.pack(anchor='w')

    silme_penceresi = tk.Toplevel()
    silme_penceresi.title("Ses Sil")
    silme_penceresi.config(bg="light salmon")
    pencere_ortala(silme_penceresi, 600, 400)  

    checkbox_vars = []
    güncelle_checkbuttons()

    sil_buton = tk.Button(silme_penceresi, text="Sil", command=sil, bg="light pink", fg="black", font="Times 15", width=15)
    sil_buton.pack(pady=20)

def ses_dinle():
    def dinle():
        selected_indices = [i for i, var in enumerate(checkbox_vars) if var.get() == 1]
        for index in selected_indices:
            ses = kayıtlı_sesler_listesi[index]
            if os.path.exists(ses):
                wf = wave.open(ses, 'rb')
                stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
                data = wf.readframes(1024)
                while data:
                    stream.write(data)
                    data = wf.readframes(1024)
                stream.stop_stream()
                stream.close()
                wf.close()

    dinleme_penceresi = tk.Toplevel()
    dinleme_penceresi.title("Sesi Dinle")
    dinleme_penceresi.config(bg="light slate gray")
    pencere_ortala(dinleme_penceresi, 600, 400)  

    checkbox_vars = []
    for ses in kayıtlı_sesler_listesi:
        var = tk.IntVar()
        checkbox_vars.append(var)
        chk = tk.Checkbutton(dinleme_penceresi, text=ses, variable=var, bg="light slate gray")
        chk.pack(anchor='w')

    dinle_buton = tk.Button(dinleme_penceresi, text="Dinle", command=dinle, bg="light gray", fg="black", font="Times 15", width=15)
    dinle_buton.pack(pady=20)

def ses_bilgilerini_goster(parent_frame, ses):
    if os.path.exists(ses):
        audio = AudioSegment.from_file(ses, format="wav")
        ses_suresi = audio.duration_seconds

        ses_bilgileri = f"Adı: {os.path.basename(ses)}\nSüresi: {int(ses_suresi // 60)}:{int(ses_suresi % 60):02d} dakika"

        for widget in parent_frame.winfo_children():
            widget.destroy()

        bilgi_label = tk.Label(parent_frame, text=ses_bilgileri, bg="darkslateblue", fg="black")
        bilgi_label.pack(pady=10)

        mfccs = librosa.feature.mfcc(y=librosa.load(ses, sr=None)[0], sr=None)
        enerji = np.sum(mfccs, axis=1)

        plt.figure(figsize=(6, 4))
        plt.subplot(2, 1, 1)
        plt.title("MFCC Özellikleri")
        plt.plot(mfccs.T)
        plt.subplot(2, 1, 2)
        plt.title("Enerji")
        plt.plot(enerji)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(plt.gcf(), master=parent_frame)
        canvas.get_tk_widget().pack()
        canvas.draw()

def sesleri_goster():
    def goster():
        ses_bilgilerini_goster(bilgi_frame, kayıtlı_sesler_listesi[listbox.curselection()[0]])
        
    goster_penceresi = tk.Toplevel()
    goster_penceresi.title("Ses Bilgileri")
    goster_penceresi.config(bg="light gray")
    pencere_ortala(goster_penceresi, 400, 300)  

    listbox = tk.Listbox(goster_penceresi)
    listbox.pack(fill="both", expand=True)

    for ses in kayıtlı_sesler_listesi:
        listbox.insert(tk.END, ses)

    bilgi_frame = tk.Frame(goster_penceresi)
    bilgi_frame.pack(fill="both", expand=True)

    goster_buton = tk.Button(goster_penceresi, text="Göster", command=goster, bg="light green", fg="black", font="Times 15", width=15)
    goster_buton.pack(pady=20)

def ana_menü():
    ses_dosyalarını_yükle()
    
    butonlar_frame = tk.Frame(arayüz, bg="light slate gray")
    butonlar_frame.pack(pady=20)

    ses_kaydet_buton = tk.Button(butonlar_frame, text="Ses Kaydet", command=ses_kaydet, bg="light blue", fg="black", font="Times 15", width=15)
    ses_kaydet_buton.grid(row=0, column=0, padx=10)

    ses_yükle_buton = tk.Button(butonlar_frame, text="Ses Yükle", command=ses_yükle, bg="light blue", fg="black", font="Times 15", width=15)
    ses_yükle_buton.grid(row=0, column=1, padx=10)

    ses_sil_buton = tk.Button(butonlar_frame, text="Ses Sil", command=ses_sil, bg="light blue", fg="black", font="Times 15", width=15)
    ses_sil_buton.grid(row=0, column=2, padx=10)

    ses_dinle_buton = tk.Button(butonlar_frame, text="Sesi Dinle", command=ses_dinle, bg="light blue", fg="black", font="Times 15", width=15)
    ses_dinle_buton.grid(row=0, column=3, padx=10)

    ses_goster_buton = tk.Button(butonlar_frame, text="Ses Bilgilerini Göster", command=sesleri_goster, bg="light blue", fg="black", font="Times 15", width=15)
    ses_goster_buton.grid(row=0, column=4, padx=10)

    arayüz.mainloop()

ana_menü()
