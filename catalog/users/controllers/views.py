from typing import cast
from uuid import UUID

import msgspec
from dishka import FromDishka
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from main.infrastructure.sessions import CustomSession
from main.integrations import DishkaRequest, inject

from users.application.interactors import (
    ActivateUser,
    AuthenticateUser,
    ChangeEmail,
    ChangePassword,
    ChangeRole,
    ChangeUsername,
    DeleteUser,
    RegisterUser,
    RestoreUser,
    SuspendUser,
    UnsuspendUser,
    UserDTO,
)
from users.controllers.schemas import (
    UserAuthSchema,
    UserPasswordSchema,
    UserRegisterSchema,
    UserUpdateSchema,
)

from ..domain.entities import UserRole
from .schemas import UserRestoreSchema, UserRoleSchema, ValidationError


# --- REGISTER USER ---
@require_http_methods(["POST"])
@inject
def user_register_view(
    request: DishkaRequest,
    interactor: FromDishka[RegisterUser],
) -> JsonResponse:
    try:
        data = msgspec.json.decode(request.body)
        params = UserRegisterSchema.from_raw(data)
    except ValidationError as e:
        return JsonResponse(
            {
                "error": "Invalid data", 
                "field": e.field, 
                "message": e.message}, 
            status=400
        )

    user = interactor.execute(params.username, params.email, params.password)
    return JsonResponse(
        msgspec.json.encode(user), 
        content_type="application/json", 
        status=201
    )


# --- AUTHENTICATE USER ---
@require_http_methods(["POST"])
@inject
def user_auth_view(
    request: DishkaRequest,
    interactor: FromDishka[AuthenticateUser],
) -> JsonResponse:
    try:
        data = msgspec.json.decode(request.body)
        params = UserAuthSchema.from_raw(data)
    except ValidationError as e:
        return JsonResponse(
            {
                "error": "Invalid data", 
                "field": e.field, 
                "message": e.message
            }, 
            status=400
        )

    user = interactor.execute(params.username, params.email, params.password)
    return JsonResponse(msgspec.json.encode(user), content_type="application/json")


# --- ACTIVATE USER ---
@require_http_methods(["POST"])
@inject
def user_activate_view(
    request: DishkaRequest,
    interactor: FromDishka[ActivateUser],
) -> JsonResponse:
    session_data = cast(CustomSession, request.session)
    user = interactor.execute(session_data.user_id)
    return JsonResponse(msgspec.json.encode(user), content_type="application/json")


# --- SUSPEND USER ---
@require_http_methods(["POST"])
@inject
def user_suspend_view(
    request: DishkaRequest,
    interactor: FromDishka[SuspendUser],
    target_username: str
) -> HttpResponse:
    session_data = cast(CustomSession, request.session)
    user = interactor.execute(session_data.user_id, target_username)
    return HttpResponse(msgspec.json.encode(user), content_type="application/json")


# --- UNSUSPEND USER ---
@require_http_methods(["POST"])
@inject
def user_unsuspend_view(
    request: DishkaRequest,
    interactor: FromDishka[UnsuspendUser],
    target_username: str
) -> JsonResponse:
    session_data = cast(CustomSession, request.session)
    user = interactor.execute(session_data.user_id, target_username)
    return JsonResponse(msgspec.json.encode(user), content_type="application/json")


# --- DELETE USER ---
@require_http_methods(["POST"])
@inject
def user_delete_view(
    request: DishkaRequest,
    interactor: FromDishka[DeleteUser],
) -> JsonResponse:
    session_data = cast(CustomSession, request.session)
    user = interactor.execute(session_data.user_id)
    return JsonResponse(msgspec.json.encode(user), content_type="application/json")


# --- RESTORE USER ---
@require_http_methods(["POST"])
@inject
def user_restore_view(
    request: DishkaRequest,
    interactor: FromDishka[RestoreUser],
) -> JsonResponse:
    try:
        data = msgspec.json.decode(request.body)
        params = UserRestoreSchema.from_raw(data)
    except ValidationError as e:
        return JsonResponse(
            {"error": "Invalid data", "field": e.field, "message": e.message},
            status=400,
        )
    user = interactor.execute(params.username, params.email, params.password)
    return JsonResponse(
        msgspec.json.encode(user),
        content_type="application/json",
        status=200,
    )


# --- CHANGE ROLE ---
@require_http_methods(["POST"])
@inject
def user_change_role_view(
    request: DishkaRequest,
    interactor: FromDishka[ChangeRole],
) -> HttpResponse:
    try:
        data = msgspec.json.decode(request.body)
        params = UserRoleSchema.from_raw(data)
    except ValidationError as e:
        return JsonResponse(
            {"error": "Invalid data", "field": e.field, "message": e.message},
            status=400,
        )

    session_data = cast(CustomSession, request.session)
    user_dto: UserDTO = interactor.execute(
        requester=session_data.user_id,
        target_username=params.target_username,
        new_role=UserRole[params.new_role],
    )

    return HttpResponse(
        msgspec.json.encode(user_dto),
        content_type="application/json",
    )


# --- CHANGE PASSWORD ---
@require_http_methods(["POST"])
@inject
def user_change_password_view(
    request: DishkaRequest,
    interactor: FromDishka[ChangePassword],
    user_id: str,
) -> HttpResponse:
    try:
        data = msgspec.json.decode(request.body)
        params = UserPasswordSchema.from_raw(data)
    except ValidationError as e:
        return JsonResponse(
            {
                "error": "Invalid data", 
                "field": e.field, 
                "message": e.message
            }, 
            status=400
        )
    session_data = cast(CustomSession, request.session)
    user = interactor.execute(session_data.user_id, params.old_hash, params.new_hash)
    return HttpResponse(msgspec.json.encode(user), content_type="application/json")


# --- CHANGE USERNAME ---
@require_http_methods(["POST"])
@inject
def user_change_username_view(
    request: DishkaRequest,
    interactor: FromDishka[ChangeUsername],
) -> HttpResponse:
    try:
        data = msgspec.json.decode(request.body)
        params = UserUpdateSchema.from_raw(data)
    except ValidationError as e:
        return JsonResponse(
            {"error": "Invalid data", "field": e.field, "message": e.message},
            status=400,
        )

    if not params.new_username:
        return JsonResponse(
            {
                "error": "Invalid data", 
                "field": "new_username", 
                "message": "Must not be empty"
            },
            status=400,
        )
    requester = cast(CustomSession, request.session)
    user: UserDTO = interactor.execute(requester.user_id, params.new_username)
    return HttpResponse(
        msgspec.json.encode(user),
        content_type="application/json",
    )


# --- CHANGE EMAIL ---
@require_http_methods(["POST"])
@inject
def user_change_email_view(
    request: DishkaRequest,
    interactor: FromDishka[ChangeEmail],
    user_id: str,
) -> HttpResponse:
    try:
        data = msgspec.json.decode(request.body)
        params = UserUpdateSchema.from_raw(data)
    except ValidationError as e:
        return JsonResponse(
            {"error": "Invalid data", "field": e.field, "message": e.message},
            status=400,
        )
    if not params.new_email:
        return JsonResponse(
            {
                "error": "Invalid data", 
                "field": "new_email", 
                "message": "Must not be empty"
            },
            status=400,
        )
    user = interactor.execute(UUID(user_id), params.new_email)
    return HttpResponse(msgspec.json.encode(user), content_type="application/json")
