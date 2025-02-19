```
pip install -r requirements.txt
```

```
docker build --no-cache -t auto-gen-ai .
```

```
docker run --env-file .env -p 8501:8501 auto-gen-ai
```

Build and start the container (first time)
```
docker-compose up --build
```

If your Streamlit app automatically reloads, you don’t need to do anything.
If not, restart the container with
```
docker-compose restart app
```



Or manually stop and start the app

```
docker-compose down && docker-compose up

```

if you modify requirements.txt, you need to update dependencies inside the container:
```
docker-compose exec app pip install -r requirements.txt

```