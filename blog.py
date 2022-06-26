import os
import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from sqlalchemy.orm.session import make_transient
from sqlalchemy import desc

from flaskr.auth import login_required
from flaskr.models import db, Recipe, File, IngredientConsistencyType, TemplateGroupLayer
from flaskr.settings import STATIC_ROOT

from .services import resize_img


bp = Blueprint('blog', __name__, url_prefix='/cake')

FILES = 'files'
UPLOAD_PATH_FILES = os.path.abspath(os.path.join(STATIC_ROOT, FILES))

if not os.path.exists(UPLOAD_PATH_FILES):
    os.makedirs(UPLOAD_PATH_FILES)


def save_file(file, save_to, key):
    date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    if file.filename != '':
        filename_now = f'{date}_{file.filename}'

        path_to_save = os.path.join(save_to, filename_now)
        file.save(path_to_save)

        try:
            extension = path_to_save.split(".")[-1]

            if extension.lower() in ("png", "jpg", "jpeg",):
                resize_img(image_path=path_to_save, max_width=1280, max_height=1280)
        except Exception:
            pass

        return File(name=filename_now, belong=key)
    return None


def save_files(files, parent, save_to, key):
    for file in files:
        file = save_file(file=file, save_to=save_to, key=key)
        if file:
            parent.append(file)


def delete_file(file):
    try:
        os.remove(os.path.join(UPLOAD_PATH_FILES, file.name))
    except Exception:  # FileNotFoundError
        pass


def delete_files(from_recipe, key=None):
    if key is None:
        file_to_del = from_recipe.files
    else:
        file_to_del = [file for file in from_recipe.files if file.belong == key]

    for file in file_to_del:
        delete_file(file)
        from_recipe.files.remove(file)
        db.session.delete(file)


def get_recipe(id, check_author=False):
    recipe = Recipe.query.filter_by(id=id).one_or_none()

    if recipe is None or (not recipe.to_trade and not g.user):
        abort(404, f"Такой рецепт с id={id} не существует.")

    # if check_author and recipe['author_id'] != g.user['id']:
    #     abort(403)

    return recipe


@bp.route('/')
def index():

    if g.user:
        recipes = Recipe.query.order_by(desc(Recipe.id)).all()
    else:
        recipes = Recipe.query.order_by(desc(Recipe.id)).filter(Recipe.to_trade).all()

    if len(recipes) != 0:

        prew_images = []
        for recipe in recipes:
            prew_image = [file.name for file in recipe.files if file.belong == 'prew_image']
            if len(prew_image) != 0:
                prew_image = url_for('static', filename=f'{FILES}/{prew_image[0]}')
            else:
                # дефолтная картинка, если не установлена иная
                prew_image = url_for('static', filename='imgs/cake_logo.png')
            prew_images.append(prew_image)

        recipes = zip(recipes, prew_images)
    else:
        recipes = None
    return render_template('/blog/index.html', recipes=recipes)


@bp.route('/<int:id>', methods=('GET',))
def view(id):
    recipe = get_recipe(id)

    other_images = [url_for('static', filename=f'{FILES}/{file.name}') for file in recipe.files if
                    file.belong == 'other_image']

    docs_file = [(url_for('static', filename=f'{FILES}/{file.name}'), file.name.split('_')[-1]) for file in recipe.files
                 if file.belong == 'docs_file']

    return render_template('blog/view_recipe.html', recipe=recipe, other_images=other_images, docs_file=docs_file)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        about = request.form['about']
        to_trade = bool(int(request.form['to_trade']))

        profit = request.form['profit'].replace(',', '.')

        prew_images = request.files.getlist('prew_image')
        other_images = request.files.getlist('other_image')
        docs_file = request.files.getlist('docs_file')

        error = None

        if not title:
            error = 'Title is required.'

        try:
            profit = float(profit)
        except Exception:
            error = f'Не корректно введен профит с продажи {profit}.'

        if error is not None:
            flash(error)
        else:
            # now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')

            recipe = Recipe(
                name=title,
                text_recipe=body,
                text_about=about,
                to_trade=to_trade,
                profit=profit,
                files=list(),
                update_date=datetime.datetime.now(datetime.timezone.utc)
            )

            # сохраняем превью рецепта
            save_files(files=prew_images, parent=recipe.files, save_to=UPLOAD_PATH_FILES, key='prew_image')

            # сохраняем дополнительные фото
            save_files(files=other_images, parent=recipe.files, save_to=UPLOAD_PATH_FILES, key='other_image')

            # сохраняем документы текстовые
            save_files(files=docs_file, parent=recipe.files, save_to=UPLOAD_PATH_FILES, key='docs_file')

            db.session.add(recipe)
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    recipe = get_recipe(id)
    templates_group = TemplateGroupLayer.query.all()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        text_about = request.form['about']
        to_trade = bool(int(request.form['to_trade']))

        profit = request.form['profit'].replace(',', '.')

        prew_images = request.files.getlist('prew_image')
        other_images = request.files.getlist('other_image')
        docs_file = request.files.getlist('docs_file')

        error = None

        if not title:
            error = 'Title is required.'

        try:
            profit = float(profit)
        except Exception:
            error = f'Не корректно введен профит с продажи {profit}.'

        if error is not None:
            flash(error, 'danger')
        else:
            recipe.name = title
            recipe.text_recipe = body
            recipe.text_about = text_about
            recipe.profit = profit

            if recipe.to_trade != to_trade:
                recipe.to_trade = to_trade
                recipe.update_date = datetime.datetime.now(datetime.timezone.utc)

            check_filename = lambda file: file.filename != ''

            if any(filter(check_filename, prew_images)):
                delete_files(from_recipe=recipe, key='prew_image')
                # сохраняем превью рецепта
                save_files(files=prew_images, parent=recipe.files, save_to=UPLOAD_PATH_FILES, key='prew_image')

            if any(filter(check_filename, other_images)):
                delete_files(from_recipe=recipe, key='other_image')
                # сохраняем дополнительные фото
                save_files(files=other_images, parent=recipe.files, save_to=UPLOAD_PATH_FILES, key='other_image')

            if any(filter(check_filename, docs_file)):
                delete_files(from_recipe=recipe, key='docs_file')
                # сохраняем документы текстовые
                save_files(files=docs_file, parent=recipe.files, save_to=UPLOAD_PATH_FILES, key='docs_file')

            db.session.add(recipe)
            try:
                db.session.commit()
                flash('Изменения внесены :)', 'success')
            except:
                flash('Изменения НЕ внесены :(', 'danger')
            # return redirect(url_for('blog.view', id=recipe.id))
            return redirect(url_for('blog.update', id=recipe.id))

    return render_template('blog/update.html', recipe=recipe, templates_group=templates_group)


@bp.route('/<int:id>/delete')
@login_required
def delete(id):
    recipe = get_recipe(id)

    for file in recipe.files:
        delete_file(file)
        db.session.delete(file)

    db.session.delete(recipe)
    db.session.commit()
    return redirect(url_for('blog.index'))


@bp.route('/add-type-consistency', methods=('POST',))
@login_required
def add_type_consistency():
    if request.method == 'POST':
        recipe_id = int(request.form['recipe_id'])
        name = request.form['consistency_type_name']
        diameter = request.form['consistency_type_diameter'].replace(',', '.')
        template_group_id = int(request.form['input_template_group_id'])

        error = None

        recipe = Recipe.query.filter_by(id=recipe_id).one_or_none()
        if recipe is None:
            error = f'Рецепт с id = {recipe_id} не существует.'

        try:
            diameter = float(diameter)
        except Exception:
            error = f'Не корректно введен диаметр {diameter}.'

        if error is None:
            if template_group_id > 0:
                template_group = TemplateGroupLayer.query.filter_by(id=template_group_id).one_or_none()

                type_consistency = IngredientConsistencyType(name=name, diameter=diameter)
                db.session.add(type_consistency)

                ing_cons_list = [ing_cons for ing_cons in template_group.ingredient_consistency]
                # db.session.expunge(template_group)
                for ing_cons in ing_cons_list:
                    make_transient(ing_cons)
                    ing_cons.id = None
                    ing_cons.ingredient_type = type_consistency
                    recipe.composition.append(ing_cons)
                    db.session.add(ing_cons)

                recipe.list_group.append(type_consistency)
                db.session.commit()

            else:
                type_consistency = IngredientConsistencyType(name=name, diameter=diameter)
                recipe.list_group.append(type_consistency)
                db.session.add(type_consistency)
                db.session.commit()

            return redirect(url_for('blog.update', id=recipe_id, _anchor='composite_table'))

        flash(error)
        return redirect(url_for('blog.update', id=recipe_id))


@bp.route('/<int:recipe_id>-<int:group_id>/delete-type-consistency', methods=('GET', 'POST'))
@login_required
def delete_type_consistency(recipe_id, group_id):
    group = IngredientConsistencyType.query.filter_by(id=group_id).one_or_none()
    error = None

    if group is None:
        error = f'Такой группы нет.'

    if error is None:
        db.session.delete(group)
        db.session.commit()
        # return render_template('blog/update.html', recipe=recipe)
        return redirect(url_for('blog.update', id=recipe_id,  _anchor='composite_table'))
        # return redirect(request.referrer)
    flash(error)
    return redirect(url_for('blog.update', id=recipe_id))


@bp.route('/<int:recipe_id>-<int:group_id>/edit-type-consistency', methods=('GET', 'POST'))
@login_required
def edit_type_consistency(recipe_id, group_id):
    group = IngredientConsistencyType.query.filter_by(id=group_id).one_or_none()

    if request.method == 'POST':
        name = request.form['input_group_name']
        diameter = request.form['input_group_diameter'].replace(',', '.')
        error = None

        try:
            diameter = float(diameter)
        except Exception:
            error = f'Не корректно введен диаметр {diameter}.'

        if error is None:
            group.name = name
            group.diameter = diameter

            db.session.add(group)
            db.session.commit()
            return redirect(url_for('blog.update', id=recipe_id, _anchor=f'group-layer-{group_id}'))

        flash(error)
    return render_template('blog/update_group_layer.html', recipe_id=recipe_id, group=group)


@bp.route('/restruct-diameter-<int:id>', methods=('POST',))
@login_required
def restruct_diameter(id):
    recipe = get_recipe(id)

    docs_file = [(url_for('static', filename=f'{FILES}/{file.name}'), file.name.split('_')[-1]) for file in recipe.files
                 if file.belong == 'docs_file']

    error = None

    input_group_name = list(filter(lambda x: x.startswith('inputgroup-'), request.form))
    try:
        new_diameter = {name.split('-')[-1]: float(request.form[name].replace(',', '.')) for name in input_group_name}
        print(new_diameter)  # TODO в жинжу передаются только строки!?!??!
    except:
        error = 'Ошибка в новом диаметре.'

    if error is None:
        return render_template('blog/restruct_diameter.html',
                               recipe=recipe,
                               docs_file=docs_file,
                               new_diameter=new_diameter)

    flash(error, 'danger')
    return render_template('blog/restruct_diameter.html', recipe=recipe)
