# Interface web (Streamlit).
FROM python:3.12-slim

WORKDIR /app

COPY requirements-streamlit.txt ./
RUN pip install --no-cache-dir -r requirements-streamlit.txt

COPY app.py ./

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
