FROM python:3.12.6

WORKDIR /
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your Streamlit app and SSL certificates into the container
COPY app/main.py /app/main.py
COPY app/key/cert.pem /app/key/cert.pem
COPY app/key/key.pem /app/key/key.pem

COPY . .

EXPOSE 8001
CMD ["streamlit", "run", "app/main.py", "--server.sslCertFile=app/key/cert.pem", "--server.sslKeyFile=app/key/key.pem"]
