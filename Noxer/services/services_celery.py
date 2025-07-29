from atexit import register
from sys import stderr
from typing import Any, TypeVar

from celery import Celery
from httpx import Client, Response
from httpx._exceptions import HTTPStatusError
from loguru._defaults import LOGURU_AUTOINIT
from loguru._logger import Core, Logger
from sqlalchemy import IteratorResult, Select, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.orm.collections import InstrumentedList

from database import sync_session_maker
from products.models import (
    Category,
    Color,
    ExcludedItem,
    Extra,
    Image,
    ImportanceNum,
    Parameter,
    Product,
    ProductMark,
    Review,
    ReviewVideo,
    Tag,
)
from products.schemas import OnMainRootModel, RootModel
from products.schemas import Product as sc_Product
from settings import cfg

logger: Logger = Logger(
    core=Core(),
    exception=None,
    depth=0,
    record=False,
    lazy=False,
    colors=False,
    raw=False,
    capture=True,
    patchers=[],
    extra={}
)

@logger.catch
def request_get_products_main_true() -> dict[str, Any]:
    response: Response = Client().get(
        url='https://bot-igor.ru/api/products?on_main=true',
        headers={
            'Accept': 'application/json'
        }
    )

    if not response.status_code == 200:
        HTTPStatusError('wrong status code')

    return response.content

@logger.catch
def request_get_products_main_false() -> dict[str, Any]:
    response: Response = Client().get(
        url='https://bot-igor.ru/api/products?on_main=false',
        headers={
            'Accept': 'application/json'
        }
    )

    if not response.status_code == 200:
        HTTPStatusError('wrong status code')

    return response.content

def prepare_celery_app() -> Celery:

    level: str = 'DEBUG' if cfg.DEBUG else 'INFO'

    if LOGURU_AUTOINIT and stderr:
        logger.add(sink=stderr, level=level, enqueue=True)

    logger.add(
        sink='celery.log',
        level=level,
        format='{time} {level} {message}',
        enqueue=True
    )

    register(logger.remove)

    app: Celery = Celery(
        main='celery_app',
        broker=cfg.REDIS_URL
    )

    app.logger: Logger = logger

    return app

AlchemyEntity: TypeVar = TypeVar('AlchemyEntity')
PydanticEntity: TypeVar = TypeVar('PydanticEntity')

"""
    Была использована функция, т.к. она нужна один раз для этого
    задания и для этой ручки, эту пробему можно было бы решить
    через классы адаптеры
"""
def update_or_create_product_entity(
    session: Session,
    table_cls: AlchemyEntity,
    model_obj: PydanticEntity | str
) -> AlchemyEntity | None:
    try:

        try:
            ident: int = model_obj.id

            target_table_obj: AlchemyEntity = session.get_one(
                entity=table_cls,
                ident=ident
            )

            target_model_obj: PydanticEntity = model_obj.__class__.from_orm(
                target_table_obj
            )

            if target_model_obj != model_obj and not isinstance(model_obj, str):
                for attr_name, attr_value in model_obj.dict().items():
                    setattr(target_model_obj, attr_name, attr_value)
                    logger.debug(
                        f'At element {
                            target_model_obj.__repr__()
                        } attribute {attr_name} was changed to {attr_value}'
                    )

        except AttributeError as e:
            if not isinstance(model_obj, str) and not isinstance(table_cls, Tag):
                raise e
            # for Tags table model
            stmt: Select = select(table_cls).where(
                Tag.name == model_obj
            )

            target_result: IteratorResult = session.execute(
                statement=stmt
            )

            target_table_obj: AlchemyEntity = target_result.scalar_one()

    except NoResultFound:
        try:
            target_table_obj: AlchemyEntity = table_cls(**model_obj.dict())
        except AttributeError as e:
            if not isinstance(model_obj, str):
                raise e
            # for Tags table model
            target_table_obj: AlchemyEntity = table_cls(name=model_obj)
        session.add(
            target_table_obj,
        )

        logger.debug(
            f'Table object {target_table_obj.__repr__()} successful added'
        )

        return target_table_obj

    return None

def run_update_or_create_for_product_list_entitys(
    session: Session,
    root_table_obj: AlchemyEntity,
    name_attribute_root: str,
    table_cls: AlchemyEntity,
    list_model_obj: list[PydanticEntity | str] | None
):
    try:
        attributes: list[AlchemyEntity] = getattr(
            root_table_obj,
            name_attribute_root
        )

        try:
            ids_actual: list[int] = [model_obj.id for model_obj in list_model_obj]
        except AttributeError as e:
            if not isinstance(list_model_obj[0], str):
                raise e
            ids_actual: list[AlchemyEntity] = [
                attribute.id for attribute in attributes \
                    if attribute.name in list_model_obj
            ]

        for attribute in attributes:
            if attribute.id not in ids_actual:
                removed_attrivute: AlchemyEntity = attributes.pop(attribute)
                for_logger_str: str = list_model_obj[0].__class__.from_orm(
                    removed_attrivute
                ).__repr__()
                logger.debug(
                    f'Attribute {for_logger_str} was removed'
                )


        for model_obj_data in list_model_obj:

            new_table_obj: AlchemyEntity = update_or_create_product_entity(
                session=session,
                table_cls=table_cls,
                model_obj=model_obj_data
            )

            if not isinstance(attributes, InstrumentedList):
                raise TypeError(
                    f'{table_cls.__repr__}.{name_attribute_root} is not list'
                )

            if new_table_obj is not None:
                attributes.append(new_table_obj)

    except TypeError as e:
        if list_model_obj is not None:
            raise e

def create_or_update_product(
    session: Session,
    product_data: sc_Product
):
    try:
        product: Product = session.get_one(
            entity=Product,
            ident=product_data.id
        )

        logger.info(f'Product with id={product_data.id} finded')
        logger.debug(f'Product schema {product_data.__repr__()}')

        product: Product = session.get_one(
            entity=Product,
            ident=product_data.id,
            options=[
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
            ]
        )

        logger.debug(f'Product model {product.__repr__()} full loaded')
    except NoResultFound:
        product: Product = Product(
            id=product_data.id,
            created_at=product_data.created_at,
            on_main=product_data.on_main,
            name=product_data.name,
            updated_at=product_data.updated_at,
            moysklad_connector_products_data=product_data.moysklad_connector_products_data
        )
        session.add(product)

        logger.info(f'Product model {product.__repr__()} added in session')

    # if product.updated_at == product_data.updated_at:
    #     return

    # Create related entities and relationships
    # Categories
    run_update_or_create_for_product_list_entitys(
        session=session,
        root_table_obj=product,
        name_attribute_root='categories',
        table_cls=Category,
        list_model_obj=product_data.categories
    )

    logger.debug(f'Product(id={product.id}) categories succeseful readed')

    # ProductMark
    run_update_or_create_for_product_list_entitys(
        session=session,
        root_table_obj=product,
        name_attribute_root='marks',
        table_cls=ProductMark,
        list_model_obj=product_data.marks
    )

    logger.debug(f'Product(id={product.id}) marks succeseful readed')

    # Colors
    run_update_or_create_for_product_list_entitys(
        session=session,
        root_table_obj=product,
        name_attribute_root='colors',
        table_cls=Color,
        list_model_obj=product_data.colors
    )

    logger.debug(f'Product(id={product.id}) colors succeseful readed')

    # Extras
    run_update_or_create_for_product_list_entitys(
        session=session,
        root_table_obj=product,
        name_attribute_root='extras',
        table_cls=Extra,
        list_model_obj=product_data.extras
    )

    logger.debug(f'Product(id={product.id}) extras succeseful readed')

    # Images
    run_update_or_create_for_product_list_entitys(
        session=session,
        root_table_obj=product,
        name_attribute_root='images',
        table_cls=Image,
        list_model_obj=product_data.images
    )

    logger.debug(f'Product(id={product.id}) images succeseful readed')

    # Parameters
    run_update_or_create_for_product_list_entitys(
        session=session,
        root_table_obj=product,
        name_attribute_root='parameters',
        table_cls=Parameter,
        list_model_obj=product_data.parameters
    )

    logger.debug(f'Product(id={product.id}) parameters succeseful readed')

    # Reviews
    run_update_or_create_for_product_list_entitys(
        session=session,
        root_table_obj=product,
        name_attribute_root='reviews',
        table_cls=Review,
        list_model_obj=product_data.reviews
    )

    logger.debug(f'Product(id={product.id}) reviews succeseful readed')

    # Review Videos
    run_update_or_create_for_product_list_entitys(
        session=session,
        root_table_obj=product,
        name_attribute_root='reviews_video',
        table_cls=ReviewVideo,
        list_model_obj=product_data.reviews_video
    )

    logger.debug(f'Product(id={product.id}) reviews_video succeseful readed')

    # Excluded Items
    run_update_or_create_for_product_list_entitys(
        session=session,
        root_table_obj=product,
        name_attribute_root='excluded',
        table_cls=ExcludedItem,
        list_model_obj=product_data.excluded
    )

    logger.debug(f'Product(id={product.id}) excluded succeseful readed')

    # Importance Numbers
    run_update_or_create_for_product_list_entitys(
        session=session,
        root_table_obj=product,
        name_attribute_root='importance_num',
        table_cls=ImportanceNum,
        list_model_obj=product_data.importance_num
    )

    logger.debug(f'Product(id={product.id}) importance_num succeseful readed')

    # Tags
    run_update_or_create_for_product_list_entitys(
        session=session,
        root_table_obj=product,
        name_attribute_root='tags',
        table_cls=Tag,
        list_model_obj=product_data.tags
    )

    logger.debug(f'Product(id={product.id}) importance_num succeseful readed')

    session.commit()

    logger.info(f'Product(id={product.id}) succesesful update or added')

@logger.catch
def database_write_update_on_main(model: OnMainRootModel):
    session: Session = sync_session_maker()

    # Create or update products
    for product_data in model.products:
        create_or_update_product(session, product_data)

    session.commit()

@logger.catch
def database_write_update_not_main(model: RootModel):
    session: Session = sync_session_maker()

    # Create or update products
    for product_data in model.products:
        create_or_update_product(session, product_data)

    session.commit()
