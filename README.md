# yamdb_final
![YaMDB workflow](https://github.com/v-sinitsin/yamdb_final/actions/workflows/yamdb_workflow.yaml/badge.svg)
### Описание
API для оценки и создания отзывов на фильмы
### Как запустить
1. Установите [Docker](https://www.docker.com/) для вашей ОС
2. Склонируйте [данный репозиторий](https://github.com/v-sinitsin/infra_sp2.git)
3. В каталоге проекта создайте файл ```.env``` со следующим содержимым:
```` 
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД 
````
3. В каталоге проекта выполните команды для создания и применения миграций, создания суперпользователя, а также для загрузки тестовых данных:  
```` 
docker-compose up -d 
docker-compose exec web python manage.py makemigrations api
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py loaddata fixtures.json
````
### Технологии
Python  
Django  
DRF  
### Автор
[Владимир Синицин](https://github.com/v-sinitsin)
