from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.models import db, TemplateGroupLayer, Ingredient, IngredientConsistency

bp = Blueprint('template_group_layer', __name__, url_prefix='/template-group')


def get_template_group_layer(id):
    group = TemplateGroupLayer.query.filter_by(id=id).one_or_none()
    if group is None:
        abort(404, f"Такого шаблона с id={id} не существует.")
    return group


@bp.route('/')
@login_required
def index():

    groups = TemplateGroupLayer.query.all()
    return render_template('/template_group_layer/index.html', groups=groups)


@bp.route('/new-template-group', methods=('POST',))
@login_required
def new():

    if request.method == 'POST':
        name = request.form['input_name_group'].lower()
        error = None

        if TemplateGroupLayer.query.filter_by(name=name).one_or_none() is not None:
            error = f"Такая группа '{name}' уже есть."

        if error is None:

            group = TemplateGroupLayer(name=name)

            db.session.add(group)
            db.session.commit()

            return redirect(url_for('template_group_layer.index'))

        flash(error)
        return redirect(url_for('template_group_layer.index'))


@bp.route('/edit-template-group/<int:id>', methods=('POST', 'GET'))
@login_required
def edit_template(id):
    group = get_template_group_layer(id=id)
    ingredients = Ingredient.query.all()

    if request.method == 'POST':
        ingr_id = request.form['input_ingredient_id']
        ingr_con_qty = request.form['input_ingredient_qty'].replace(',', '.')
        error = None

        ingredient = Ingredient.query.filter_by(id=ingr_id).one_or_none()
        try:
            ingr_con_qty = float(ingr_con_qty)
        except Exception:
            error = f"Не корректно введено кол-во '{ingr_con_qty}'."

        if error is None:
            ingr_con = IngredientConsistency(
                ingredient=ingredient,
                qty=ingr_con_qty,
            )
            db.session.add(ingr_con)

            group.ingredient_consistency.append(ingr_con)
            db.session.commit()
            return redirect(url_for('template_group_layer.edit_template', id=id))
        flash(error)

    return render_template('/template_group_layer/update.html', group=group, ingredients=ingredients)


@bp.route('/del-ing-cons-from-template-group-<int:template_id>/<int:ing_id>', methods=('GET',))
@login_required
def del_ing_from_template(template_id, ing_id):
    ing_cons = IngredientConsistency.query.filter_by(id=ing_id).one_or_none()
    template_group = TemplateGroupLayer.query.filter_by(id=template_id).one_or_none()
    if ing_cons is None:
        flash(f"Такого {id} ингредиента нет.")
    else:
        template_group.ingredient_consistency.remove(ing_cons)
        db.session.delete(ing_cons)
        db.session.commit()
    return redirect(url_for('template_group_layer.edit_template', id=template_id))


@bp.route('/delete-template-group/<int:id>', methods=('GET', ))
@login_required
def delete_template(id):
    template_group = TemplateGroupLayer.query.filter_by(id=id).one_or_none()
    if template_group is None:
        flash(f"Такого шаблона с id={id} нет.")
    else:
        db.session.delete(template_group)
        db.session.commit()
    return redirect(url_for('template_group_layer.index'))
