# старт 

установить библиотеки
```
python -m pip install -r requirements.txt
or
pip install -r requirements.txt 
```
запустить
```
python wsgi.py
```
<a href="http://127.0.0.1:5000/">и открыть в браузере</a>

или в живую
<a href="https://fun-cake.ru/">fun-cake.ru</a>


## task

- [x] список рецептов и отображение внутри (разграничение по авторизации)
- [x] список ингредиентов с ценой и фасовкой
- [x] состав рецепта с учетом цены ингердинтов и кол-ва => себестоимость рецепта по кол-ву
- [x] пересчет ингрединтов (кол-ва и цены) для нового диаметра
- [x] список покупок для рецепта (с учетом фасовки)
- [x] шаблоны для слоев в рецепте
- [ ] оптимизация картинок при загрузке
- [ ] список заказчиков


### как это выглядит
![alt tag](screenshots/index_page.png "индексная страница")
![alt tag](screenshots/default_view_recipe.png "вид пользователю")
![alt tag](screenshots/view_recipe.png "вид кондитеру")
![alt tag](screenshots/ingredient_list_recipe.png "список ингредиентов по кол-ву")
![alt tag](screenshots/shopping.png "список покупок")
![alt tag](screenshots/new_ingredient.png "список ингредиентов")
![alt tag](screenshots/template_ingredient.png "список шаблонов")
![alt tag](screenshots/edit_recipe_ingredient.png "редактор слоев")
