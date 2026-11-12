FROM python:3.12-slim
WORKDIR /app

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY data/docs ./data/docs
COPY results/chosen_threshold.json ./results/chosen_threshold.json

# Build the vector index and download both models at build time, so startup is fast
RUN python -c "import sys; sys.path.insert(0, 'src'); from retrieve import build_index; build_index(200)" \
 && python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

EXPOSE 8000
CMD ["uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]