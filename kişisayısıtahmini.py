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
import pyodbc
from datetime import datetime
import json
from tkinter import ttk
import scipy.signal
from sklearn.mixture import GaussianMixture

arayüz = tk.Tk()
arayüz.title("Ses Analiz Uygulaması")
arayüz.geometry("800x650")
arayüz.resizable(False, False)
arayüz.config(bg="light slate gray")

kayıtlı_sesler_listesi = []
silinen_sesler_listesi = []
geçmiş_listesi = []

recording = False
audio = pyaudio.PyAudio()

json_dosyası = "ses_dosyalari.json"
silinen_sesler_dosyası = "silinen_sesler.json"

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

def silinen_sesler_dosyalarını_yaz():
    with open(silinen_sesler_dosyası, "w") as dosya:
        json.dump(silinen_sesler_listesi, dosya)

def silinen_sesler_dosyalarını_yükle():
    global silinen_sesler_listesi
    if os.path.exists(silinen_sesler_dosyası):
        with open(silinen_sesler_dosyası, "r") as dosya:
            silinen_sesler_listesi = json.load(dosya)
    else:
        silinen_sesler_listesi = []

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

            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
            frames = []
            start_time = time.time()
            while recording:
                data = stream.read(CHUNK)
                frames.append(data)
                kayit_penceresi.update_idletasks()
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
    durdur_buton = tk.Button(kayit_penceresi, text="Kaydı Durdur",command=durdur, bg="light blue", fg="black", font="Times 15", width=15)
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
        güncelle_kayıtlı_sesler_listesi(selected_indices)
        güncelle_checkbuttons()
        silme_penceresi.destroy()

    def güncelle_kayıtlı_sesler_listesi(indices):
        global kayıtlı_sesler_listesi
        for index in indices:
            ses = kayıtlı_sesler_listesi[index]
            if os.path.exists(ses):
                os.remove(ses)
                geçmiş_listesi.append(f"Silindi: {ses}")
        kayıtlı_sesler_listesi = [ses for i, ses in enumerate(kayıtlı_sesler_listesi) if i not in indices]

    def güncelle_checkbuttons():
        for widget in silme_penceresi.winfo_children():
            widget.destroy()
        checkbox_vars.clear()  # Var olan checkboxları temizler
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
                stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                                    channels=wf.getnchannels(),
                                    rate=wf.getframerate(),
                                    output=True)
                data = wf.readframes(1024)
                while data:
                    stream.write(data)
                    data = wf.readframes(1024)
                stream.stop_stream()
                stream.close()
                wf.close()
            else:
                print(f"File not found: {ses}")

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

    dinle_buton = tk.Button(dinleme_penceresi, text="Dinle",command=dinle, bg="light gray", fg="black", font="Times 15", width=15)
    dinle_buton.pack(pady=20)

def gürültü_azaltma(y, sr):
    # Yüksek geçiş filtresi ile düşük frekanstaki gürültüyü azaltma
    b, a = scipy.signal.butter(1, 1000/(sr/2), btype='highpass')
    filtered_y = scipy.signal.lfilter(b, a, y)
    return filtered_y
    
def kisi_sayisi_tahmin_et(ses_dosyasi):
    y, sr = librosa.load(ses_dosyasi)

    # MFCC (Mel Frequency Cepstral Coefficients) 
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    segment_count = mfccs.shape[1] // 100
    farklılık_skoru = 0

    for i in range(segment_count - 1):
        mfcc_diff = np.mean(np.abs(mfccs[:, i * 100:(i + 1) * 100] - mfccs[:, (i + 1) * 100:(i + 2) * 100]))
        farklılık_skoru += mfcc_diff

    farklılık_skoru /= segment_count

    # Farklılık skorunu kişi sayısına çevirme
    if farklılık_skoru < 10:
        return 1  # Tahmini bir kişi
    elif farklılık_skoru > 10 and farklılık_skoru < 20:
        return 2  # Tahmini iki kişi
    elif farklılık_skoru > 20 and farklılık_skoru < 30:
        return 3  # Tahmini üç kişi
    elif farklılık_skoru > 30 and farklılık_skoru < 40:
        return 4  # Tahmini dört kişi
    else:
        return 5  # Beş veya daha fazla kişi olabilir
    
def kişi_sayısı_tahmin():
    tahmin_penceresi = tk.Toplevel()
    tahmin_penceresi.title("Kişi Sayısı Tahmini")
    tahmin_penceresi.config(bg="lightblue")
    pencere_ortala(tahmin_penceresi, 400, 300)  

    tahmin_listbox = tk.Listbox(tahmin_penceresi, selectmode=tk.SINGLE)
    tahmin_listbox.pack(fill="both", expand=True)

    for ses in kayıtlı_sesler_listesi:
        tahmin_listbox.insert(tk.END, ses)

    def tahmin_et():
        selected_indices = tahmin_listbox.curselection()
        if selected_indices:
            ses = tahmin_listbox.get(selected_indices[0])
            tahmini_kisi_sayisi = kisi_sayisi_tahmin_et(ses)
            tahmin_sonuclari_label.config(text=f"Tahmini Kişi Sayısı: {tahmini_kisi_sayisi}")

    tahmin_buton = tk.Button(tahmin_penceresi, text="Tahmin Et", command=tahmin_et, bg="lightgray", fg="black", font="Times 15")
    tahmin_buton.pack(pady=20)

    tahmin_sonuclari_label = tk.Label(tahmin_penceresi, text="", bg="lightblue", fg="black")
    tahmin_sonuclari_label.pack(pady=20)
  
def ses_bilgilerini_goster(parent_frame, ses):
    if os.path.exists(ses):
        audio = AudioSegment.from_file(ses, format="wav")
        ses_suresi = audio.duration_seconds

        ses_bilgileri = f"Adı: {os.path.basename(ses)}\nSüresi: {int(ses_suresi // 60)}:{int(ses_suresi % 60):02d} dakika"

        for widget in parent_frame.winfo_children():
            widget.destroy()

        bilgi_label = tk.Label(parent_frame, text=ses_bilgileri, bg="darkslateblue", fg="black")
        bilgi_label.pack(pady=10)

        ses_goruntule_ve_oynat(ses, parent_frame)

def ses_goruntule_ve_oynat(ses, parent_frame):
    if os.path.exists(ses):
        # Yeni bir pencere oluştur
        spektrum_penceresi = tk.Toplevel()
        spektrum_penceresi.title("Ses Dalga Formu")
        spektrum_penceresi.config(bg="indian red")
        pencere_ortala(spektrum_penceresi, 600, 400)

        audio_segment = AudioSegment.from_file(ses, format="wav")
        samples = np.array(audio_segment.get_array_of_samples())
        if audio_segment.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(samples)
        ax.set_title(f'Ses Dalga Formu: {os.path.basename(ses)}')
        ax.set_xlabel('Örnek Numarası')
        ax.set_ylabel('Genlik')

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=spektrum_penceresi)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        canvas.draw()

        def oynat():
            if os.path.exists(ses):
                wf = wave.open(ses, 'rb')
                stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                                    channels=wf.getnchannels(),
                                    rate=wf.getframerate(),
                                    output=True)
                data = wf.readframes(1024)
                while data:
                    stream.write(data)
                    data = wf.readframes(1024)
                stream.stop_stream()
                stream.close()
                wf.close()
        def spektrum_kapat():
            spektrum_penceresi.destroy()

        spektrum_penceresi.protocol("WM_DELETE_WINDOW", spektrum_kapat)

def kayitli_sesler():
    kayitli_penceresi = tk.Toplevel()
    kayitli_penceresi.title("Ses Dalga Formu")
    kayitli_penceresi.config(bg="indian red")
    pencere_ortala(kayitli_penceresi, 800, 600)

    analiz_bilgi = tk.Label(kayitli_penceresi, text="KAYITLI SES BİLGİLERİ", font="Times 20", bg="indian red")
    analiz_bilgi.pack(pady=20)

    kayıt_listbox = tk.Listbox(kayitli_penceresi)
    kayıt_listbox.pack(fill="both", expand=True)

    for ses in kayıtlı_sesler_listesi:
        kayıt_listbox.insert(tk.END, ses)
        
    def ses_sec_ve_goster():
        selected_ses = kayıt_listbox.get(tk.ACTIVE)
        if selected_ses:
            ses_bilgilerini_goster(bilgi_frame, selected_ses)

    bilgi_frame = tk.Frame(kayitli_penceresi, bg="indian red")
    bilgi_frame.pack(fill="both", expand=True)

    ses_sec_buton = tk.Button(kayitli_penceresi, text="Ses Spektrum Göster", command=ses_sec_ve_goster, bg="dark salmon", fg="black", font="Times 14")
    ses_sec_buton.pack(pady=10)
  
def kayit_gecmisi():
    gecmis_penceresi = tk.Toplevel()
    gecmis_penceresi.title("Kayıt Geçmişi")
    gecmis_penceresi.config(bg="sienna")
    pencere_ortala(gecmis_penceresi, 300, 200)

    geçmiş_listbox = tk.Listbox(gecmis_penceresi)
    geçmiş_listbox.pack(fill="both", expand=True)

    for entry in geçmiş_listesi:
        geçmiş_listbox.insert(tk.END, entry)
    
def tüm_sesleri_göster():
    tüm_sesler_penceresi = tk.Toplevel()
    tüm_sesler_penceresi.title("Tüm Sesler")
    tüm_sesler_penceresi.config(bg="light blue")
    pencere_ortala(tüm_sesler_penceresi, 600, 400)

    # Tabloyu pencerede yerleştirmek için bir çerçeve oluşturun
    tree_frame = tk.Frame(tüm_sesler_penceresi)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Scrollbar ekleyin
    tree_scroll = tk.Scrollbar(tree_frame)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set)
    tree.pack(fill=tk.BOTH, expand=True)

    tree_scroll.config(command=tree.yview)

    # Sütun ayarları
    tree["columns"] = ("Ses Adı", "Süresi")

    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("Ses Adı", anchor=tk.W, width=300, minwidth=200)
    tree.column("Süresi", anchor=tk.W, width=100, minwidth=100)

    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("Ses Adı", text="Ses Adı", anchor=tk.W)
    tree.heading("Süresi", text="Süresi", anchor=tk.W)

    # Renkli satırlar için stil uygulayın
    style = ttk.Style()
    style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
    style.map('Treeview', background=[('selected', 'green')])

    # Alternatif satır renkleri ekleyin
    tree.tag_configure('oddrow', background="lightblue")
    tree.tag_configure('evenrow', background="white")

    for index, ses in enumerate(kayıtlı_sesler_listesi):
        audio = AudioSegment.from_file(ses, format="wav")
        ses_suresi = audio.duration_seconds
        tag = 'oddrow' if index % 2 == 0 else 'evenrow'
        tree.insert("", tk.END, values=(os.path.basename(ses), f"{int(ses_suresi // 60)}:{int(ses_suresi % 60):02d}"), tags=(tag,))

    # Pencereyi ekranın ortasında açmak için
    pencere_ortala(tüm_sesler_penceresi, 800, 500)

ikon = tk.PhotoImage(file="icon/ikon.png")
baslık_label= tk.Label(arayüz, image=ikon, text="SES ANALİZİ İLE KİŞİ SAYISI TAHMİNİ", fg='black', bg='light slate gray', font="Times 25",compound=tk.LEFT)
baslık_label.pack(pady=10)

ikon2= tk.PhotoImage(file="")
ses_kaydet_buton = tk.Button(arayüz, text="Ses Kaydet", command=ses_kaydet, bg="steel blue", fg="black", font="Times 15", width=20 )
ses_kaydet_buton.pack(pady=10)

ikon3= tk.PhotoImage(file="")
ses_yükle_buton = tk.Button(arayüz, text="Ses Yükle", command=ses_yükle, bg="coral", fg="black", font="Times 15", width=20)
ses_yükle_buton.pack(pady=10)

ikon4= tk.PhotoImage(file="")
ses_dinle_buton = tk.Button(arayüz, text="Ses Dinle", command=ses_dinle, bg="slate gray", fg="black", font="Times 15", width=20)
ses_dinle_buton.pack(pady=10)

ikon5= tk.PhotoImage(file="")
ses_sil_buton = tk.Button(arayüz, text="Ses Sil", command=ses_sil, bg="salmon", fg="black", font="Times 15", width=20)
ses_sil_buton.pack(pady=10)

ikon8 = tk.PhotoImage(file="")
tüm_sesler_buton = tk.Button(arayüz, text="Tüm Sesleri Göster", command=tüm_sesleri_göster, bg="light blue", fg="black", font="Times 15", width=20)
tüm_sesler_buton.pack(pady=10)

ikon9= tk.PhotoImage(file="")
kayitli_buton = tk.Button(arayüz, text="Ses Dalga Formu", command=kayitli_sesler, bg="rosy brown", fg="black", font="Times 15", width=20)
kayitli_buton.pack(pady=10)

ikon10= tk.PhotoImage(file="")
kişi_sayısı_buton = tk.Button(arayüz, text="Kişi Sayısı Tahmini", command=kişi_sayısı_tahmin, bg="gray45", fg="black", font="Times 15",width=20)
kişi_sayısı_buton.pack(pady=10)

ikon11= tk.PhotoImage(file="")
geçmiş_buton = tk.Button(arayüz, text="Kayıt Geçmişi", command=kayit_gecmisi, bg="sienna", fg="black", font="Times 15", width=20)
geçmiş_buton.pack(pady=10)

arayüz.mainloop()