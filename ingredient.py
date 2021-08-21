import os
import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.models import db, Ingredient, Measurement, Recipe, IngredientConsistency, IngredientConsistencyType

bp = Blueprint('ingredient', __name__, url_prefix='/ingredient')


@bp.route('/')
@login_required
def index():

    ingredients = Ingredient.query.order_by(Ingredient.name).all()
    measurement = Measurement.query.order_by(Measurement.name).all()

    return render_template('/ingredient/index.html', ingredients=ingredients, measurement=measurement)


@bp.route('/newingredient', methods=('POST',))
@login_required
def newingredient():

    if request.method == 'POST':
        name = request.form['input_name']
        mass_id = int(request.form['input_mass'])
        price = request.form['input_price'].replace(',', '.')
        packing = request.form['input_packing'].replace(',', '.')

        error = None

        if Ingredient.query.filter_by(name=name).one_or_none() is not None:
            error = f"Ингредиент '{name}' уже есть."

        try:
            price = float(price)
        except Exception:
            error = f"В поле Цена '{price}' введено неверно."

        try:
            packing = float(packing)
        except Exception:
            error = f"В поле Фасовка '{packing}' введено неверно."

        if error is None:

            measure = Measurement.query.filter_by(id=mass_id).one_or_none()
            ingr = Ingredient(name=name.lower(), price=price, measurement=measure, packing=packing)

            db.session.add(ingr)
            db.session.commit()

            return redirect(url_for('ingredient.index'))

        flash(error)
        return redirect(url_for('ingredient.index'))


def get_ingredient(id):
    ingredient = Ingredient.query.filter_by(id=id).one_or_none()

    if ingredient is None:
        abort(404, f"Ингредиента с id={id} не существует.")

    return ingredient


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    ingredient = get_ingredient(id)
    measurement = Measurement.query.all()

    if request.method == 'POST':
        name = request.form['input_name']
        mass_id = int(request.form['input_mass'])
        price = request.form['input_price'].replace(',', '.')
        packing = request.form['input_packing'].replace(',', '.')

        error = None

        try:
            price = float(price)
        except Exception:
            error = f"В поле Цена '{price}' введено неверно."

        try:
            packing = float(packing)
        except Exception:
            error = f"В поле Фасовка '{packing}' введено неверно."

        if error is None:
            ingredient.name = name.lower()
            ingredient.price = price
            ingredient.packing = packing

            measure = Measurement.query.filter_by(id=mass_id).one_or_none()
            ingredient.measurement = measure

            db.session.add(ingredient)
            db.session.commit()
            return redirect(url_for('ingredient.index'))

        flash(error)
        return render_template('/ingredient/update.html', ingredient=ingredient, measurement=measurement)

    return render_template('/ingredient/update.html', ingredient=ingredient, measurement=measurement)


@bp.route('/<int:id>/delete')
@login_required
def delete(id):
    ingredient = get_ingredient(id)
    error = None

    ingredient_consistency = ingredient.ingredient_consistency
    if len(ingredient_consistency) > 0:
        # TODO прицепить шаблоны потом к консистенциям и выводить имя шаблона, а пока пришлепка "if ing_con.recipe"
        recipes = set([ing_con.recipe for ing_con in ingredient_consistency if ing_con.recipe])
        str_recipes = '<br> '.join(['- '+recipe.name for recipe in recipes])
        error = f'Ингредиент "{ingredient.name}" используется в: <br>{str_recipes}'

    if error is None:
        db.session.delete(ingredient)
        db.session.commit()
        return redirect(url_for('ingredient.index'))
    flash(error)
    return redirect(url_for('ingredient.index'))


@bp.route('/newmass', methods=('POST',))
@login_required
def newmass():

    if request.method == 'POST':

        name = request.form['input_name_mass']

        error = None

        if Measurement.query.filter_by(name=name).one_or_none() is not None:
            error = f"Такая единица измерения '{name}' уже есть."

        if error is None:
            measure = Measurement(name=name)
            db.session.add(measure)
            db.session.commit()

            return redirect(url_for('ingredient.index'))

        flash(error)
        return redirect(request.referrer)


def get_recipe(id):
    recipe = Recipe.query.filter_by(id=id).one_or_none()

    if recipe is None:
        abort(404, f"Рецепта с id={id} не существует.")

    return recipe


@bp.route('/recipe-<int:recipe_id>-group-<int:group_id>/newconsistency', methods=('GET', 'POST'))
@login_required
def newconsistency(recipe_id, group_id):

    recipe = get_recipe(recipe_id)
    ingredients = Ingredient.query.all()
    ingredient_types = IngredientConsistencyType.query.filter_by(recipe_id=recipe.id)

    if request.method == 'POST':

        ingr_id = request.form['input_ingredient_id']
        ingredient_type_id = request.form.get('input_ingredient_type_id')
        ingredient_type_id = group_id if ingredient_type_id is None else ingredient_type_id

        ingr = get_ingredient(ingr_id)
        ingredient_type = IngredientConsistencyType.query.filter_by(id=int(ingredient_type_id)).one_or_none()
        ingr_con_qty = request.form['input_ingredient_qty'].replace(',', '.')

        error = None
        if ingredient_type is None:
            error = f'Такой группы ингредиента не найдно.'

        try:
            ingr_con_qty = float(ingr_con_qty)
        except Exception:
            error = f"Не корректно введено кол-во '{ingr_con_qty}'."

        if error is None:
            ingr_con = IngredientConsistency(
                ingredient=ingr,
                qty=ingr_con_qty,
                ingredient_type=ingredient_type
            )
            db.session.add(ingr_con)

            recipe.composition.append(ingr_con)

            db.session.commit()
            return redirect(url_for('blog.update', id=recipe.id, _anchor=f'group-layer-{ingredient_type_id}'))

        flash(error)

    return render_template(
        '/ingredient/create_consistency.html',
        ingredients=ingredients,
        recipe_id=recipe_id,
        ingredient_types=ingredient_types,
        group_id=group_id
    )


@bp.route('/recipe-<int:recipe_id>-ingr-con-<int:ingr_con_id>/delconsistency', methods=('GET', 'POST'))
@login_required
def delconsistency(recipe_id, ingr_con_id):
    recipe = get_recipe(recipe_id)
    ingr_con = IngredientConsistency.query.filter_by(id=ingr_con_id).one_or_none()

    ingredient_type = IngredientConsistencyType.query.filter_by(id=ingr_con.ingredient_type_id).one_or_none()

    if ingr_con in recipe.composition:
        recipe.composition.remove(ingr_con)
        db.session.commit()

    return redirect(url_for('blog.update', id=recipe_id, _anchor=f'group-layer-{ingredient_type.id}'))


@bp.route('/recipe-<int:recipe_id>-ingr-con-<int:ingr_con_id>/editconsistency', methods=('GET', 'POST'))
@login_required
def editconsistency(recipe_id, ingr_con_id):
    recipe = get_recipe(recipe_id)
    ingr_con = IngredientConsistency.query.filter_by(id=ingr_con_id).one_or_none()
    ingredients = Ingredient.query.all()
    ingredient_types = IngredientConsistencyType.query.filter_by(recipe_id=recipe.id)

    if request.method == 'POST':
        ingr_id = request.form['input_ingredient_id']
        ingredient_type_id = request.form['input_ingredient_type_id']

        ingr = get_ingredient(ingr_id)
        ingredient_type = IngredientConsistencyType.query.filter_by(id=int(ingredient_type_id)).one_or_none()
        ingr_con_qty = request.form['input_ingredient_qty'].replace(',', '.')


        error = None
        if ingredient_type is None:
            error = f'Такой группы ингредиента не найдно.'

        try:
            ingr_con_qty = float(ingr_con_qty)
        except Exception:
            error = f"Не корректно введено кол-во '{ingr_con_qty}'."

        if error is None:
            ingr_con.ingredient = ingr
            ingr_con.qty = ingr_con_qty
            ingr_con.ingredient_type = ingredient_type
            db.session.add(ingr_con)

            db.session.commit()
            return redirect(url_for('blog.update', id=recipe.id, _anchor=f'group-layer-{ingredient_type_id}'))

        flash(error)

    return render_template(
        '/ingredient/update_consistency.html',
        ingredients=ingredients,
        recipe=recipe,
        ingr_con=ingr_con,
        ingredient_types=ingredient_types
    )
