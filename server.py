#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import urllib.parse

PORT = 8000

class IBRFlowHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        print(f"📡 Richiesta: {self.path}")
        
        # API file audio
        if self.path.startswith('/api/files'):
            self.handle_api_files()
        
        # Servi file audio
        elif self.path.startswith('/audio-files/'):
            self.serve_audio_file(self.path)
        
        # Per tutte le route SPA, servi index.html
        elif any(self.path.startswith(route) for route in ['/', '/production', '/dashboard', '/report', '/contenuti']):
            self.serve_spa()
        
        # File statici (CSS, JS, immagini)
        else:
            super().do_GET()
    
    def serve_spa(self):
        """Serve la SPA IBRFlow per tutte le route"""
        try:
            # Leggi index.html
            with open('index.html', 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content)
            print("✅ Servito index.html (SPA)")
            
        except FileNotFoundError:
            self.send_error(404, "index.html non trovato")
    
    def handle_api_files(self):
        """API per lista file audio"""
        try:
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            requested_path = params.get('path', ['/raw'])[0]
            
            # Percorso sicuro
            if requested_path == '/':
                folder_path = 'audio-files'
            else:
                folder_path = f"audio-files{requested_path}"
                # Prevenire directory traversal
                if '..' in folder_path or not folder_path.startswith('audio-files'):
                    self.send_json_response({'error': 'Percorso non valido'})
                    return
            
            audio_files = []
            if os.path.exists(folder_path):
                for file in os.listdir(folder_path):
                    # Salta file nascosti macOS (._)
                    if not file.startswith('._') and self.is_audio_file(file):
                        file_path = os.path.join(folder_path, file)
                        if os.path.isfile(file_path):
                            size = os.path.getsize(file_path)
                            
                            audio_files.append({
                                'name': file,
                                'size': size,
                                'size_mb': round(size / (1024*1024), 2),
                                'url': f'/audio-files/{requested_path.lstrip("/")}/{urllib.parse.quote(file)}'
                            })
            
            self.send_json_response(audio_files)
            print(f"✅ API: inviati {len(audio_files)} file da {requested_path}")
            
        except Exception as e:
            print(f"❌ Errore API: {e}")
            self.send_json_response({'error': str(e)}, status=500)
    
    def serve_audio_file(self, path):
        """Serve un file audio per la riproduzione"""
        try:
            # Estrai: /audio-files/raw/nomefile.mp3
            file_path = path[len('/audio-files/'):]
            
            if os.path.exists(file_path) and self.is_audio_file(file_path):
                content_type = self.get_mime_type(file_path)
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(content)
                print(f"✅ Servito file audio: {file_path}")
            else:
                print(f"❌ File non trovato: {file_path}")
                self.send_error(404, "File audio non trovato")
                
        except Exception as e:
            print(f"💥 Errore servire file: {e}")
            self.send_error(500, f"Errore: {e}")
    
    def get_mime_type(self, filename):
        """Restituisce il tipo MIME corretto"""
        ext = os.path.splitext(filename.lower())[1]
        mime_types = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.m4a': 'audio/mp4',
            '.flac': 'audio/flac',
            '.aac': 'audio/aac'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def is_audio_file(self, filename):
        audio_extensions = ('.mp3', '.wav', '.m4a', '.flac', '.aac')
        return filename.lower().endswith(audio_extensions)
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.write_json(data)
    
    def write_json(self, data):
        """Scrive dati JSON nella risposta"""
        json_str = json.dumps(data, ensure_ascii=False)
        self.wfile.write(json_str.encode('utf-8'))

print("🚀 IBRFlow Server SPA")
print("📍 http://localhost:8000")
print("📊 Production: http://localhost:8000/#production")
print("📁 Contenuti: http://localhost:8000/#contenuti")
print("🎵 File audio: ./audio-files/")
print("=" * 50)

# Crea cartelle se non esistono
os.makedirs("audio-files/raw", exist_ok=True)
os.makedirs("audio-files/processing", exist_ok=True)
os.makedirs("audio-files/completed", exist_ok=True)

# Verifica che index.html esista
if not os.path.exists('index.html'):
    print("❌ ATTENZIONE: index.html non trovato!")
    print("   Assicurati che index.html sia nella stessa cartella del server")
else:
    print("✅ index.html trovato")

try:
    with socketserver.TCPServer(("", PORT), IBRFlowHandler) as httpd:
        print(f"✅ Server avviato sulla porta {PORT}")
        httpd.serve_forever()
except OSError as e:
    if "Address already in use" in str(e):
        print(f"❌ Porta {PORT} occupata! Uccidi il processo:")
        print("   kill -9 $(lsof -ti:8000)")
    else:
        raise e