#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import mimetypes
from pathlib import Path

class VideoGalleryHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Ruta donde están los videos
        self.video_directory = r"C:\Users\sergi\Desktop\RANDOM"
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # API para listar videos
        if parsed_path.path == '/api/videos':
            self.handle_video_list()
        # Servir videos desde la carpeta especificada
        elif parsed_path.path.startswith('/videos/'):
            self.handle_video_file(parsed_path.path)
        # Servir archivos estáticos (HTML, CSS, JS)
        else:
            super().do_GET()
    
    def handle_video_list(self):
        """Devuelve la lista de videos en formato JSON"""
        try:
            if not os.path.exists(self.video_directory):
                self.send_error_response(404, "Directorio de videos no encontrado")
                return
            
            video_extensions = {'.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv', '.flv'}
            videos = []
            
            for filename in os.listdir(self.video_directory):
                file_path = os.path.join(self.video_directory, filename)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(filename.lower())
                    if ext in video_extensions:
                        try:
                            file_size = os.path.getsize(file_path)
                            size_mb = round(file_size / (1024 * 1024), 2)
                            videos.append({
                                'name': filename,
                                'path': f'/videos/{filename}',
                                'size': f'{size_mb} MB',
                                'extension': ext
                            })
                        except OSError:
                            continue
            
            # Ordenar por nombre
            videos.sort(key=lambda x: x['name'].lower())
            
            self.send_json_response(videos)
            
        except Exception as e:
            self.send_error_response(500, f"Error al listar videos: {str(e)}")
    
    def handle_video_file(self, path):
        """Sirve archivos de video desde la carpeta especificada"""
        try:
            # Extraer el nombre del archivo de la URL
            filename = path.split('/videos/')[-1]
            file_path = os.path.join(self.video_directory, filename)
            
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                self.send_error(404, "Video no encontrado")
                return
            
            # Verificar que es un archivo de video
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type or not mime_type.startswith('video/'):
                self.send_error(403, "Tipo de archivo no permitido")
                return
            
            # Servir el archivo
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(os.path.getsize(file_path)))
            self.send_header('Accept-Ranges', 'bytes')
            self.end_headers()
            
            with open(file_path, 'rb') as f:
                self.copyfile(f, self.wfile)
                
        except Exception as e:
            self.send_error_response(500, f"Error al servir video: {str(e)}")
    
    def send_json_response(self, data):
        """Envía una respuesta JSON"""
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(json_data.encode('utf-8'))))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def send_error_response(self, code, message):
        """Envía una respuesta de error en JSON"""
        error_data = {'error': message, 'code': code}
        json_data = json.dumps(error_data, ensure_ascii=False)
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(json_data.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Personalizar el logging"""
        print(f"[{self.address_string()}] {format % args}")

def run_server(port=8000):
    """Ejecuta el servidor HTTP"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, VideoGalleryHandler)
    
    print(f"\n🎬 Servidor de Galería de Videos iniciado")
    print(f"📁 Directorio de videos: C:\\Users\\sergi\\Desktop\\RANDOM")
    print(f"🌐 Servidor ejecutándose en: http://localhost:{port}")
    print(f"🔗 Abrir en navegador: http://localhost:{port}")
    print("\n⚡ Presiona Ctrl+C para detener el servidor\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")
        httpd.server_close()

if __name__ == '__main__':
    # Verificar si el directorio de videos existe
    video_dir = r"C:\Users\sergi\Desktop\RANDOM"
    if not os.path.exists(video_dir):
        print(f"⚠️  ADVERTENCIA: El directorio {video_dir} no existe.")
        print("   Por favor, verifica la ruta o crea el directorio.")
        print("   El servidor se iniciará de todos modos.\n")
    
    run_server(8000)