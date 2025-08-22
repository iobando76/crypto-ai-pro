FROM python:3.11-slim
WORKDIR /workspace
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000 8501
CMD ["bash","-lc","uvicorn app.api.app:app --host 0.0.0.0 --port 8000 & streamlit run app/ui/app.py --server.address 0.0.0.0 --server.port 8501"]
