#!/usr/bin/env python3
import socketio
import threading
import os
import sys
import datetime
import json

# ===== UBAH INI SESUAI NGROK URL KAMU =====
SERVER_URL = "https://prejuvenile-trickly-jacqui.ngrok-free.dev"
# ==========================================

CONFIG_FILE = "chat_config.json"

class ChatClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=10, reconnection_delay=1)
        self.nickname = ""
        self.connected = False
        
        # Setup event handlers
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('message', self.on_message)
        self.sio.on('server_message', self.on_server_message)
        self.sio.on('error', self.on_error)
    
    def load_config(self):
        """Load username dari file config"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get('nickname', '')
        except Exception as e:
            print(f"[WARNING] Error loading config: {e}")
        return ''
    
    def save_config(self):
        """Simpan username ke file config"""
        try:
            config = {'nickname': self.nickname}
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"[WARNING] Error saving config: {e}")
    
    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_banner(self):
        banner = """ /$$   /$$                                /$$$$$$  /$$                   /$$    
| $$$ | $$                               /$$__  $$| $$                  | $$    
| $$$$| $$ /$$   /$$  /$$$$$$$  /$$$$$$ | $$  \__/| $$$$$$$   /$$$$$$  /$$$$$$  
| $$ $$ $$| $$  | $$ /$$_____/ |____  $$| $$      | $$__  $$ |____  $$|_  $$_/  
| $$  $$$$| $$  | $$|  $$$$$$   /$$$$$$$| $$      | $$  \ $$  /$$$$$$$  | $$    
| $$\  $$$| $$  | $$ \____  $$ /$$__  $$| $$    $$| $$  | $$ /$$__  $$  | $$ /$$
| $$ \  $$|  $$$$$$/ /$$$$$$$/|  $$$$$$$|  $$$$$$/| $$  | $$|  $$$$$$$  |  $$$$/
|__/  \__/ \______/ |_______/  \_______/ \______/ |__/  |__/ \_______/   \___/  
Server: {self.server_url}
"""
        print(banner)
    
    def on_connect(self):
        print("[INFO] Terhubung ke server!")
        self.connected = True
        print(f"\n{'─'*60}")
        print("Ketik /help untuk melihat perintah yang tersedia")
        print(f"{'─'*60}\n")
        
        # Set nickname
        self.sio.emit('set_nickname', {'nickname': self.nickname})
    
    def on_disconnect(self):
        print("\n[ERROR] Disconnected dari server")
        self.connected = False
    
    def on_message(self, data):
        timestamp = data.get('timestamp', '')
        nickname = data.get('nickname', '')
        message = data.get('message', '')
        # Print dengan newline supaya tidak menimpa input prompt
        print(f"\r[{timestamp}] {nickname}: {message}\n[PESAN] ", end='', flush=True)
    
    def on_server_message(self, data):
        message = data.get('message', '')
        print(f"\r[SERVER] {message}\n[PESAN] ", end='', flush=True)
    
    def on_error(self, data):
        message = data.get('message', '')
        print(f"\r[ERROR] {message}\n[PESAN] ", end='', flush=True)
    
    def send_input(self):
        while self.connected:
            try:
                message = input("[PESAN] ")
                
                if message.lower() == '/quit':
                    print("\n[INFO] Keluar dari chat...")
                    self.connected = False
                    self.sio.disconnect()
                    os._exit(0)
                elif message.lower() == '/help':
                    print("""
╔════════════════════════════════════════╗
║ /quit   - Keluar dari chat             ║
║ /help   - Tampilkan bantuan            ║
║ /clear  - Bersihkan layar              ║
║ /change - Ganti username               ║
╚════════════════════════════════════════╝
""")
                elif message.lower() == '/clear':
                    self.clear_screen()
                    self.print_banner()
                    print(f"{'─'*60}")
                    print("Ketik /help untuk melihat perintah yang tersedia")
                    print(f"{'─'*60}\n")
                elif message.lower() == '/change':
                    print("\nMasukkan username baru:")
                    new_nickname = input(">>> ").strip()
                    if new_nickname:
                        self.nickname = new_nickname
                        self.save_config()
                        print(f"[INFO] Username berubah menjadi: {self.nickname}")
                        print("[INFO] Username akan digunakan saat reconnect")
                    else:
                        print("[ERROR] Username tidak boleh kosong!")
                elif message.strip():
                    self.sio.emit('message', {'message': message})
                    
            except Exception as e:
                if self.connected:
                    print(f"\n[ERROR] {e}")
                break
    
    def start(self):
        self.clear_screen()
        self.print_banner()
        
        # Load username dari file
        saved_nickname = self.load_config()
        
        if saved_nickname:
            print(f"Username tersimpan: {saved_nickname}")
            print("Pilih:")
            print("1. Gunakan username yang tersimpan")
            print("2. Ganti dengan username baru")
            choice = input(">>> ").strip()
            
            if choice == '2':
                print("\nMasukkan username baru:")
                self.nickname = input(">>> ").strip()
                if not self.nickname:
                    print("[ERROR] Username tidak boleh kosong!")
                    return
            else:
                self.nickname = saved_nickname
        else:
            print("Masukkan username Anda:")
            self.nickname = input(">>> ").strip()
            
            if not self.nickname:
                print("[ERROR] Username tidak boleh kosong!")
                return
        
        # Save username
        self.save_config()
        print(f"\n[INFO] Username: {self.nickname}")
        
        try:
            print(f"[INFO] Menghubungkan ke server...")
            self.sio.connect(self.server_url, 
                           transports=['websocket', 'polling'],
                           wait_timeout=10)
            
            # Start input thread
            input_thread = threading.Thread(target=self.send_input)
            input_thread.daemon = True
            input_thread.start()
            
            # Keep main thread alive
            self.sio.wait()
            
        except Exception as e:
            print(f"[ERROR] Tidak dapat terhubung ke server: {e}")
            print(f"\nPastikan:")
            print(f"1. Server sudah running: python3 chat_server_socketio.py")
            print(f"2. ngrok sudah expose: ngrok http 5555")
            print(f"3. URL ngrok benar: {self.server_url}")
            return

if __name__ == "__main__":
    client = ChatClient(SERVER_URL)
    try:
        client.start()
    except KeyboardInterrupt:
        print("\n[INFO] Keluar dari chat...")
        exit(0)
