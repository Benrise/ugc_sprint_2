import psycopg2
import typer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import pg, settings
from models.entity import User

DATABASE_URL = f'postgresql+psycopg2://{pg.user}:{pg.password}@{pg.host}:{pg.port}/{pg.db}'


engine = create_engine(DATABASE_URL, echo=settings.debug, future=True)
session_maker = sessionmaker(
    engine, expire_on_commit=False
)
session = session_maker()


def create_superuser(login: str, password: str):

    superuser = User(
        login=login,
        password=password,
        email='admind@sample.com',
        first_name='',
        last_name='',
    )

    superuser.role_id = 3

    session.add(superuser)
    session.commit()
    session.refresh(superuser)

    typer.echo(f'Superuser {login} created successfully')


if __name__ == '__main__':
    typer.run(create_superuser)
