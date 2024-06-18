### Что из себя представляет приложение?
Площадка для компьютерных/мобильных игр, которые создают студенты. Кстати, потом надо будет добавить категории для этих игр (мобильные/компьютерные и также какие операционки поддерживаются).  

В чем отличия от других похожих проектов? Современное решение, созданное на современном стеке. Плюс, это только тренировочный проект

### Какой стек используется?
Frontend - ...  
Backend - FastAPI, PostgreSQL, ELK(Elasticsearch, Logstash, Kafka)(WIP), Redis(WIP), Nginx(WIP)

CI/CD - Docker(WIP), Kubernetes(WIP)

### Как запустить backend?
1. Установи Python 3.12 (либо ниже, просто писал именно на этой версии, за остальные не ручаюсь)
2. Поставь виртуальное окружение (что-то типо локальной версии питона именно для этого проекта, нужно, чтобы не устанавливать все библиотеки в общую систему и держать все внутри одной папки)
3. Установи все необходимые библиотеки
```bash
pip install -r requirements.txt 
```
4. Запускаешь приложение
```bash
uvicorn backend.app.main:app --reload
```
5. В бразуере пишешь: `localhost:8000/docs` и изучаешь документацию по API, карта в фигме будет попозже
6. По желанию, можешь пользоваться Postman для запросов к API, если знаешь как

### Как запустить frontend?
Тут опиши мне всю инструкцию пж, сейчас знаю только как на JS написать скрипто, который в `<canvas>` рисует кружочки, которые следуют за курсором :3