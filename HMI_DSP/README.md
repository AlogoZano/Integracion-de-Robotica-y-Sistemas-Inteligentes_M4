# Interfaz gráfica para el procesamiento digital de señales

Implementación de una interfaz simple para el procesamiento digital de audio. Se permite la carga de archivos, cálculo de transformada de Fourier y la implementación de diversos filtros para observar el comportamiento de la señal cargada. Ideal para probar con canciones o audios cuya finalidad sea obtener ciertos componentes frecuenciales.

### Instalación
Se recomienda generar un ambiente virtual con _virtualenv_ para así seleccionar una versión específica de python. En el caso de esta interfaz se recomienda la versión 3.12.0.

 Inicialmente se deben de instalar las dependencias necesarias, en este caso se encuentra en el archivo de texto _requirements.txt_ y se recomienda utilizar _pip_ para la instalación de la siguiente manera:

```bash
pip install requirements.txt
```

**Importante:** La librería utilizada para la lectura de audio: _Librosa_, necesita de la herramienta de decodificación de audio **ffmpeg**. Esta herramienta vendrá por defecto para usuarios de Linux u OSX, sin embargo, para usuarios de Windows, se requiere hacer la instalación externa. Para más información:

* [FFmpeg](https://www.ffmpeg.org/)
* [Librosa](https://librosa.org/doc/main/install.html)

