# Modelo Computacional Educativo de Sistema de Alerta Temprana (SAT) para Sismos y Tsunamis



Proyecto académico – Didáctica STEM | UNAN–Managua – UNIR México

Este repositorio contiene el desarrollo del Modelo Computacional Educativo de un Sistema de Alerta Temprana (SAT) orientado a la enseñanza del Movimiento Oscilatorio y Ondulatorio, la prevención de sismos y tsunamis, y la integración de la Didáctica STEM en la formación de docentes de Física–Matemática.

El proyecto se fundamenta en la necesidad de acercar a los estudiantes a fenómenos reales de alta relevancia social mediante modelación matemática, física y computacional, utilizando herramientas accesibles como Python, y simulaciones digitales. La ausencia de modelos computacionales educativos de SAT desde una perspectiva pedagógica limita las oportunidades de los estudiantes para comprender los principios y fundamentos físicos aplicados a contextos reales.



OBJETIVO GENERAL

Validar un Modelo Computacional de Sistema de Alerta Temprana (SAT) que integre la Didáctica STEM en la enseñanza de la prevención y mitigación de sismos y tsunamis con estudiantes de la carrera de Física–Matemática del CUR Estelí.



OBJETIVOS ESPECÍFICOS

Analizar fundamentos teóricos del movimiento ondulatorio y el efecto Doppler aplicados a sismos y tsunamis.

Diseñar un modelo computacional de SAT utilizando herramientas tecnológicas con enfoque didáctico.

Integrar el modelo en metodologías activas STEM.

Presentar el modelo ante autoridades y estudiantes para su validación académica.



FUNDAMENTACIÓN STEM

La Didáctica STEM promueve la integración articulada de la Ciencia, la Tecnología, la Ingeniería y la Matemática favoreciendo un aprendizaje significativo y contextualizado.



COMPONENTES CLAVES

Ciencia: estudio de ondas sísmicas, energía, magnitud, intensidad.

Tecnología: sensores, microcontroladores, comunicación serial.

Ingeniería: diseño del sistema, calibración, pruebas.

Matemáticas: ecuaciones diferenciales, modelos de ondas, análisis de señales.



Modelo Matemático del Sismo
El fenómeno sísmico se modela inicialmente como un oscilador armónico simple:

𝑑
2
𝑥
𝑑
𝑡
2
+
𝜔
2
𝑥
=
0
Con solución:

𝑥
(
𝑡
)
=
𝐴
cos
⁡
(
𝜔
𝑡
+
𝜙
)
La aceleración crítica se obtiene mediante:

𝑎
(
𝑡
)
=
𝜔
2
𝑥
(
𝑡
)




Umbrales educativos utilizados:


Aceleración	Clasificación
Sismo leve
0.05–0.2 g	Moderado
≥ 0.2 g	Fuerte
También se incorpora la relación energía–magnitud:

log
⁡
𝐸
𝑅
=
1.5
𝑀
𝑠
+
4.8



MODELO MATEMÁTICO DEL TSUNAMI
El tsunami se modela como una onda larga dependiente de la profundidad:

𝑣
=
𝑔
ℎ
Ecuación de onda:

𝑑
2
𝜂
𝑑
𝑡
2
=
𝑔
ℎ
𝑑
2
𝜂
𝑑
𝑥
2
Amplificación costera:

𝐴
𝑐
=
𝐴
0
ℎ
0
ℎ
𝑐
Umbrales educativos:

Altura de ola	Clasificación
Leve
0.5–2.0 m	Moderado
≥ 2.0 m	Severo



MODELO COMPUTACIONAL

El modelo computacional integra los modelos físico y matemático mediante Python.

Procesamiento y análisis de señal

FFT, curtosis, STA/LTA, umbrales

Visualización

Gráficas en tiempo real

Generación de alerta

Activación según umbrales críticos

Cierre y reflexión didáctica

El uso de herramientas tecnológicas no reemplaza el razonamiento científico, sino que lo potencia analizando situaciones complejas.
