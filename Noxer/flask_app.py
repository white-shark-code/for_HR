from products.blueprint import products_bp
from services.tunned_flask import TunnedFlask

app: TunnedFlask = TunnedFlask(
    import_name = __name__
)

app.register_blueprint(blueprint=products_bp)
