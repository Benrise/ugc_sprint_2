import typer
from core.config import pg, settings
from models.entity import Role
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = f'postgresql+psycopg2://{pg.user}:{pg.password}@{pg.host}:{pg.port}/{pg.db}'


engine = create_engine(DATABASE_URL, echo=settings.debug, future=True)
session_maker = sessionmaker(
    engine, expire_on_commit=False
)
session = session_maker()


def create_superuser():
    roles = ['guest', 'admin', 'superuser']
    for role in roles:
        obj = Role(role=role)
        session.add(obj)
        session.commit()
    typer.echo('Roles created successfully')


if __name__ == '__main__':
    typer.run(create_superuser)
