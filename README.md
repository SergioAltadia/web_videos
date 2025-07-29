# 🎬 Galería de Videos Web

Una galería web moderna para visualizar videos en bucle automático desde una carpeta local.

## 📋 Características

- ✅ Reproducción automática en bucle de todos los videos
- ✅ Diseño responsive tipo carrete/grid
- ✅ Scroll suave para navegar por los videos
- ✅ Múltiples videos visibles simultáneamente
- ✅ Información de archivos al hacer hover
- ✅ Soporte para múltiples formatos de video
- ✅ Interfaz moderna y elegante

## 🚀 Cómo usar

### Paso 1: Verificar la carpeta de videos
Asegúrate de que la carpeta `C:\Users\sergi\Desktop\RANDOM` existe y contiene videos.

### Paso 2: Iniciar el servidor
Abre una terminal en esta carpeta y ejecuta:

```bash
python server.py
```

### Paso 3: Abrir en el navegador
Ve a: `http://localhost:8000`

## 📁 Estructura del proyecto

```
web_videos/
├── index.html          # Página principal de la galería
├── server.py           # Servidor Python para servir videos
└── README.md           # Este archivo
```

## 🎥 Formatos de video soportados

- MP4 (.mp4)
- WebM (.webm)
- OGG (.ogg)
- MOV (.mov)
- AVI (.avi)
- MKV (.mkv)
- FLV (.flv)

## ⚙️ Configuración

Para cambiar la carpeta de videos, edita la línea en `server.py`:

```python
self.video_directory = r"C:\Users\sergi\Desktop\RANDOM"
```

## 🔧 Requisitos

- Python 3.6 o superior
- Navegador web moderno
- Videos en la carpeta especificada

## 📱 Características responsive

- **Desktop**: Grid de múltiples columnas
- **Tablet**: Grid adaptativo
- **Mobile**: Grid optimizado para pantallas pequeñas

## 🎨 Personalización

Puedes modificar el CSS en `index.html` para:
- Cambiar colores y temas
- Ajustar el tamaño de los videos
- Modificar el número de columnas
- Personalizar efectos de hover

## 🛠️ Solución de problemas

### Los videos no se cargan
1. Verifica que la carpeta existe: `C:\Users\sergi\Desktop\RANDOM`
2. Asegúrate de que hay videos en la carpeta
3. Comprueba que el servidor está ejecutándose

### Error de permisos
- Ejecuta la terminal como administrador si es necesario

### Puerto ocupado
- Cambia el puerto en `server.py` (línea final): `run_server(8001)`

## 📞 Soporte

Si encuentras algún problema:
1. Revisa la consola del navegador (F12)
2. Verifica los logs del servidor Python
3. Asegúrate de que los archivos de video no están corruptos

---

¡Disfruta de tu galería de videos! 🎉