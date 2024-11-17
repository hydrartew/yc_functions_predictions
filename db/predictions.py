import logging
from typing import Any

from faker import Faker
import ydb
import ydb.iam

from config_data import settings, credentials
from schemas import Prediction

logger = logging.getLogger('predictions')


full_path: str = '{}/ynyb/predictions/'.format(settings.YDB_DATABASE.removeprefix('/'))
table_name: str = 'predictions'


def __create_table_predictions_if_not_exists(_pool) -> None:
    global full_path, table_name

    def callee(session) -> None:
        logger.info(f"Create table if not exists: {full_path}{table_name}")
        session.execute_scheme(
            """
            PRAGMA TablePathPrefix("{}");
            CREATE TABLE IF NOT EXISTS `{}` (
                `prediction_id` Uint32 NOT NULL,
                `accepted` Bool NOT NULL,
                `author_tg_user_id` Uint64 NOT NULL,
                `author_staff_login` Utf8 NOT NULL,
                `dttm_created` Timestamp NOT NULL,
                `dttm_last_usage` Timestamp,
                `text` Utf8 NOT NULL,
                `issue_key` Utf8,
                PRIMARY KEY (`prediction_id`)
            )
            """.format(
                full_path, table_name
            )
        )

    return _pool.retry_operation_sync(callee)


def __bulk_upsert(table_client, list_predictions: list[Prediction]) -> Any | None:
    global full_path, table_name
    logger.info(f"Start bulk upsert {table_name} with {[p.issue_key for p in list_predictions]}")
    column_types = (
        ydb.BulkUpsertColumns()
        .add_column("prediction_id", ydb.OptionalType(ydb.PrimitiveType.Uint32))
        .add_column("accepted", ydb.OptionalType(ydb.PrimitiveType.Bool))
        .add_column("author_tg_user_id", ydb.OptionalType(ydb.PrimitiveType.Uint64))
        .add_column("author_staff_login", ydb.OptionalType(ydb.PrimitiveType.Utf8))
        .add_column("dttm_created", ydb.OptionalType(ydb.PrimitiveType.Timestamp))
        .add_column("dttm_last_usage", ydb.OptionalType(ydb.PrimitiveType.Timestamp))
        .add_column("text", ydb.OptionalType(ydb.PrimitiveType.Utf8))
        .add_column("issue_key", ydb.OptionalType(ydb.PrimitiveType.Utf8))
    )
    operation = None
    try:
        operation = table_client.bulk_upsert(
            '{}{}'.format(full_path, table_name),
            list_predictions,
            column_types
        )
        if operation is not None:
            logger.info(f"Bulk upsert was completed successfully!")
        else:
            logger.error(f"Bulk upsert failed with list_predictions: {list_predictions}")
    except Exception as err:
        logger.critical(f"Error during bulk upsert: {err}", exc_info=True)
    return operation


def __select_max_prediction_id(_pool) -> int:
    global full_path, table_name

    def callee(session) -> int:
        logger.info(f"Getting MAX prediction_id of the table: {full_path}{table_name}")
        max_prediction_id = session.transaction(ydb.SerializableReadWrite()).execute(
            """
            PRAGMA TablePathPrefix("{}");
            SELECT MAX(prediction_id) as max_prediction_id FROM {};
            """.format(
                full_path, table_name
            ),
            commit_tx=True,
        )[0].rows[0].max_prediction_id

        if max_prediction_id is None:
            max_prediction_id = 0

        logger.info(f"max_prediction_id is received: {max_prediction_id}")
        return max_prediction_id

    return _pool.retry_operation_sync(callee)


def get_max_prediction_id() -> int:
    with ydb.Driver(
        endpoint=settings.YDB_ENDPOINT,
        database=settings.YDB_DATABASE,
        credentials=credentials,
    ) as driver:
        driver.wait(timeout=5, fail_fast=True)
        with ydb.SessionPool(driver) as pool:
            return __select_max_prediction_id(pool)


def add_list_predictions(list_predictions: list[Prediction]) -> Any | None:
    with ydb.Driver(
        endpoint=settings.YDB_ENDPOINT,
        database=settings.YDB_DATABASE,
        credentials=credentials,
    ) as driver:
        driver.wait(timeout=5, fail_fast=True)
        return __bulk_upsert(driver.table_client, list_predictions)


def create_table_predictions():
    with ydb.Driver(
        endpoint=settings.YDB_ENDPOINT,
        database=settings.YDB_DATABASE,
        credentials=credentials,
    ) as driver:
        driver.wait(timeout=5, fail_fast=True)
        with ydb.SessionPool(driver) as pool:
            __create_table_predictions_if_not_exists(pool)


def fill_test_data():
    global table_name
    table_name = 'test_predictions'

    fake = Faker()

    _list_predictions = []

    for prediction_id in range(40_000):
        _list_predictions.append(
            Prediction(
                prediction_id=prediction_id,
                author_staff_login=fake.user_name(),
                dttm_created=fake.date_time(),
                text=fake.text(256),
                issue_key=fake.text(10)
            )
        )

    with ydb.Driver(
        endpoint=settings.YDB_ENDPOINT,
        database=settings.YDB_DATABASE,
        credentials=credentials,
    ) as driver:
        driver.wait(timeout=5, fail_fast=True)
        with ydb.SessionPool(driver) as pool:
            __create_table_predictions_if_not_exists(pool)
            add_list_predictions(_list_predictions)
