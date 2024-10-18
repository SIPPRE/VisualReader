import os
import re
import tkinter as tk
import threading
import PyPDF2
from tkinter import messagebox, Text, filedialog, StringVar, Scrollbar
from tkinter import ttk
from google.cloud import texttospeech, vision
from PIL import Image, ImageEnhance
from transformers import BlipProcessor, BlipForConditionalGeneration
from googletrans import Translator
from tkinter import PhotoImage
from pygame import mixer 
import time

# Ορισμός της διαδρομής για το Google Cloud credentials JSON αρχείο
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'Project Audio/project_audio.json' #use your own json file from google

# Dictionary υποστηριζόμενων γλωσσών και φωνών Neural2
VOICES = {
    "en-US": {
        "Male": "en-US-Neural2-D",
        "Female": "en-US-Neural2-F"
    },
    "el-GR": {
        "Female": "el-GR-Standard-A"  # Μόνο γυναικεία φωνή διαθέσιμη για τα Ελληνικά
    },
    "de-DE": {
        "Male": "de-DE-Neural2-B",
        "Female": "de-DE-Neural2-A"
    },
    "es-ES": {
        "Male": "es-ES-Neural2-B",
        "Female": "es-ES-Neural2-A"
    },
    "fr-FR": {
        "Male": "fr-FR-Neural2-B",
        "Female": "fr-FR-Neural2-A"
    }
}

LANGUAGES = {
    "Αγγλικά": "en-US",
    "Ελληνικά": "el-GR",
    "Γαλλικά": "fr-FR",
    "Γερμανικά": "de-DE",
    "Ισπανικά": "es-ES"
}

# Προετοιμασία του μοντέλου για περιγραφή εικόνας
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
translator = Translator()

# Δημιουργία main παραθύρου
window = tk.Tk()
window.geometry("700x700")
window.title("Speakify")
window.configure(bg='#F8F8F8')

# Ορισμός εικονιδίου
icon = PhotoImage(file="C:/Users/USER/Desktop/project/Project Audio/onoma.png")
window.iconphoto(False, icon)

# Ορισμός της μεταβλητής gender_var
gender_var = StringVar(value="Female")

# Ενεργοποίηση/Απενεργοποίηση του "Male" όταν επιλέγω Ελληνικά και αυτόματη εμφάνιση ρυθμίσεων
def on_language_change(event=None):
    selected_language = language_combobox.get()
    if selected_language == "Ελληνικά":
        messagebox.showinfo("Προειδοποίηση!", "Η ανδρική φωνή δεν είναι διαθέσιμη για τα Ελληνικά. Θα χρησιμοποιηθεί η γυναικεία φωνή.")
        gender_var.set("Γυναικεία")
        show_settings()  # Αυτόματη εμφάνιση του παραθύρου ρυθμίσεων όταν επιλέγονται τα Ελληνικά
    else:
        gender_var.set("Γυναικεία")

# Resize εικόνας για βελτιστοποίηση
def resize_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image = image.resize((256, 256))  # Μειώνουμε το μέγεθος της εικόνας για ταχύτερη επεξεργασία
    return image

# Περιγραφή εικόνας μέσω AI και μετάφραση (εκτέλεση σε νήμα)
def describe_image(image_path):
    try:
        # Ξεκινάμε τη μέτρηση του χρόνου
        start_time = time.time()

        image = resize_image(image_path)
        inputs = processor(image, return_tensors="pt")
        out = model.generate(**inputs, max_length=50, num_beams=15)
        description = processor.decode(out[0], skip_special_tokens=True)

        # Τέλος μέτρησης χρόνου
        end_time = time.time()
        recognition_time = end_time - start_time

        print(f"Χρόνος αναγνώρισης και περιγραφής εικόνας: {recognition_time} δευτερόλεπτα")

        # Μετάφραση της περιγραφής στα Ελληνικά
        translated_description = translator.translate(description, dest='el').text
        text_entry.delete("1.0", tk.END)
        text_entry.insert(tk.END, translated_description)
    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Ένα σφάλμα προέκυψε: {str(e)}")

# Εκτέλεση της περιγραφής σε ξεχωριστό νήμα για να μην "παγώνει" το GUI
def start_description_thread(image_path):
    threading.Thread(target=describe_image, args=(image_path,)).start()

# Άνοιγμα αρχείου εικόνας και περιγραφή
def open_image_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if file_path:
        start_description_thread(file_path)

# Καθαρισμός του Text Box
def clear_text():
    text_entry.delete("1.0", tk.END)

# Άνοιγμα αρχείου κειμένου (TXT)
def open_text_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()

            # Καθαρισμός του Text Box και εισαγωγή του κειμένου
            text_entry.delete("1.0", tk.END)
            text_entry.insert(tk.END, text_content)

# EPUB
def open_epub_file():
    messagebox.showinfo("Έρχεται σύντομα!", "Η δυνατότητα ανάγνωσης αρχείων EPUB για άτομα με μειωμένη ή προβληματική όραση θα προστεθεί σύντομα!")

# Άνοιγμα PDF
def open_pdf_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    try:
        pdf_file = open(file_path, 'rb')
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        pdf_text = ""

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_text += page.extract_text()

        pdf_file.close()

        # Καθαρισμός του Text Box και εισαγωγή του κειμένου
        text_entry.delete("1.0", tk.END)
        text_entry.insert(tk.END, pdf_text)

    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Ένα σφάλμα προέκυψε κατά την ανάγνωση του PDF αρχείου: {str(e)}")

# Ρυθμίσεις
def show_settings():
    global settings_window  # Δηλώνουμε την settings_window ως global για να τη χρησιμοποιήσουμε σε όλη τη συνάρτηση

    # Έλεγχος αν υπάρχει ήδη ανοιχτό παράθυρο ρυθμίσεων
    if 'settings_window' in globals() and settings_window.winfo_exists():
        settings_window.deiconify()  # Επαναφορά του παραθύρου (αν είναι κρυμμένο)
        settings_window.lift()  # Το φερνω μπροστά
        return
    
    # Ελεγχος αν υπάρχει κείμενο για μετατροπή
    text_input = text_entry.get("1.0", tk.END).strip()
    if not text_input:
        messagebox.showwarning("Προειδοποίηση!", "Παρακαλώ εισάγετε κείμενο για μετατροπή.")
        return

    # Δημιουργία παραθύρου ρυθμίσεων
    settings_window = tk.Toplevel(window)
    settings_window.title("Ρυθμίσεις Παραμέτρων")
    settings_window.geometry("400x350")
    settings_window.configure(bg='#F0F0F0')

    # Ετικέτες και κουμπιά για φύλο, ταχύτητα, τόνο και ένταση
    gender_label = tk.Label(settings_window, text="Φύλο:", bg="#F0F0F0")
    gender_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    gender_male = tk.Radiobutton(settings_window, text="Άνδρας", variable=gender_var, value="Male", bg="#F0F0F0")
    gender_female = tk.Radiobutton(settings_window, text="Γυναίκα", variable=gender_var, value="Female", bg="#F0F0F0")
    gender_male.grid(row=1, column=0, padx=20, sticky="w")
    gender_female.grid(row=1, column=1, padx=20, sticky="w")

    # Έλεγχος αν η γλώσσα είναι ελληνικά για να απενεργοποιηθεί η επιλογή του "Male"
    if language_combobox.get() == "Ελληνικά":
        gender_male.config(state="disabled")
        gender_female.select()

    # Ρυθμίσεις ταχύτητας, τόνου και έντασης
    speed_label = tk.Label(settings_window, text="Ταχύτητα:", bg="#F0F0F0")
    speed_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
    speed_scale = tk.Scale(settings_window, from_=0.25, to=2.0, orient='horizontal', bg="#F0F0F0")
    speed_scale.set(1.0)
    speed_scale.grid(row=2, column=1, padx=20, pady=5, sticky="w")

    pitch_label = tk.Label(settings_window, text="Τόνος:", bg="#F0F0F0")
    pitch_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
    pitch_scale = tk.Scale(settings_window, from_=-10.0, to=10.0, orient='horizontal', bg="#F0F0F0")
    pitch_scale.set(0.0)
    pitch_scale.grid(row=3, column=1, padx=20, pady=5, sticky="w")

    volume_label = tk.Label(settings_window, text="Ένταση:", bg="#F0F0F0")
    volume_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
    volume_scale = tk.Scale(settings_window, from_=-96.0, to=16.0, orient='horizontal', bg="#F0F0F0")
    volume_scale.set(0.0)
    volume_scale.grid(row=4, column=1, padx=20, pady=5, sticky="w")

    # Κουμπί εφαρμογής των ρυθμίσεων
    apply_button = tk.Button(settings_window, text="Μετατροπή",
                             command=lambda: apply_settings_convert(speed_scale.get(), pitch_scale.get(), volume_scale.get(), gender_var.get(), settings_window),
                             bg="#4CAF50", fg="white")
    apply_button.grid(row=5, column=0, columnspan=2, pady=20)

    # Κουμπί εφαρμογής των ρυθμίσεων
    apply_button = tk.Button(settings_window, text="Μετατροπή",
                             command=lambda: apply_settings_convert(speed_scale.get(), pitch_scale.get(), volume_scale.get(), gender_var.get(), settings_window),
                             bg="#4CAF50", fg="white")
    apply_button.grid(row=5, column=0, columnspan=2, pady=20)

    show_settings.window_opened = True  # Ορισμός σημαίας ότι το παράθυρο είναι ανοιχτό

# Εφαρμογή των ρυθμίσεων
def apply_settings_convert(speed, pitch, volume, gender, settings_window):
    try:
        text_input = text_entry.get("1.0", tk.END).strip()
        if not text_input:
            messagebox.showwarning("Προειδοποίηση!", "Παρακαλώ εισάγεται κείμενο για μετατροπή.")
            return

        start_time = time.time()
        
        language_code = LANGUAGES.get(language_combobox.get(), "en-US")
        voice_name = VOICES.get(language_code, {}).get(gender, "en-US-Neural2-F")

        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text_input)
        voice = texttospeech.VoiceSelectionParams(language_code=language_code, name=voice_name)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=speed, pitch=pitch, volume_gain_db=volume)
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        end_time = time.time()
        conversion_time = end_time - start_time
        print(f"Χρόνος μετατροπής κειμένου σε ομιλία: {conversion_time} δευτερόλεπτα")

        with open("output.mp3", "wb") as out:
            out.write(response.audio_content)
            messagebox.showinfo("Επιτυχής!", "Ο ήχος αποθηκεύτηκε επιτυχώς.")
            
            # Ενεργοποίηση των κουμπιών αναπαραγωγής
            play_button.config(state="normal")
            pause_button.config(state="normal")
            resume_button.config(state="normal")
            reset_button.config(state="normal")

        settings_window.destroy()  # Κλείσιμο του παραθύρου ρυθμίσεων

    except Exception as e:
        messagebox.showerror("Σφάλμα", str(e))

# Λειτουργία Play Audio
def play_audio():
    try:
        mixer.init()
        mixer.music.load("output.mp3")
        mixer.music.play()
    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την αναπαραγωγή: {str(e)}")

# Λειτουργία Pause Audio
def pause_audio():
    try:
        mixer.music.pause()
    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την παύση: {str(e)}")

# Λειτουργία Resume Audio
def resume_audio():
    try:
        mixer.music.unpause()
    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Σφάλμα κατά τη συνέχιση: {str(e)}")

# Λειτουργία Reset
def reset_application():
    try:
        # Σταμάτημα της μουσικής και εκκαθάριση των πεδίων
        if mixer.get_init():  # Ελέγχουμε αν το mixer έχει αρχικοποιηθεί
            mixer.music.stop()
            mixer.quit()  # Απενεργοποιούμε το mixer για να απελευθερώσουμε το αρχείο

        if os.path.exists("output.mp3"):  # Αν υπάρχει το αρχείο, το διαγράφουμε
            os.remove("output.mp3")

        # Επαναφορά των ρυθμίσεων και εκκαθάριση του κειμένου
        text_entry.delete("1.0", tk.END)
        language_combobox.set("Αγγλικά")
        gender_var.set("Γυναικεία")

        # Απενεργοποίηση κουμπιών μέχρι να παραχθεί νέος ήχος
        play_button.config(state="disabled")
        pause_button.config(state="disabled")
        resume_button.config(state="disabled")
        reset_button.config(state="disabled")

        messagebox.showinfo("Επαναφορά ολοκληρώθηκε!", "Η εφαρμογή επανήλθε στις αρχικές ρυθμίσεις.")
    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Σφάλμα κατά το reset: {str(e)}")
        
# context menu
def show_context_menu(event):
    context_menu.tk_popup(event.x_root, event.y_root)

# Δημιουργία context menu (Cut, Copy, Paste)
context_menu = tk.Menu(window, tearoff=0)
context_menu.add_command(label="Αποκοπή", command=lambda: text_entry.event_generate("<<Cut>>"))
context_menu.add_command(label="Αντιγραφή", command=lambda: text_entry.event_generate("<<Copy>>"))
context_menu.add_command(label="Επικόλληση", command=lambda: text_entry.event_generate("<<Paste>>"))

# Text input label και Text box
text_label = tk.Label(window, text="Κείμενο:", bg="#F8F8F8", font=('Helvetica', 12))
text_label.grid(row=0, column=0, padx=10, pady=(5, 10), sticky="w")
text_entry = Text(window, wrap="word", width=60, height=10, bg='white', fg='black', insertbackground='black', font=('Helvetica', 10))
text_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Προσθήκη context menu για δεξί κλικ
text_entry.bind("<Button-3>", show_context_menu)

# Scrollbar
scrollbar = Scrollbar(window, command=text_entry.yview)
scrollbar.grid(row=1, column=2, sticky='ns')
text_entry.config(yscrollcommand=scrollbar.set)

# Language selection combobox
language_label = tk.Label(window, text="Γλώσσα:", bg="#F8F8F8", font=('Helvetica', 12))
language_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
language_combobox = ttk.Combobox(window, values=list(LANGUAGES.keys()), state="readonly", font=('Helvetica', 10))
language_combobox.grid(row=2, column=1, padx=10, pady=10)
language_combobox.set("Αγγλικά")

# Όταν αλλάζει η γλώσσα, καλείται η συνάρτηση on_language_change
language_combobox.bind("<<ComboboxSelected>>", on_language_change)

# Frame για τα κουμπιά
button_frame = tk.Frame(window, bg="#F8F8F8")
button_frame.grid(row=4, column=0, columnspan=2, pady=10)

# Buttons for various functions
button_clear = tk.Button(button_frame, text='Καθαρισμός κειμένου', command=clear_text, bg="#4CAF50", fg="white", font=('Helvetica', 10, 'bold'))
button_clear.grid(row=0, column=0, padx=10, pady=5)

button_convert = tk.Button(button_frame, text='Μετατροπή κειμένου σε ομιλία', command=show_settings, bg="#4CAF50", fg="white", font=('Helvetica', 10, 'bold'))
button_convert.grid(row=0, column=1, padx=10, pady=5)

button_open_txt = tk.Button(button_frame, text='Άνοιγμα TXT File', command=open_text_file, bg="#4CAF50", fg="white", font=('Helvetica', 10, 'bold'))
button_open_txt.grid(row=1, column=0, padx=10, pady=5)

button_open_epub = tk.Button(button_frame, text='Άνοιγμα EPUB File', command=open_epub_file, bg="#4CAF50", fg="white", font=('Helvetica', 10, 'bold'))
button_open_epub.grid(row=1, column=1, padx=10, pady=5)

button_open_image = tk.Button(button_frame, text='Άνοιγμα Image File', command=open_image_file, bg="#4CAF50", fg="white", font=('Helvetica', 10, 'bold'))
button_open_image.grid(row=2, column=0, padx=10, pady=5)

button_open_pdf = tk.Button(button_frame, text='Άνοιγμα PDF File', command=open_pdf_file, bg="#4CAF50", fg="white", font=('Helvetica', 10, 'bold'))
button_open_pdf.grid(row=2, column=1, padx=10, pady=5)

# Προσθήκη κουμπιών αναπαραγωγής ήχου
audio_frame = tk.Frame(window, bg="#F8F8F8")
audio_frame.grid(row=5, column=0, columnspan=2, pady=10)

play_button = tk.Button(audio_frame, text='Αναπαραγωγή ήχου', command=play_audio, bg="#4CAF50", fg="white", font=('Helvetica', 10, 'bold'), state="disabled")
play_button.grid(row=0, column=0, padx=10, pady=5)

pause_button = tk.Button(audio_frame, text='Παύση ήχου', command=pause_audio, bg="#FFA500", fg="white", font=('Helvetica', 10, 'bold'), state="disabled")
pause_button.grid(row=0, column=1, padx=10, pady=5)

resume_button = tk.Button(audio_frame, text='Συνέχιση ήχου', command=resume_audio, bg="#008CBA", fg="white", font=('Helvetica', 10, 'bold'), state="disabled")
resume_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

reset_button = tk.Button(window, text="Επαναφορά", command=reset_application, bg="red", fg="white", font=('Helvetica', 10, 'bold'), state="disabled")
reset_button.grid(row=6, column=0, columnspan=2, pady=10)

# Εκκίνηση του GUI event loop
window.mainloop()
