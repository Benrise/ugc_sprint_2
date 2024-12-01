from enum import Enum


class Sort(str, Enum):
    asc = 'asc',
    desc = 'desc'


class Roles(str, Enum):
    guest = 1
    admin = 2
    superuser = 3
