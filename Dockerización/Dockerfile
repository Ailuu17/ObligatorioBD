# Imagen oficial de Python para ejecutar el backend (versión liviana)
FROM python:3.12-slim

# Evita archivos .pyc innecesarios y muestra los logs inmediatamente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copia primero las dependencias para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el script actual. 
# Cuando agreguemos el archivo .py al backend lo incluiremos también
COPY Backend/Backend.py ./Backend.py

# Comando inicial
# El puerto HTTP se cambiará según la API terminada
CMD ["python", "Backend.py"]