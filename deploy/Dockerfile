# JEV-as-a-Judge: vLLM serving autotrust/JEV-9B + the judging API, in one GPU container.
#   docker build -t jev-judge -f deploy/Dockerfile .
#   docker run --gpus all -p 8080:8080 -e JUDGE_API_KEY=change-me -e HF_TOKEN=... jev-judge
FROM vllm/vllm-openai:v0.31.0
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -e '.[server]'
COPY deploy/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENV VLLM_URL=http://127.0.0.1:8000 GPU_USD_PER_HR=0.59
EXPOSE 8080
ENTRYPOINT ["/app/entrypoint.sh"]
