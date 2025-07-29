from flask import Blueprint, current_app, render_template, request
from sqlalchemy import (
    ChunkedIteratorResult,
    Select,
    select,
)
from sqlalchemy.orm import aliased, joinedload
from sqlalchemy.orm.util import AliasedClass

from products.models import Category, Product, Tag
from products.schemas import ProductView

products_bp: Blueprint = Blueprint(
    name = 'products',
    import_name = __name__,
    url_prefix = '/info'
)

@products_bp.route("")
async def get_products_texted():
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 3, type=int)
    category_names = request.args.getlist('category_names', type=str)
    tags_ids = request.args.getlist('tags', type=int)

    async with current_app.get_async_session() as session:
        stmt: Select = select(Product).options(
            joinedload(Product.categories),
            joinedload(Product.marks),
            joinedload(Product.colors),
            joinedload(Product.excluded),
            joinedload(Product.images),
            joinedload(Product.importance_num),
            joinedload(Product.parameters),
            joinedload(Product.extras),
            joinedload(Product.reviews),
            joinedload(Product.reviews_video),
            joinedload(Product.tags)
        )

        if category_names:
            for category_name in category_names:
                category_alias: AliasedClass = aliased(Category, name=category_name)
                stmt = stmt.join(
                    Product.categories.of_type(category_alias),
                    isouter=False
                ).where(category_alias.name == category_name)

        if tags_ids:
            stmt = stmt.where(
                Product.tags.any(
                    Tag.id.in_(tags_ids)
                )
            )

        stmt = stmt.offset((page-1)*count).limit(count)

        result: ChunkedIteratorResult = await session.execute(stmt)

        products_orm: list[Product] = result.scalars().unique().all()

        products_sc: ProductView = [
            ProductView.from_orm(product) for product in products_orm
        ]

        return render_template(
            'all_info.html',
            title='All information',
            products=[product_sc.dict() for product_sc in products_sc]
        )
