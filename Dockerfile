FROM python:3.12.6

WORKDIR /
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8001
CMD ["streamlit", "run", "app/main.py"]
