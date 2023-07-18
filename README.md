![TeamCity build status](https://teamcity.milkhunters.ru/app/rest/builds/buildType:id:MilkhuntersBackend_Build_Prod/statusIcon.svg)

# Milky-backend
Основной backend сайта команды MilkHunters
 

## Установка

Клонируйте проект:
```bash
git clone https://github.com/milkhunters/milky-backend.git
```

Перейдите в директорию проекта, создайте виртуальное окружение и активируйте его:
```bash
cd milky-backend
python3 -m venv venv
source venv/bin/activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

Следует определить переменные окружения:
```bash
export DEBUG=1
export CONSUL_ROOT=milk-back-dev
```

Запустите приложение:
```bash
uvicorn src.app:app --proxy-headers --host 0.0.0.0 --port 8000
```

## Docker

Соберите образ приложения:
```bash
docker build -t milky-backend .
```

Запустите контейнер на основе образа:
```bash
docker run -d --restart=always -u 0 --name milky-backend -e DEBUG=1 -e CONSUL_ROOT=milk-back-dev -p 8000:8000 -m 1024m --cpus=2 milky-backend
```
