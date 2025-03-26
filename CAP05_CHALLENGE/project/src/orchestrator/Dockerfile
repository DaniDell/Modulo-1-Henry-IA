FROM python:3.10-slim-buster

WORKDIR /app

# Copiar el archivo de requisitos
COPY requirements.txt .
RUN pip install -r requirements.txt

# Instalar el modelo de SpaCy
RUN python -m spacy download en_core_web_sm

# Copiar el resto del código
COPY . .

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]