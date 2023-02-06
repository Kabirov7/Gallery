# The Gallery REST API 
It's something like gallery on your phone. 
This API allows to create albums and save photos. 

# Features
- [x] Registration and authentication
- [x] Create albums
- [x] Upload many photos to one album

# Extra points
- [x] Unit and integration tests
- [x] Dockerized

# Installation
You can easily install Gallery using docker. 
Just execute following commands in the root dir 👇
```
# build and run image
docker-compose up -d 
```
Then gallery api wil run on the  http://0.0.0.0:8000/
<br/>
You have to check documentation at first, just follow this url 
http://0.0.0.0:8000/docs
<br/>

# Post scriptum
To get access to the admins urls you have to create new superuser, you can do this if you run this command:

```
docker-compose exec web python manage.py createsuperuser
```


