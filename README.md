# Aplicación Dash sobre Indicadores de México

![](assets/app_screencast.gif)

Los datos utilizados en esta aplicación provienen de fuentes oficiales de México, como el **INEGI** y la **Secretaría de Salud**. Los gráficos reflejan indicadores relevantes como la **tasa de natalidad**, **mortalidad**, **escolaridad**, y otros aspectos demográficos y sociales importantes.  

Mapa programado por:  
Oswaldo Rendón Lira  
Marco Iván Rodríguez Graciano  

Página basada en el repositorio de Dash Gallery App: Opioid Epidemic  
Información y datos obtenidos de datos oficiales del Gobierno Mexicano.

---

## Introducción

Esta aplicación utiliza **Dash** para proporcionar una visualización interactiva de los indicadores clave en México. Su propósito es permitir a los usuarios explorar tendencias demográficas y sociales de forma dinámica y personalizada.

---

## Comenzando

### Ejecutar la aplicación de manera local

Es recomendable crear un entorno virtual separado que ejecute **Python 3** para esta aplicación, e instalar todas las dependencias necesarias ahí. Ejecuta los siguientes comandos en tu Terminal o Símbolo del sistema:

```
git clone https://github.com/MarcoGraciano69/MapaInteractivoMexico.git
python3 -m virtualenv venv
```
En sistemas con UNIX:

```
source venv/bin/activate
```
En Windows: 

```
venv\Scripts\activate
```

Para instalar los paquetes y módulos necesarios:

```
pip install -r modulos.txt
```
Para correr finalmente el Mapa Interactivo:
```
python MapaFinal.py
```

