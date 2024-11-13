from datetime import datetime

import ydb
import ydb.iam
from ydb import SessionPool


from config_data import settings, credentials
from schemas import Prediction

path = settings.YDB_DATABASE + '/ynyb/predictions/'


def add_predictions(_pool: SessionPool, predictions: list[Prediction]):
    global path

    def callee(session):
        query_insert = """
        PRAGMA TablePathPrefix("{}");
        INSERT INTO predictions (id, author_tg_user_id, author_staff_login, accepted, dttm_created, text)
        VALUES ({}, {}, "{}", {}, Datetime("2009-02-14T02:31:00Z"), "{}");
        """

        query_select = """
        PRAGMA TablePathPrefix("{}");
        SELECT MAX(id) as current_id FROM predictions;
        """.format(path)

        with session.transaction() as tx:
            current_id = tx.execute(query_select)[0].rows[0]['current_id'] + 1
            for _id, prediction in enumerate(predictions, start=current_id):
                tx.execute(
                    query_insert.format(
                        path,
                        _id,
                        prediction.author_tg_user_id,
                        prediction.author_staff_login,
                        prediction.accepted,
                        prediction.text,
                    ),
                    commit_tx=True
                )

    return _pool.retry_operation_sync(callee)


p = Prediction(
    author_tg_user_id=123,
    author_staff_login='staff_login',
    dttm_created=datetime.now(),
    text='Some prediction text',
)

with ydb.Driver(
    endpoint=settings.YDB_ENDPOINT,
    database=settings.YDB_DATABASE,
    credentials=credentials,
) as driver:
    driver.wait(timeout=5, fail_fast=True)
    with ydb.SessionPool(driver) as pool:
        result_sets = add_predictions(pool, [p])
        print(result_sets)
