from config import PostgresConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def new_session_maker(psql_config: PostgresConfig) -> sessionmaker[Session]:
    raw_url = "postgresql+psycopg2://{login}:{password}@{host}:{port}/{database}"
    database_uri = raw_url.format(
        login=psql_config.login,
        password=psql_config.password,
        host=psql_config.host,
        port=psql_config.port,
        database=psql_config.database,
    )
    engine = create_engine(
        database_uri,
        pool_size=15,
        max_overflow=15,
        connect_args={"connect_timeout": 5},
    )
    return sessionmaker(
        bind=engine,
        class_=Session,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
