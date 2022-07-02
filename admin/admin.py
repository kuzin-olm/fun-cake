import flask_admin as admin

from .views import AdminUserView, AdminRecipeView, AdminIngredientView, CakeAdminIndexView, AdminMeasurementView


admin = admin.Admin(
    name="AdminFunCake",
    template_mode='bootstrap4',
    index_view=CakeAdminIndexView(name='Home', url='/cakemylife')
)

admin.add_view(AdminUserView)
admin.add_view(AdminRecipeView)
admin.add_view(AdminIngredientView)
admin.add_view(AdminMeasurementView)
