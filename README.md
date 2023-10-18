![TeamCity build status](https://teamcity.milkhunters.ru/app/rest/builds/buildType:id:MilkhuntersBackend_Build_Prod/statusIcon.svg)

# Milky-Blog-Service
Один из основных backend сервисов сайта команды MilkHunters
 

## Установка

Клонируйте проект:
```bash
git clone https://github.com/milkhunters/milky-blog-service.git
```

...


## Docker

Соберите образ приложения:
```bash
docker build -t milky-backend .
```

Запустите контейнер на основе образа:
```bash
docker run -d --restart=always -u 0 --name milky-blog-dev -e DEBUG=1 -e CONSUL_ROOT=milk-back-dev -p 8000:8000 -m 1024m --cpus=2 milky-blog-dev
```
