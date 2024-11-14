from datetime import datetime

import ydb
import ydb.iam

from config_data import settings, credentials
from schemas import Prediction

full_path: str = '{}/ynyb/predictions/'.format(settings.YDB_DATABASE.removeprefix('/'))
table_name: str = 'predictions'


def test_predictions_for_bulk_upsert():
    return [
        Prediction(
            prediction_id=3,
            dttm_created=datetime.now(),
            text='test prediction 1'
        )
    ]


def create_table_predictions_if_not_exists(_pool) -> None:
    global full_path, table_name

    def callee(session) -> None:
        print(f"> create_table: {full_path}{table_name}")
        session.execute_scheme(
            """
                PRAGMA TablePathPrefix("{}");
                CREATE TABLE IF NOT EXISTS `{}` (
                    `prediction_id` Uint16 NOT NULL,
                    `accepted` Bool NOT NULL,
                    `author_tg_user_id` Uint64 NOT NULL,
                    `author_staff_login` Utf8 NOT NULL,
                    `dttm_created` Timestamp NOT NULL,
                    `dttm_last_usage` Timestamp,
                    `text` Utf8 NOT NULL,
                    PRIMARY KEY (`prediction_id`)
                )
                """.format(
                full_path, table_name
            )
        )

    return _pool.retry_operation_sync(callee)


def bulk_upsert(table_client):
    global full_path, table_name
    column_types = (
        ydb.BulkUpsertColumns()
        .add_column("prediction_id", ydb.OptionalType(ydb.PrimitiveType.Uint16))
        .add_column("accepted", ydb.OptionalType(ydb.PrimitiveType.Bool))
        .add_column("author_tg_user_id", ydb.OptionalType(ydb.PrimitiveType.Uint64))
        .add_column("author_staff_login", ydb.OptionalType(ydb.PrimitiveType.Utf8))
        .add_column("dttm_created", ydb.OptionalType(ydb.PrimitiveType.Timestamp))
        .add_column("dttm_last_usage", ydb.OptionalType(ydb.PrimitiveType.Timestamp))
        .add_column("text", ydb.OptionalType(ydb.PrimitiveType.Utf8))
    )
    rows = test_predictions_for_bulk_upsert()
    table_client.bulk_upsert('{}{}'.format(full_path, table_name), rows, column_types)


with ydb.Driver(
        endpoint=settings.YDB_ENDPOINT,
        database=settings.YDB_DATABASE,
        credentials=credentials,
) as driver:
    driver.wait(timeout=5, fail_fast=True)
    with ydb.SessionPool(driver) as pool:
        create_table_predictions_if_not_exists(pool)
        bulk_upsert(driver.table_client)
