import ydb.iam
from config_data import credentials, settings

driver = ydb.Driver(
    endpoint=settings.YDB_ENDPOINT,
    database=settings.YDB_DATABASE,
    credentials=credentials,
)
