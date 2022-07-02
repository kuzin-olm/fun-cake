from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView

from flaskr.models import User, db, Recipe, Ingredient, Measurement

from .mixins import AccessMixin


class CakeAdminIndexView(AccessMixin, AdminIndexView):
    ...


class UserView(AccessMixin, ModelView):
    page_size = 12
    can_create = False
    can_delete = False
    column_exclude_list = ["pswd", "uid"]
    column_editable_list = ["is_admin", ]
    form_excluded_columns = ["name", "pswd", "uid"]


class RecipeView(AccessMixin, ModelView):
    page_size = 4
    can_delete = False
    can_view_details = True
    column_searchable_list = ["name", "text_about", "text_recipe"]
    column_filters = ["to_trade", "profit"]
    column_editable_list = ["to_trade", "profit"]
    form_columns = ["name", "text_about", "text_recipe", "to_trade", "profit"]


class IngredientView(AccessMixin, ModelView):
    page_size = 12
    can_delete = False
    column_searchable_list = ["name"]
    column_filters = ["price"]
    column_editable_list = ["price"]
    column_list = ["name", "price", "packing", "measurement"]
    form_excluded_columns = ["ingredient_consistency"]


class MeasurementView(AccessMixin, ModelView):
    page_size = 12
    can_delete = False
    column_searchable_list = ["name"]
    column_editable_list = ["name"]
    form_excluded_columns = ["ingredient"]


AdminUserView = UserView(User, db.session, name="Пользователи")
AdminRecipeView = RecipeView(Recipe, db.session, name="Рецепты")
AdminIngredientView = IngredientView(Ingredient, db.session, name="Ингредиенты", endpoint="/ingts")
AdminMeasurementView = MeasurementView(Measurement, db.session, name="Ед.измерения", endpoint="/measure")
