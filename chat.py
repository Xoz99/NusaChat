#!/usr/bin/env python3
import socketio
import threading
import os
import sys
import datetime
import json
SERVER_URL = "https://prejuvenile-trickly-jacqui.ngrok-free.dev"
CONFIG_FILE = "chat_config.json"
class Colors:
    CYAN = '\033[96m'
    LIGHT_BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_BLUE = '\033[94m'

class ChatClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=10, reconnection_delay=1)
        self.nickname = ""
        self.connected = False
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
            print(f"{Colors.YELLOW}[WARNING] Error loading config: {e}{Colors.RESET}")
        return ''
    
    def save_config(self):
        """Simpan username ke file config"""
        try:
            config = {'nickname': self.nickname}
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"{Colors.YELLOW}[WARNING] Error saving config: {e}{Colors.RESET}")
    
    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_banner(self):
        banner = f"""{Colors.BRIGHT_CYAN}{Colors.BOLD} /$$   /$$                                /$$$$$$  /$$                   /$$    
| $$$ | $$                               /$$__  $$| $$                  | $$    
| $$$$| $$ /$$   /$$  /$$$$$$$  /$$$$$$ | $$  \__/| $$$$$$$   /$$$$$$  /$$$$$$  
| $$ $$ $$| $$  | $$ /$$_____/ |____  $$| $$      | $$__  $$ |____  $$|_  $$_/  
| $$  $$$$| $$  | $$|  $$$$$$   /$$$$$$$| $$      | $$  \ $$  /$$$$$$$  | $$    
| $$\  $$$| $$  | $$ \____  $$ /$$__  $$| $$    $$| $$  | $$ /$$__  $$  | $$ /$$
| $$ \  $$|  $$$$$$/ /$$$$$$$/|  $$$$$$$|  $$$$$$/| $$  | $$|  $$$$$$$  |  $$$$/
|__/  \__/ \______/ |_______/  \_______/ \______/ |__/  |__/ \_______/   \___/  {Colors.RESET}

{Colors.LIGHT_BLUE}{Colors.BOLD}Server: {self.server_url}{Colors.RESET}
"""
        print(banner)
    
    def on_connect(self):
        print(f"{Colors.GREEN}{Colors.BOLD}[✓] Terhubung ke server!{Colors.RESET}")
        self.connected = True
        print(f"\n{Colors.CYAN}{'─'*60}{Colors.RESET}")
        print(f"{Colors.YELLOW}Ketik /help untuk melihat perintah yang tersedia{Colors.RESET}")
        print(f"{Colors.CYAN}{'─'*60}{Colors.RESET}\n")
        self.sio.emit('set_nickname', {'nickname': self.nickname})
    
    def on_disconnect(self):
        print(f"\n{Colors.RED}{Colors.BOLD}[✗] Disconnected dari server{Colors.RESET}")
        self.connected = False
    
    def on_message(self, data):
        timestamp = data.get('timestamp', '')
        nickname = data.get('nickname', '')
        message = data.get('message', '')
        print(f"\r{Colors.LIGHT_BLUE}[{timestamp}]{Colors.RESET} {Colors.MAGENTA}{nickname}{Colors.RESET}: {message}\n{Colors.CYAN}[PESAN]{Colors.RESET} ", end='', flush=True)
    
    def on_server_message(self, data):
        message = data.get('message', '')
        print(f"\r{Colors.GREEN}{Colors.BOLD}[SERVER]{Colors.RESET} {message}\n{Colors.CYAN}[PESAN]{Colors.RESET} ", end='', flush=True)
    
    def on_error(self, data):
        message = data.get('message', '')
        print(f"\r{Colors.RED}{Colors.BOLD}[ERROR]{Colors.RESET} {message}\n{Colors.CYAN}[PESAN]{Colors.RESET} ", end='', flush=True)
    
    def send_input(self):
        while self.connected:
            try:
                message = input(f"{Colors.CYAN}[PESAN]{Colors.RESET} ")
                
                if message.lower() == '/quit':
                    print(f"\n{Colors.YELLOW}{Colors.BOLD}[INFO] Keluar dari chat...{Colors.RESET}")
                    self.connected = False
                    self.sio.disconnect()
                    os._exit(0)
                elif message.lower() == '/help':
                    print(f"""{Colors.BRIGHT_CYAN}{Colors.BOLD}
╔════════════════════════════════════════╗
║ /quit   - Keluar dari chat             ║
║ /help   - Tampilkan bantuan            ║
║ /clear  - Bersihkan layar              ║
║ /change - Ganti username               ║
╚════════════════════════════════════════╝{Colors.RESET}
""")
                elif message.lower() == '/clear':
                    self.clear_screen()
                    self.print_banner()
                    print(f"{Colors.CYAN}{'─'*60}{Colors.RESET}")
                    print(f"{Colors.YELLOW}Ketik /help untuk melihat perintah yang tersedia{Colors.RESET}")
                    print(f"{Colors.CYAN}{'─'*60}{Colors.RESET}\n")
                elif message.lower() == '/change':
                    print(f"\n{Colors.YELLOW}Masukkan username baru:{Colors.RESET}")
                    new_nickname = input(f"{Colors.LIGHT_BLUE}>>> {Colors.RESET}").strip()
                    if new_nickname:
                        self.nickname = new_nickname
                        self.save_config()
                        print(f"{Colors.GREEN}[✓] Username berubah menjadi: {Colors.BOLD}{self.nickname}{Colors.RESET}")
                        print(f"{Colors.YELLOW}[INFO] Username akan digunakan saat reconnect{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}[✗] Username tidak boleh kosong!{Colors.RESET}")
                elif message.strip():
                    self.sio.emit('message', {'message': message})
                    
            except Exception as e:
                if self.connected:
                    print(f"\n{Colors.RED}{Colors.BOLD}[ERROR] {e}{Colors.RESET}")
                break
    
    def start(self):
        self.clear_screen()
        self.print_banner()
        saved_nickname = self.load_config()
        
        if saved_nickname:
            print(f"{Colors.LIGHT_BLUE}{Colors.BOLD}Username tersimpan: {saved_nickname}{Colors.RESET}")
            print(f"{Colors.YELLOW}Pilih:{Colors.RESET}")
            print(f"{Colors.CYAN}1. Gunakan username yang tersimpan{Colors.RESET}")
            print(f"{Colors.CYAN}2. Ganti dengan username baru{Colors.RESET}")
            choice = input(f"{Colors.LIGHT_BLUE}>>> {Colors.RESET}").strip()
            
            if choice == '2':
                print(f"\n{Colors.YELLOW}Masukkan username baru:{Colors.RESET}")
                self.nickname = input(f"{Colors.LIGHT_BLUE}>>> {Colors.RESET}").strip()
                if not self.nickname:
                    print(f"{Colors.RED}{Colors.BOLD}[✗] Username tidak boleh kosong!{Colors.RESET}")
                    return
            else:
                self.nickname = saved_nickname
        else:
            print(f"{Colors.YELLOW}Masukkan username Anda:{Colors.RESET}")
            self.nickname = input(f"{Colors.LIGHT_BLUE}>>> {Colors.RESET}").strip()
            
            if not self.nickname:
                print(f"{Colors.RED}{Colors.BOLD}[✗] Username tidak boleh kosong!{Colors.RESET}")
                return






        self.save_config()
        print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] Username: {self.nickname}{Colors.RESET}")
        
        try:
            print(f"{Colors.YELLOW}[INFO] Menghubungkan ke server...{Colors.RESET}")
            self.sio.connect(self.server_url, 
                           transports=['websocket', 'polling'],
                           wait_timeout=10)
            input_thread = threading.Thread(target=self.send_input)
            input_thread.daemon = True
            input_thread.start()
            self.sio.wait()
            
        except Exception as e:
            print(f"{Colors.RED}{Colors.BOLD}[✗] Tidak dapat terhubung ke server: {e}{Colors.RESET}")
            print(f"\n{Colors.YELLOW}Pastikan:{Colors.RESET}")
            print(f"{Colors.CYAN}1. Server sudah running: python3 chat_server_simple.py{Colors.RESET}")
            print(f"{Colors.CYAN}2. ngrok sudah expose: ngrok http 5555{Colors.RESET}")
            print(f"{Colors.CYAN}3. URL ngrok benar: {self.server_url}{Colors.RESET}")
            return

if __name__ == "__main__":
    client = ChatClient(SERVER_URL)
    try:
        client.start()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}[INFO] Keluar dari chat...{Colors.RESET}")
        exit(0)