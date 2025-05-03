# Sistema de detección y seguimiento de animales

Sistema capaz de detectar y realizar el seguimiento de animales en tiempo real con utilización de algoritmos de aprendizaje profundo como YOLO y de seguimiento de objetos como lo es SORT y DeepSORT. Estos algoritmos de seguimiento utilizan filtros de Kalman para estimar la trayectoria de los objetos en movimiento, incluso cuando las detecciones son ruidosas o intermitentes. 

Para el desarrollo de este sistema se implementó utilizando Python 3.12.0, _SORT_ de código abierto, _deep-sort-realtime_ y el modelo yolov8l de _ultralytics_. Además de ciertas librerías como _OpenCV_, _Numpy_ _CVzone_ y _filterpy_. Para el manual general de ejecución, se puede observar el proyecto de [HMI_DSP](../HMI_DSP) (Interfaz de procesamiento digital de señales); sin embargo, en este apartado se explicará el desempeño del sistema y los fundamentos técnicos.


### YOLO
YOLOv8 es un detector de objetos basado en redes neuronales convolucionales que realiza inferencias en una sola pasada sobre la imagen, combinando rapidez y precisión. En este sistema, se utiliza el modelo preentrenado _yolov8l.pt_ de Ultralytics, con soporte para detección de múltiples clases. Solo se consideran detecciones con confianza mayor a 0.5 y pertenecientes a clases de interés, como horse.

Características principales:

* Inferencia rápida en GPU y CPU.

* Alta precisión en la detección de bordes.

* Capacidad de trabajar en flujos de video.

### Filtro de Kalman
El filtro de Kalman es un estimador recursivo que permite predecir el estado de un sistema dinámico en presencia de ruido. En este caso, se utiliza para estimar y actualizar la posición de los objetos detectados, proporcionando robustez frente a detecciones erróneas o ausentes.

En la implementación se modela cada objeto con un estado de 7 dimensiones, incluyendo posición, escala, razón de aspecto y velocidad. Se emplea un modelo de movimiento con velocidad constante, adecuado para escenarios con trayectorias suaves.

### SORT y DeepSORT
SORT (Simple Online and Realtime Tracking):

Ligero y eficiente.

Asigna IDs a cada objeto detectado mediante la predicción del filtro de Kalman y una estrategia de asignación basada en IOU (Intersección sobre Unión).

Se usa cuando no se requiere información adicional (como apariencia visual).

DeepSORT:

Extiende SORT utilizando un extractor de características visuales para mejorar la asociación entre detecciones y trayectorias.

Utiliza métricas de distancia del espacio latente (coseno) para reforzar el seguimiento, ideal para escenarios con múltiples objetos similares.

Ambos métodos permiten realizar seguimiento multiobjeto y mantener una asociación coherente entre frames consecutivos.

### Funcionamiento general
Primeramente, el abordaje fue utilizar un modelo preentrenado de YOLOv8 para la detección de animales y con el uso de SORT, proveer de una solución al seguimiento. Dentro de este algoritmo, los parámetros más importantes son: 

* **max_age=60**: Este parámetro define cuántos frames puede permanecer _activo_ un objeto rastreado sin recibir nuevas detecciones antes perderse, o no obtener nuevas actuzalizaciones y ser eliminado del seguimiento. Este valor es alto para permitir que los animales se sigan detectando aún cuando salgan de frame o se pierda el ángulo.

* **min_hits=1**: Establece el número mínimo de veces que un objeto debe ser detectado de manera consistente para ser considerado como un objet válido. Un valor pequeño permite que el seguimiento se adecue a cambios bruscos.

* **iou_threshold=0.1**: Define el umbral mínimo del coeficiente de Intersection over Union (IoU) para asociar detecciones consecutivas al mismo animal. Un valor bajo, como en ese caso, implica que se permite mayor variación en la posición del objeto entre cuadros, lo cual es útil cuando las detecciones de YOLO son ruidosas o hay movimientos bruscos.

Estos parámetros definen el trackeo inicial, y se utiliza de la siguiente manera:

```bash
detections = np.empty((0, 5)) #Arreglo para detecciones
results = self.predict(img) #Predicción de YOLOv8
detections, frames = self.plot_boxes(results, img, detections) #Marcar como detecciones para tracker
```

Este fragmento de código complementa al seguimiento ya que, inicialmente inicializa el arreglo para las detecciones con el formato: [x1, y1, x2, y2, confidence], después se genera la predicción con el modelo preentrenado para finalmente marcar ese resultado como una detección más para el seguimiento.

La línea:
```bash
resultTracker = tracker.update(detections)
```

Dentro de la función _track_detect_, recibe las detecciones dadas por YOLO y devuelve cajas con el formato [x1, y1, x2, y2, ID], donde ID es el identificador de cada animal en específico.

Esto finalmente se realiza iterativamente y progresivamente con cada frame permitiendo identificar y seguir cada detección ligada a un identificador. Los resultados son los siguientes:

![](result/results_dogs.avi)


#### Referencias
* Ultralytics YOLOv8: https://docs.ultralytics.com

* SORT: Bewley et al., "Simple Online and Realtime Tracking", 2016.

* DeepSORT: Wojke et al., "Simple Online and Realtime Tracking with a Deep Association Metric", 2017.

* filterpy: https://github.com/rlabbe/filterpy

* cvzone: https://github.com/cvzone/cvzone
