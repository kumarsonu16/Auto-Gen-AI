```
pip install -r requirements.txt
```

```
docker build --no-cache -t auto-gen-ai .
```

```
docker run --env-file .env -p 8501:8501 auto-gen-ai
```