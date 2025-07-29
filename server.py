#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import mimetypes
from pathlib import Path

class VideoGalleryHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Ruta donde están los videos
        self.video_directory = r"C:\Users\sergi\Desktop\RANDOM"
        super().__init__(*args, **kwargs)
    
    def handle_one_request(self):
        """Maneja una sola petición HTTP con manejo de errores mejorado"""
        try:
            super().handle_one_request()
        except ConnectionResetError:
            # El cliente cerró la conexión abruptamente - esto es normal
            self.log_message("Cliente desconectado abruptamente")
        except BrokenPipeError:
            # El cliente cerró la conexión antes de recibir la respuesta completa
            self.log_message("Conexión cerrada por el cliente")
        except socket.error as e:
            # Otros errores de socket
            self.log_message(f"Error de socket: {e}")
        except Exception as e:
            # Otros errores inesperados
            self.log_message(f"Error inesperado: {e}")
    
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
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        # API para borrar videos
        if parsed_path.path == '/api/delete-video':
            self.handle_delete_video()
        else:
            self.send_error_response(404, 'Endpoint no encontrado')
    
    def handle_video_list(self):
        """Devuelve la lista de videos en formato JSON"""
        try:
            # Obtener la ruta de los parámetros de consulta
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            # Usar la ruta proporcionada o la ruta por defecto
            target_directory = query_params.get('path', [self.video_directory])[0]
            
            if not os.path.exists(target_directory):
                self.send_error_response(404, f"Directorio no encontrado: {target_directory}")
                return
            
            if not os.path.isdir(target_directory):
                self.send_error_response(400, f"La ruta especificada no es un directorio: {target_directory}")
                return
            
            video_extensions = {'.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv', '.flv'}
            videos = []
            
            try:
                for filename in os.listdir(target_directory):
                    file_path = os.path.join(target_directory, filename)
                    if os.path.isfile(file_path):
                        _, ext = os.path.splitext(filename.lower())
                        if ext in video_extensions:
                            try:
                                file_size = os.path.getsize(file_path)
                                size_mb = round(file_size / (1024 * 1024), 2)
                                videos.append({
                                    'name': filename,
                                    'path': f'/videos/{filename}?dir={target_directory}',
                                    'size': f'{size_mb} MB',
                                    'extension': ext
                                })
                            except OSError:
                                continue
            except PermissionError:
                self.send_error_response(403, f"Sin permisos para acceder al directorio: {target_directory}")
                return
            
            # Ordenar por nombre
            videos.sort(key=lambda x: x['name'].lower())
            
            self.send_json_response(videos)
            
        except Exception as e:
            self.send_error_response(500, f"Error al listar videos: {str(e)}")
    
    def handle_video_file(self, path):
        """Sirve archivos de video desde la carpeta especificada"""
        try:
            # Parsear la URL para obtener parámetros
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            # Extraer el nombre del archivo de la URL
            filename = parsed_path.path.split('/videos/')[-1]
            
            # Obtener el directorio de los parámetros o usar el por defecto
            target_directory = query_params.get('dir', [self.video_directory])[0]
            file_path = os.path.join(target_directory, filename)
            
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
    
    def handle_delete_video(self):
        """Maneja la eliminación de videos"""
        try:
            # Leer el cuerpo de la petición
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parsear JSON
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_error_response(400, "JSON inválido")
                return
            
            filename = data.get('filename')
            directory = data.get('directory')
            
            if not filename:
                self.send_error_response(400, "Nombre de archivo requerido")
                return
            
            if not directory:
                directory = self.video_directory
            
            # Construir la ruta completa del archivo
            file_path = os.path.join(directory, filename)
            
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                self.send_error_response(404, f"El archivo {filename} no existe")
                return
            
            # Verificar que es un archivo (no un directorio)
            if not os.path.isfile(file_path):
                self.send_error_response(400, f"{filename} no es un archivo válido")
                return
            
            # Verificar que el archivo está dentro del directorio permitido
            abs_file_path = os.path.abspath(file_path)
            abs_directory = os.path.abspath(directory)
            
            if not abs_file_path.startswith(abs_directory):
                self.send_error_response(403, "Acceso denegado: archivo fuera del directorio permitido")
                return
            
            # Intentar borrar el archivo
            try:
                os.remove(file_path)
                self.log_message(f"Archivo borrado: {file_path}")
                
                # Enviar respuesta de éxito
                response_data = {
                    "success": True,
                    "message": f"Video {filename} borrado exitosamente"
                }
                self.send_json_response(response_data)
                
            except PermissionError:
                self.send_error_response(403, f"Sin permisos para borrar {filename}")
            except OSError as e:
                self.send_error_response(500, f"Error del sistema al borrar {filename}: {str(e)}")
                
        except Exception as e:
            self.send_error_response(500, f"Error interno del servidor: {str(e)}")
    
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
        print("\n🛑 Servidor detenido por el usuario")
    except ConnectionResetError:
        print("\n⚠️  Conexión reiniciada - el servidor continúa ejecutándose")
        # Reiniciar el servidor automáticamente
        run_server(port)
    except Exception as e:
        print(f"\n❌ Error del servidor: {e}")
        print("🔄 Intentando reiniciar el servidor...")
        # Reiniciar el servidor automáticamente
        run_server(port)
    finally:
        httpd.server_close()

if __name__ == '__main__':
    # Verificar si el directorio de videos existe
    video_dir = r"C:\Users\sergi\Desktop\RANDOM"
    if not os.path.exists(video_dir):
        print(f"⚠️  ADVERTENCIA: El directorio {video_dir} no existe.")
        print("   Por favor, verifica la ruta o crea el directorio.")
        print("   El servidor se iniciará de todos modos.\n")
    
    run_server(8000)