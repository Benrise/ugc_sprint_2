from http import HTTPStatus
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from schemas.auth_request import AuthRequest
from schemas.role import RoleAction, RoleCreate, RoleDelete, RoleInDB
from schemas.user import UserRoles
from services.role import RoleService
from services.user import UserService

from dependencies.user import get_user_service
from dependencies.role import roles_required, get_role_service

from utils.enums import Roles


router = APIRouter()
auth_dep = AuthJWTBearer()


@router.get('/', response_model=list[RoleInDB], status_code=HTTPStatus.OK)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def get_roles(
    request: AuthRequest,
    role_service: RoleService = Depends(get_role_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> RoleInDB:
    await authorize.jwt_required()

    return await role_service.get_all_roles(db)


@router.post('/create', response_model=RoleInDB, status_code=HTTPStatus.CREATED)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def create_role(
    request: AuthRequest,
    role_create: RoleCreate,
    role_service: RoleService = Depends(get_role_service), 
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> RoleInDB:

    return await role_service.create_role(role_create, db)


@router.post('/asign', status_code=HTTPStatus.OK)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def asign_role(
    request: AuthRequest,
    data: RoleAction,
    role_service: RoleService = Depends(get_role_service),
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> dict:
    await authorize.jwt_required()

    user_to_asign = await user_service.get_user_by_id(data.user_id, db)
    if not user_to_asign:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    role_id = await role_service.role_validation(data.role_id, db)

    if user_to_asign.role_id == role_id:
        return {"detail": "User already has this role"}

    await role_service.add_role(user_to_asign, role_id, db)

    return {"detail": "Role successfully assigned"}


@router.patch('/revoke', status_code=HTTPStatus.OK)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def revoke_role(
    request: AuthRequest,
    user_id: UUID,
    role_service: RoleService = Depends(get_role_service),
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
) -> dict:
    await authorize.jwt_required()

    user_to_revoke = await user_service.get_user_by_id(user_id, db)
    if not user_to_revoke:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    if user_to_revoke.role_id == Roles.superuser.value:
        return {"detail": "Cannot revoke this role"}

    await role_service.revoke_role(user_to_revoke, db)
    return {"detail": "Role successfully revoked"}


@router.delete('/delete', status_code=HTTPStatus.OK)
@roles_required(roles_list=[UserRoles().admin, UserRoles().superuser])
async def delete_role(
    request: AuthRequest,
    data: RoleDelete,
    role_service: RoleService = Depends(get_role_service),
    db: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_dep)
):
    await authorize.jwt_required()

    role_id = await role_service.role_validation(data.role_id, db)
    
    await role_service.delete_role(role_id, db)
    return {"detail": "Role successfully deleted"}
