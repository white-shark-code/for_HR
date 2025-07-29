from celery import Celery
from celery.schedules import crontab

from products.schemas import OnMainRootModel, RootModel
from services.services_celery import (
    database_write_update_not_main,
    database_write_update_on_main,
    prepare_celery_app,
    request_get_products_main_false,
    request_get_products_main_true,
)
from settings import cfg

app: Celery = prepare_celery_app()

@app.task
def download_products_on_main_true():
    try:
        response_json_bytes: bytes = request_get_products_main_true()
    except Exception as e:
        app.logger.error(e)

    try:
        new: OnMainRootModel = OnMainRootModel.model_validate_json(
            json_data=response_json_bytes,
            by_alias=True
        )

    except Exception as e:
        app.logger.error(e)

    app.logger.info('JSON readed and finish validation')

    database_write_update_on_main(new)

    app.logger.info('All JSON\'s objects successful added')

    return True

@app.task
def download_products_on_main_false():
    try:
        response_json_bytes: bytes = request_get_products_main_false()
    except Exception as e:
        app.logger.error(e)
        raise e

    try:
        new: RootModel = RootModel.model_validate_json(
            json_data=response_json_bytes,
            by_alias=True
        )

    except Exception as e:
        app.logger.error(e)
        raise e


    app.logger.info('JSON readed and finish validation')

    database_write_update_not_main(new)

    app.logger.info('All JSON\'s objects successful added')

    return True

app.conf.beat_schedule = {
    'download_products_on_main_true': {
        'task': 'celery_app.download_products_on_main_true',
        'schedule': crontab(hour=cfg.UPDATE_HOURS),
    },
    'download_products_on_main_false': {
        'task': 'celery_app.download_products_on_main_false',
        'schedule': crontab(hour=(cfg.UPDATE_HOURS)),
    }
}

download_products_on_main_true.delay()
download_products_on_main_false.delay()
