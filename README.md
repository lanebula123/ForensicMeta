# ForensicMeta 🔍

ForensicMeta es una aplicación web diseñada para el análisis de metadatos en archivos y la auditoría de seguridad. Este proyecto ha sido desarrollado bajo un enfoque de **Ciclo de Vida de Desarrollo Seguro (S-SDLC)**, integrando pruebas SAST, DAST y auditoría de contenedores.

## 🚀 Instalación y Despliegue con Docker

La forma más rápida de ejecutar la aplicación es utilizando el contenedor publicado en Docker Hub.

### Requisitos previos
* Tener [Docker](https://docs.docker.com/get-docker/) instalado.

### Comandos de ejecución
1. **Descargar la imagen:**
   ```bash
   docker pull luisaraujo1234/forensicmeta:latest

  2. **Ejecutar el contenedor:**
     ```bash
     docker run -d -p 8080:5000 --name forensicmeta_app luisaraujo1234/forensicmeta:latest

 2. **Accede a la aplicación en:**
    ```bash
    http://localhost:8080


