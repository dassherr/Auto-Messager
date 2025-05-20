import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time
import random
import datetime
import pyautogui
import pyperclip
from pynput import keyboard
import winsound

# Dil desteği (Türkçe ve İngilizce)
langs = {
    "tr": {
        "title": "Auto Messager",
        "message_label": "Mesajlar (Her satır bir mesaj):",
        "min_wait": "Minimum Bekleme (sn):",
        "max_wait": "Maksimum Bekleme (sn):",
        "loops": "Döngü Sayısı (0 = sonsuz):",
        "start": "Başlat",
        "stop": "Durdur",
        "pause": "Duraklat",
        "resume": "Devam Et",
        "next_msg": "Sonraki Mesaj:",
        "waiting": "Başlamadan önce bekleniyor: {} sn",
        "stopped": "Durduruldu.",
        "paused": "Duraklatıldı.",
        "resumed": "Devam Edildi.",
        "invalid_input": "Lütfen tüm alanları doğru doldurunuz!",
        "made_by": "Made by dassher",
        "dc_dassher": "Dc : dassherlol"
    },
    "en": {
        "title": "Auto Messager",
        "message_label": "Messages (One per line):",
        "min_wait": "Minimum Wait (sec):",
        "max_wait": "Maximum Wait (sec):",
        "loops": "Loop Count (0 = infinite):",
        "start": "Start",
        "stop": "Stop",
        "pause": "Pause",
        "resume": "Resume",
        "next_msg": "Next Message:",
        "waiting": "Waiting before start: {} sec",
        "stopped": "Stopped.",
        "paused": "Paused.",
        "resumed": "Resumed.",
        "invalid_input": "Please fill all fields correctly!",
        "made_by": "Made by dassher",
        "dc_dassher": "Dc : dassherlol"
    }
}

class AutoMessagerApp:
    def __init__(self, root):
        self.root = root
        self.lang = "tr"  # Dil Türkçe, istersen değiştir
        
        self.running = False
        self.paused = False
        self.stop_flag = False
        
        self.messages = []
        self.min_wait = 1.0
        self.max_wait = 1.0
        self.loop_count = 0
        self.current_loop = 0
        self.current_msg_index = 0
        
        self.build_gui()
        self.setup_hotkeys()
        
    def build_gui(self):
        self.root.title(langs[self.lang]["title"])
        self.root.geometry("1150x600")
        self.root.configure(bg="#000000")
        self.root.resizable(False, False)
        
        # Neon kenarlıklı Frame
        self.main_frame = tk.Frame(self.root, bg="#000000", highlightthickness=4, highlightbackground="#8A2BE2")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", width=1140, height=590)
        
        # Mesaj label
        self.lbl_messages = tk.Label(self.main_frame, text=langs[self.lang]["message_label"], fg="white", bg="#000000", font=("Arial", 14))
        self.lbl_messages.pack(pady=(10, 0))
        
        # Mesaj Textarea (scrolled)
        self.txt_messages = scrolledtext.ScrolledText(self.main_frame, width=80, height=15, font=("Consolas", 12), bg="#111111", fg="white", insertbackground="white")
        self.txt_messages.pack(pady=5)
        
        # Bekleme süresi Frame
        wait_frame = tk.Frame(self.main_frame, bg="#000000")
        wait_frame.pack(pady=10)
        
        # Minimum bekleme
        tk.Label(wait_frame, text=langs[self.lang]["min_wait"], fg="white", bg="#000000", font=("Arial", 12)).grid(row=0, column=0, padx=10, sticky="w")
        self.entry_min_wait = tk.Entry(wait_frame, width=8, font=("Arial", 12), bg="#222222", fg="white", insertbackground="white")
        self.entry_min_wait.grid(row=0, column=1, padx=5)
        self.entry_min_wait.insert(0, "1")
        
        # Maksimum bekleme
        tk.Label(wait_frame, text=langs[self.lang]["max_wait"], fg="white", bg="#000000", font=("Arial", 12)).grid(row=0, column=2, padx=10, sticky="w")
        self.entry_max_wait = tk.Entry(wait_frame, width=8, font=("Arial", 12), bg="#222222", fg="white", insertbackground="white")
        self.entry_max_wait.grid(row=0, column=3, padx=5)
        self.entry_max_wait.insert(0, "3")
        
        # Döngü sayısı
        tk.Label(wait_frame, text=langs[self.lang]["loops"], fg="white", bg="#000000", font=("Arial", 12)).grid(row=0, column=4, padx=10, sticky="w")
        self.entry_loops = tk.Entry(wait_frame, width=8, font=("Arial", 12), bg="#222222", fg="white", insertbackground="white")
        self.entry_loops.grid(row=0, column=5, padx=5)
        self.entry_loops.insert(0, "0")
        
        # Butonlar Frame
        btn_frame = tk.Frame(self.main_frame, bg="#000000")
        btn_frame.pack(pady=10)
        
        self.btn_start = tk.Button(btn_frame, text=langs[self.lang]["start"], font=("Arial", 14, "bold"), bg="#8A2BE2", fg="white", width=12, command=self.start)
        self.btn_start.grid(row=0, column=0, padx=10)
        
        self.btn_stop = tk.Button(btn_frame, text=langs[self.lang]["stop"], font=("Arial", 14, "bold"), bg="#8A2BE2", fg="white", width=12, command=self.stop, state="disabled")
        self.btn_stop.grid(row=0, column=1, padx=10)
        
        self.btn_pause = tk.Button(btn_frame, text=langs[self.lang]["pause"], font=("Arial", 14, "bold"), bg="#8A2BE2", fg="white", width=12, command=self.pause_resume, state="disabled")
        self.btn_pause.grid(row=0, column=2, padx=10)
        
        # Durum ve sonraki mesaj label
        self.lbl_status = tk.Label(self.main_frame, text="", fg="white", bg="#000000", font=("Arial", 12))
        self.lbl_status.pack(pady=(10,0))
        
        self.lbl_next_msg = tk.Label(self.main_frame, text=langs[self.lang]["next_msg"], fg="white", bg="#000000", font=("Arial", 14, "bold"))
        self.lbl_next_msg.pack(pady=5)
        
        # Alt yazılar (made by, dc)
        self.lbl_made_by = tk.Label(self.root, text=langs[self.lang]["made_by"], fg="#8A2BE2", bg="#000000", font=("Arial", 10))
        self.lbl_made_by.place(relx=0.02, rely=0.96)
        
        self.lbl_dc = tk.Label(self.root, text=langs[self.lang]["dc_dassher"], fg="#8A2BE2", bg="#000000", font=("Arial", 10))
        self.lbl_dc.place(relx=0.88, rely=0.96)
    
    def validate_inputs(self):
        try:
            self.messages = [m.strip() for m in self.txt_messages.get("1.0", tk.END).splitlines() if m.strip()]
            if not self.messages:
                return False
            
            self.min_wait = float(self.entry_min_wait.get())
            self.max_wait = float(self.entry_max_wait.get())
            self.loop_count = int(self.entry_loops.get())
            
            if self.min_wait < 0 or self.max_wait < 0 or self.min_wait > self.max_wait or self.loop_count < 0:
                return False
            
            return True
        except Exception:
            return False
    
    def start(self):
        if not self.validate_inputs():
            messagebox.showerror(langs[self.lang]["title"], langs[self.lang]["invalid_input"])
            return
        
        if self.running:
            return
        
        self.running = True
        self.paused = False
        self.stop_flag = False
        self.current_loop = 0
        self.current_msg_index = 0
        
        self.update_ui_running(True)
        
        wait_before_start = 5  # Başlamadan önce bekleme süresi
        self.lbl_status.config(text=langs[self.lang]["waiting"].format(wait_before_start))
        self.root.update()
        
        # Başlamadan önce bekle
        def delayed_start():
            time.sleep(wait_before_start)
            if not self.stop_flag:
                self.lbl_status.config(text="")
                self.send_messages_loop()
        
        threading.Thread(target=delayed_start, daemon=True).start()
    
    def send_messages_loop(self):
        while self.running and not self.stop_flag:
            if self.paused:
                time.sleep(0.3)
                continue
            
            if self.loop_count != 0 and self.current_loop >= self.loop_count:
                self.stop()
                break
            
            msg = self.messages[self.current_msg_index]
            formatted_msg = self.format_message(msg)
            
            # Gönder (panoya kopyala + ctrl+v + enter)
            pyperclip.copy(formatted_msg)
            time.sleep(0.2)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.1)
            pyautogui.press("enter")
            
            # Sonraki mesaj
            self.current_msg_index += 1
            if self.current_msg_index >= len(self.messages):
                self.current_msg_index = 0
                self.current_loop += 1
            
            self.lbl_next_msg.config(text=langs[self.lang]["next_msg"] + " " + self.get_current_message_preview())
            
            wait_time = random.uniform(self.min_wait, self.max_wait)
            for _ in range(int(wait_time * 10)):
                if self.stop_flag or self.paused:
                    break
                time.sleep(0.1)
        
        self.running = False
        self.update_ui_running(False)
        self.lbl_next_msg.config(text=langs[self.lang]["stopped"])
        self.play_sound("stop")
    
    def get_current_message_preview(self):
        if self.messages and 0 <= self.current_msg_index < len(self.messages):
            preview = self.messages[self.current_msg_index]
            if len(preview) > 30:
                preview = preview[:27] + "..."
            return preview
        return ""
    
    def format_message(self, msg):
        now = datetime.datetime.now()
        msg = msg.replace("{date}", now.strftime("%Y-%m-%d"))
        msg = msg.replace("{time}", now.strftime("%H:%M:%S"))
        msg = msg.replace("{datetime}", now.strftime("%Y-%m-%d %H:%M:%S"))
        return msg
    
    def stop(self):
        if not self.running:
            return
        self.stop_flag = True
        self.running = False
        self.paused = False
        self.update_ui_running(False)
        self.lbl_status.config(text=langs[self.lang]["stopped"])
        self.play_sound("stop")
    
    def pause_resume(self):
        if not self.running:
            return
        self.paused = not self.paused
        if self.paused:
            self.lbl_status.config(text=langs[self.lang]["paused"])
            self.btn_pause.config(text=langs[self.lang]["resume"])
            self.play_sound("pause")
        else:
            self.lbl_status.config(text=langs[self.lang]["resumed"])
            self.btn_pause.config(text=langs[self.lang]["pause"])
            self.play_sound("resume")
    
    def update_ui_running(self, running):
        if running:
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
            self.btn_pause.config(state="normal")
        else:
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.btn_pause.config(state="disabled")
            self.btn_pause.config(text=langs[self.lang]["pause"])
    
    def play_sound(self, event):
        # Basit sesler
        if event == "start":
            winsound.MessageBeep(winsound.MB_OK)
        elif event == "stop":
            winsound.MessageBeep(winsound.MB_ICONHAND)
        elif event == "pause":
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        elif event == "resume":
            winsound.MessageBeep(winsound.MB_OK)
    
    def setup_hotkeys(self):
        def on_press(key):
            try:
                if key == keyboard.Key.esc:
                    if self.running:
                        self.stop()
                elif key == keyboard.Key.pause:
                    if self.running:
                        self.pause_resume()
            except Exception:
                pass
        
        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoMessagerApp(root)
    root.mainloop()
