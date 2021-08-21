# from flaskr.models import db, Ingredient
# from sqlalchemy import DDL, event
#
# trigger_ingredient_upd_price_ingredient_consistency = \
#         "create trigger ingredient_upd_price_ingredient_consistency " \
#         "after update on ingredient " \
#         "begin" \
#         "update ingredient_consistency " \
#         "set price = round(new.price / new.packing * qty, 2) " \
#         "from ingredient " \
#         "where ingredient_id = new.id;" \
#         "end;"
# ddl_trigger_ingredient = DDL(trigger_ingredient_upd_price_ingredient_consistency)
#
# # after call db.init_app(app)
# def init_event():
#     event.listen(Ingredient, 'after_update', ddl_trigger_ingredient)
#
