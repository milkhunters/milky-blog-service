![TeamCity build status](https://teamcity.milkhunters.ru/app/rest/builds/buildType:id:MilkhuntersBackend_Build_Prod/statusIcon.svg)

# MilkHunters-backend
Основной backend сайта команды MilkHunters
 

Используется фреймворк FastAPI

```bash
pip install -r requirements.txt
```

Следует определить переменные окружения:
```bash
export MODE=dev
export DEBUG=1
```

Для запуска приложения:
```bash
uvicorn src.app:app --proxy-headers --host 0.0.0.0 --port 8000
```


Также можно запустить приложение через docker, собрав образ:
```bash
docker build -t milkhunters-backend .
```

И запустив контейнер:
```bash
docker run -d --restart=always -u 0 --name milkhunters-backend -e MODE=dev -e DEBUG=1 -p 8000:8000 -m 1024m --cpus=2 milkhunters-backend
```
