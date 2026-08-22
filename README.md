
--------
## Изменения от классики !!!!
--------

1. Нет слоняры и дельфина. Все на срерверной sqlite и duckdb
2. Не серевере делаем только migrate (не делаем makemigration) НО миграции делаем если вносили изменения в структуру DB
3. Теперь settings.py как и проект находится в папке manuf/config а не manuf/manuf 
4. Все максимально на UNFOLD. Заменяем admin на from unfold.admin !!! 
5. https://unfoldadmin.com/docs/ мануал
6. https://demo.unfoldadmin.com демка 
7. Важно !!! Это приложение ни в коем случае не заменяет Manu.db. Приложение только администрирует сайт. Аналитика через duckdb и dash. Договора, начисления и пр. ведем как вели. 
8. Все комманды по работе с данными теперь в приложении utils

--------
## Приводим нашу базу Manu к норм виду !!!!
--------

1. Удаляем view Comparison <Запрос битый гробит все>


---------
## Настраиваем окружение
---------
source .venv/bin/activate

touch .env
SOURCE_MANU=путь к базе данных manu без ковычек

mkdir manuf
git clone git@github.com:feb100281/manuf.git .
python3.12 -m venv .venv  
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

brew install sshpass !!!!! НУЖНО

pip freeze > requirements.txt   

https://fonts.google.com/icons


unzip Договоры_аренды.zip

sudo systemctl restart gunicorn-manuf

PDF оптимизируем

brew install ghostscript на мак
sudo apt install ghostscript на сервер

/Users/pavelustenko/pr
/Users/pavelustenko/Library/CloudStorage/Dropbox/Remark_app/Manu.db