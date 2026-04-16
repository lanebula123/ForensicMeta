# Usar una imagen ligera de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para ForensicMeta
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

# COPIA CORREGIDA: Ahora busca el archivo en la raíz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer puerto de Flask
EXPOSE 5000

CMD ["python", "app.py"]
