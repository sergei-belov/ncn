from api.settings import get_settings
from libs.cp_common import Authorization, BaseServiceHub
from libs.cp_postgresql import PostgreSQL
from libs.cp_prometheus import PrometheusCollector


class Services(BaseServiceHub):
    """External services used by ncn-pms."""

    config = get_settings()
    collector = PrometheusCollector()
    auth = Authorization(
        flow=config.AUTH_FLOW,
        secret_key=config.AUTH_SECRET_KEY,
        algorythm=config.AUTH_ALGORITHM,
        login_url=config.AUTH_LOGIN_URL,
        expires_delta=config.AUTH_ACCESS_TOKEN_EXPIRE_SECONDS,
    )
    database = PostgreSQL(
        username=config.DB_USERNAME,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_DATABASE,
        echo_pool=config.DB_ECHO_POOL,
        pool_size=config.DB_POOL_SIZE,
        connection_retry_period_sec=config.DB_CONNECTION_RETRY_PERIOD_SEC,
        statement_timeout_sec=config.DB_STATEMENT_TIMEOUT_SEC,
    )
