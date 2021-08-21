from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
import datetime

metadata = MetaData(
    naming_convention={
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s'
    }
)
db = SQLAlchemy(metadata=metadata)

LAZY_LOAD = 'joined'


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String, unique=True, nullable=False)
    pswd = db.Column(db.String, nullable=False)
    uid = db.Column(db.String, nullable=False)


class File(db.Model):
    __tablename__ = 'file'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    belong = db.Column(db.String, nullable=False)

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))


class Measurement(db.Model):
    __tablename__ = 'measurement'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    # ratio = db.Column(db.Float, nullable=False, default=1)

    ingredient = db.relationship(
        'Ingredient',
        back_populates='measurement',
        lazy=LAZY_LOAD
    )

    def __repr__(self):
        return f'Measur: 1{self.name} = {self.ratio}г'


class Ingredient(db.Model):
    __tablename__ = 'ingredient'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False, default=0)
    packing = db.Column(db.Float, nullable=False, default=0)

    measurement_id = db.Column(db.Integer, db.ForeignKey('measurement.id'))
    measurement = db.relationship('Measurement', back_populates='ingredient', uselist=False)

    ingredient_consistency = db.relationship(
        'IngredientConsistency',
        back_populates='ingredient',
        lazy=LAZY_LOAD
    )

    def __repr__(self):
        return f'Ingredient: {self.name} {self.price} за {self.measurement.name}'


class IngredientConsistencyType(db.Model):
    __tablename__ = 'ingredient_consistency_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    diameter = db.Column(db.Float, nullable=False, default=18)

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))

    ingredient_consistency = db.relationship(
        'IngredientConsistency',
        back_populates='ingredient_type',
        lazy=LAZY_LOAD,
        cascade="all, delete, delete-orphan"
    )


# реализация Many to Many
association_table = db.Table('association',
                          db.Column('ingredient_consistency_id',
                                    db.Integer,
                                    db.ForeignKey('ingredient_consistency.id', ondelete="CASCADE")
                                    ),
                          db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id', ondelete="CASCADE"))
                          )


class IngredientConsistency(db.Model):
    __tablename__ = 'ingredient_consistency'

    id = db.Column(db.Integer, primary_key=True)
    # diameter = db.Column(db.Float, nullable=False, default=0)
    qty = db.Column(db.Float, nullable=False, default=0)

    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'))
    ingredient = db.relationship('Ingredient', back_populates='ingredient_consistency', uselist=False)

    ingredient_type_id = db.Column(db.Integer, db.ForeignKey('ingredient_consistency_type.id'))
    ingredient_type = db.relationship('IngredientConsistencyType', back_populates='ingredient_consistency', uselist=False)

    recipe = db.relationship(
        'Recipe',
        back_populates='composition',
        secondary=association_table,
        passive_deletes=True,
        # т.к. в Recipe relationship single_parent=True, то только одын родитель
        # если родителей будет больше, то каскадного удаления не получится
        uselist=False,
        lazy=LAZY_LOAD
    )

    def __repr__(self):
        return f'IngredientConc: {self.ingredient.name} {self.qty}{self.ingredient.measurement.name} = {self.qty * self.ingredient.price}'


class Recipe(db.Model):
    __tablename__ = 'recipe'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    text_about = db.Column(db.String, default='')
    text_recipe = db.Column(db.String, default='')
    # флаг готовности к продаже
    to_trade = db.Column(db.Boolean, nullable=False, default=False)
    # множитель выручки => qty*price*profit
    profit = db.Column(db.Float, nullable=False, default=2)
    update_date = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    ingredient_consistency_id = db.Column(db.Integer, db.ForeignKey('ingredient_consistency.id'))
    composition = db.relationship(
        'IngredientConsistency',
        back_populates='recipe',
        secondary=association_table,
        cascade="all, delete, delete-orphan",
        single_parent=True,
        lazy=LAZY_LOAD
    )

    files = db.relationship('File', backref='recipe', lazy=LAZY_LOAD, uselist=True)
    list_group = db.relationship('IngredientConsistencyType', backref='recipe', lazy=LAZY_LOAD, uselist=True)

    def __repr__(self):
        return f'Recipe: "{self.name}" composition: {self.composition}'


# Many to Many для TemplateGroupLayer и IngredientConsistency
association_table_template_group_layer = \
    db.Table('association_template_group_layer',
             db.Column('ingredient_consistency_id',
                       db.Integer,
                       db.ForeignKey('ingredient_consistency.id', ondelete="CASCADE")
                       ),
             db.Column('template_group_layer_id',
                       db.Integer,
                       db.ForeignKey('template_group_layer.id', ondelete="CASCADE")
                       )
             )


class TemplateGroupLayer(db.Model):
    __tablename__ = 'template_group_layer'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    ingredient_consistency = db.relationship(
        'IngredientConsistency',
        secondary=association_table_template_group_layer,
        lazy=LAZY_LOAD,
        cascade="all, delete"
    )
