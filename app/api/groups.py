"""
Endpoints para gestión de grupos de usuarios.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db
from app.services.auth_service import get_current_user
from app.services.group_service import GroupService
from app.models.user import User
from app.schemas.error import ErrorResponse
from app.schemas.group import (
    Group, GroupCreate, GroupUpdate, GroupSummary,
    GroupMember, GroupMemberCreate, GroupMemberUpdate, GroupMemberWithUser
)
from app.schemas.invitation import Invitation, InvitationCreate, InvitationResponse

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post(
    "/",
    response_model=Group,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo grupo",
    description="""
    Crea un nuevo grupo de usuarios en la plataforma.
    
    - El usuario que crea el grupo se convierte automáticamente en administrador
    - El nombre del grupo debe ser único para el usuario
    - Se puede proporcionar una descripción opcional
    """,
    responses={
        201: {
            "description": "Grupo creado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Club de Lectura",
                        "description": "Grupo para compartir libros de fantasía",
                        "created_by": "123e4567-e89b-12d3-a456-426614174001",
                        "created_at": "2025-09-29T15:30:00",
                        "updated_at": None,
                        "members": [
                            {
                                "user": {
                                    "id": "123e4567-e89b-12d3-a456-426614174001",
                                    "username": "usuario1",
                                    "email": "usuario1@example.com"
                                },
                                "role": "admin",
                                "joined_at": "2025-09-29T15:30:00"
                            }
                        ]
                    }
                }
            }
        },
        400: {
            "description": "Datos de entrada inválidos o nombre de grupo ya en uso",
            "model": ErrorResponse
        },
        401: {
            "description": "No autorizado - Se requiere autenticación",
            "model": ErrorResponse
        },
        422: {
            "description": "Error de validación en los datos de entrada",
            "model": ErrorResponse
        }
    }
)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo grupo de usuarios.
    
    El usuario que crea el grupo se convierte automáticamente en administrador.
    """
    group_service = GroupService(db)
    group = group_service.create_group(group_data, current_user.id)
    return group

@router.get(
    "/",
    response_model=List[GroupSummary],
    summary="Obtener grupos del usuario",
    description="""
    Obtiene una lista de todos los grupos a los que pertenece el usuario autenticado.
    
    - Incluye información resumida de cada grupo
    - Muestra el rol del usuario en cada grupo
    - Incluye conteos de miembros y administradores
    """,
    responses={
        200: {
            "description": "Lista de grupos del usuario",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Club de Lectura",
                            "description": "Grupo para compartir libros de fantasía",
                            "member_count": 5,
                            "admin_count": 2,
                            "created_at": "2025-09-29T15:30:00",
                            "is_admin": True
                        },
                        {
                            "id": "223e4567-e89b-12d3-a456-426614174001",
                            "name": "Amantes del Misterio",
                            "description": "Intercambio de novelas de misterio y suspenso",
                            "member_count": 12,
                            "admin_count": 3,
                            "created_at": "2025-08-15T10:20:00",
                            "is_admin": False
                        }
                    ]
                }
            }
        },
        401: {
            "description": "No autorizado - Se requiere autenticación",
            "model": ErrorResponse
        }
    }
)
async def get_user_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recupera todos los grupos a los que pertenece el usuario actual.
    
    Para cada grupo, se incluye información resumida como el número de miembros,
    número de administradores y si el usuario actual es administrador del grupo.
    """
    group_service = GroupService(db)
    groups = group_service.get_user_groups(current_user.id)
    
    # Convertir a GroupSummary con información adicional
    group_summaries = []
    for group in groups:
        member_count = len(group.members)
        admin_count = sum(1 for member in group.members if member.role.value == "admin")
        is_admin = any(member.user_id == current_user.id and member.role.value == "admin" for member in group.members)
        
        group_summaries.append(GroupSummary(
            id=group.id,
            name=group.name,
            description=group.description,
            member_count=member_count,
            admin_count=admin_count,
            created_at=group.created_at,
            is_admin=is_admin
        ))
    
    return group_summaries


@router.get(
    "/{group_id}",
    response_model=Group,
    summary="Obtener detalles de un grupo",
    description="""
    Obtiene información detallada de un grupo específico al que pertenece el usuario.
    
    - Incluye la lista completa de miembros con sus roles
    - Muestra la información detallada del grupo
    - Solo accesible para miembros del grupo
    """,
    responses={
        200: {
            "description": "Detalles del grupo obtenidos exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Club de Lectura",
                        "description": "Grupo para compartir libros de fantasía",
                        "created_by": "123e4567-e89b-12d3-a456-426614174001",
                        "created_at": "2025-09-29T15:30:00",
                        "updated_at": None,
                        "members": [
                            {
                                "user": {
                                    "id": "123e4567-e89b-12d3-a456-426614174001",
                                    "username": "usuario1",
                                    "email": "usuario1@example.com"
                                },
                                "role": "admin",
                                "joined_at": "2025-09-29T15:30:00"
                            },
                            {
                                "user": {
                                    "id": "223e4567-e89b-12d3-a456-426614174002",
                                    "username": "usuario2",
                                    "email": "usuario2@example.com"
                                },
                                "role": "member",
                                "joined_at": "2025-09-30T10:15:00"
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "No autorizado - Se requiere autenticación",
            "model": ErrorResponse
        },
        403: {
            "description": "Prohibido - No eres miembro de este grupo",
            "model": ErrorResponse
        },
        404: {
            "description": "Grupo no encontrado",
            "model": ErrorResponse
        }
    }
)
async def get_group(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recupera los detalles completos de un grupo específico.
    
    Solo los miembros del grupo pueden ver sus detalles. Los administradores
    pueden ver información adicional como invitaciones pendientes y configuración
    avanzada del grupo.
    """
    group_service = GroupService(db)
    group = group_service.get_group(group_id, current_user.id)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes acceso"
        )
    
    return group


@router.put(
    "/{group_id}",
    response_model=Group,
    summary="Actualizar un grupo",
    description="""
    Actualiza la información de un grupo existente.
    
    - Solo los administradores del grupo pueden realizar esta acción
    - Se pueden actualizar el nombre y la descripción del grupo
    - Los campos no incluidos en la solicitud no se modificarán
    """,
    responses={
        200: {
            "description": "Grupo actualizado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Club de Lectura Actualizado",
                        "description": "Nueva descripción del grupo de lectura",
                        "created_by": "123e4567-e89b-12d3-a456-426614174001",
                        "created_at": "2025-09-29T15:30:00",
                        "updated_at": "2025-10-01T10:15:30",
                        "members": [
                            {
                                "user": {
                                    "id": "123e4567-e89b-12d3-a456-426614174001",
                                    "username": "usuario1",
                                    "email": "usuario1@example.com"
                                },
                                "role": "admin",
                                "joined_at": "2025-09-29T15:30:00"
                            }
                        ]
                    }
                }
            }
        },
        400: {
            "description": "Datos de entrada inválidos",
            "model": ErrorResponse
        },
        401: {
            "description": "No autorizado - Se requiere autenticación",
            "model": ErrorResponse
        },
        403: {
            "description": "Prohibido - No tienes permisos de administrador",
            "model": ErrorResponse
        },
        404: {
            "description": "Grupo no encontrado",
            "model": ErrorResponse
        }
    }
)
async def update_group(
    group_id: UUID,
    group_data: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza la información de un grupo existente.
    
    Solo los administradores del grupo pueden modificar su información.
    Los campos no incluidos en la solicitud permanecerán sin cambios.
    """
    group_service = GroupService(db)
    group = group_service.update_group(group_id, current_user.id, group_data)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes permisos de administrador"
        )
    
    return group


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un grupo",
    description="""
    Elimina permanentemente un grupo y todos sus datos asociados.
    
    - Solo el creador del grupo puede eliminarlo
    - Esta acción no se puede deshacer
    - Se eliminarán todos los miembros, invitaciones y configuraciones del grupo
    """,
    responses={
        204: {
            "description": "Grupo eliminado exitosamente",
            "content": None
        },
        401: {
            "description": "No autorizado - Se requiere autenticación",
            "model": ErrorResponse
        },
        403: {
            "description": "Prohibido - Solo el creador puede eliminar el grupo",
            "model": ErrorResponse
        },
        404: {
            "description": "Grupo no encontrado",
            "model": ErrorResponse
        }
    }
)
async def delete_group(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina permanentemente un grupo y todos sus datos asociados.
    
    Esta acción es irreversible y eliminará todos los miembros, invitaciones
    y configuraciones del grupo. Solo el usuario que creó el grupo puede
    realizar esta acción.
    """
    group_service = GroupService(db)
    success = group_service.delete_group(group_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no eres el creador"
        )


@router.get(
    "/{group_id}/members",
    response_model=List[GroupMemberWithUser],
    summary="Obtener miembros de un grupo",
    description="""
    Obtiene la lista de todos los miembros de un grupo específico.
    
    - Solo los miembros del grupo pueden ver la lista de miembros
    - Incluye información detallada de cada miembro
    - Muestra el rol de cada usuario en el grupo
    - Incluye la fecha en que se unió al grupo
    """,
    responses={
        200: {
            "description": "Lista de miembros del grupo obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "user": {
                                "id": "123e4567-e89b-12d3-a456-426614174001",
                                "username": "usuario1",
                                "email": "usuario1@example.com"
                            },
                            "role": "admin",
                            "joined_at": "2025-09-29T15:30:00"
                        },
                        {
                            "user": {
                                "id": "223e4567-e89b-12d3-a456-426614174002",
                                "username": "usuario2",
                                "email": "usuario2@example.com"
                            },
                            "role": "member",
                            "joined_at": "2025-09-30T10:15:00"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "No autorizado - Se requiere autenticación",
            "model": ErrorResponse
        },
        403: {
            "description": "Prohibido - No eres miembro de este grupo",
            "model": ErrorResponse
        },
        404: {
            "description": "Grupo no encontrado",
            "model": ErrorResponse
        }
    }
)
async def get_group_members(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recupera la lista completa de miembros de un grupo específico.
    
    Solo los miembros del grupo pueden ver la lista de miembros. Los administradores
    pueden ver información adicional sobre los miembros, como su rol y fecha de ingreso.
    """
    group_service = GroupService(db)
    members = group_service.get_group_members(group_id, current_user.id)
    
    if members is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes acceso"
        )
    
    return members


@router.post(
    "/{group_id}/members",
    response_model=GroupMember,
    status_code=status.HTTP_201_CREATED,
    summary="Añadir un miembro al grupo",
    description="""
    Añade un nuevo miembro a un grupo existente.
    
    - Solo los administradores del grupo pueden añadir nuevos miembros
    - El usuario debe existir en la plataforma
    - No se puede añadir a un usuario que ya es miembro del grupo
    - Se puede especificar el rol del nuevo miembro (por defecto es 'member')
    """,
    responses={
        201: {
            "description": "Miembro añadido exitosamente al grupo",
            "content": {
                "application/json": {
                    "example": {
                        "id": "323e4567-e89b-12d3-a456-426614174003",
                        "group_id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "323e4567-e89b-12d3-a456-426614174003",
                        "role": "member",
                        "joined_at": "2025-10-01T14:30:00",
                        "invited_by": "123e4567-e89b-12d3-a456-426614174001"
                    }
                }
            }
        },
        400: {
            "description": "Solicitud inválida - El usuario ya es miembro o no existe",
            "model": ErrorResponse
        },
        401: {
            "description": "No autorizado - Se requiere autenticación",
            "model": ErrorResponse
        },
        403: {
            "description": "Prohibido - No tienes permisos de administrador",
            "model": ErrorResponse
        },
        404: {
            "description": "Grupo o usuario no encontrado",
            "model": ErrorResponse
        }
    }
)
async def add_group_member(
    group_id: UUID,
    member_data: GroupMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Añade un nuevo miembro a un grupo existente.
    
    Los administradores del grupo pueden invitar a otros usuarios a unirse.
    El usuario objetivo recibirá una notificación de la invitación.
    """
    group_service = GroupService(db)
    member = group_service.add_member(group_id, current_user.id, member_data)
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo añadir el miembro. Verifica que seas admin y el usuario no sea ya miembro"
        )
    
    return member


@router.put(
    "/{group_id}/members/{member_id}",
    response_model=GroupMember,
    summary="Actualizar rol de un miembro",
    description="""
    Actualiza el rol de un miembro en el grupo.
    
    - Solo los administradores pueden modificar roles
    - No se puede modificar el rol del propietario del grupo
    - No se puede asignar un rol superior al propio
    - Roles disponibles: 'admin', 'member'
    """,
    responses={
        200: {
            "description": "Rol actualizado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "group_id": "123e4567-e89b-12d3-a456-426614174001",
                        "user_id": "223e4567-e89b-12d3-a456-426614174002",
                        "role": "admin",
                        "joined_at": "2025-09-15T10:30:00",
                        "user": {
                            "id": "223e4567-e89b-12d3-a456-426614174002",
                            "username": "usuario_actualizado",
                            "email": "usuario@ejemplo.com"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Solicitud inválida - No se puede modificar el rol del propietario o rol inválido",
            "model": ErrorResponse
        },
        403: {
            "description": "No autorizado - No tienes permisos para actualizar roles",
            "model": ErrorResponse
        },
        404: {
            "description": "No encontrado - Grupo o miembro no encontrado",
            "model": ErrorResponse
        }
    }
)
async def update_member_role(
    group_id: UUID,
    member_id: UUID,
    role_data: GroupMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el rol de un miembro específico en el grupo.
    
    Esta operación solo puede ser realizada por un administrador del grupo.
    El propietario del grupo no puede cambiar su propio rol.
    """
    group_service = GroupService(db)
    member = group_service.update_member_role(group_id, current_user.id, member_id, role_data)
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Miembro no encontrado o no tienes permisos de administrador"
        )
    
    return member


@router.delete(
    "/{group_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un miembro del grupo",
    description="""
    Elimina a un miembro de un grupo existente.
    
    - Solo los administradores del grupo pueden eliminar miembros
    - No se puede eliminar al creador del grupo
    - No se puede eliminar a uno mismo (usar leave_group en su lugar)
    - La acción es irreversible
    """,
    responses={
        204: {
            "description": "Miembro eliminado exitosamente del grupo"
        },
        400: {
            "description": "Solicitud inválida - No puedes eliminar al creador del grupo o a ti mismo",
            "model": ErrorResponse
        },
        401: {
            "description": "No autorizado - Se requiere autenticación",
            "model": ErrorResponse
        },
        403: {
            "description": "Prohibido - No tienes permisos de administrador",
            "model": ErrorResponse
        },
        404: {
            "description": "Grupo o miembro no encontrado",
            "model": ErrorResponse
        }
    }
)
async def remove_group_member(
    group_id: UUID,
    member_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina a un miembro de un grupo existente.
    
    Solo los administradores pueden eliminar a otros miembros. No se puede eliminar
    al creador del grupo ni a uno mismo. Para salir de un grupo, usar leave_group.
    """
    group_service = GroupService(db)
    success = group_service.remove_member(group_id, current_user.id, member_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Miembro no encontrado o no tienes permisos de administrador"
        )


@router.post(
    "/{group_id}/invitations",
    response_model=Invitation,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una invitación a un grupo",
    description="""
    Crea una nueva invitación para unirse a un grupo existente.
    
    - Solo los administradores del grupo pueden crear invitaciones
    - Se puede invitar a cualquier correo electrónico, incluso si el usuario no está registrado
    - La invitación expira después de 7 días por defecto
    - No se pueden crear invitaciones duplicadas para el mismo correo en el mismo grupo
    """,
    responses={
        201: {
            "description": "Invitación creada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "group_id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "usuario@ejemplo.com",
                        "code": "ABC123DEF456",
                        "created_at": "2025-09-29T15:30:00",
                        "expires_at": "2025-10-06T15:30:00",
                        "is_accepted": None,
                        "responded_at": None,
                        "invited_by": "123e4567-e89b-12d3-a456-426614174001"
                    }
                }
            }
        },
        400: {
            "description": "Solicitud inválida - Ya existe una invitación pendiente para este correo",
            "model": ErrorResponse
        },
        401: {
            "description": "No autorizado - Se requiere autenticación",
            "model": ErrorResponse
        },
        403: {
            "description": "Prohibido - No tienes permisos de administrador",
            "model": ErrorResponse
        },
        404: {
            "description": "Grupo no encontrado",
            "model": ErrorResponse
        }
    }
)
async def create_invitation(
    group_id: UUID,
    invitation_data: InvitationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva invitación para que un usuario se una al grupo especificado.
    
    El usuario invitado recibirá un correo electrónico con un enlace para unirse al grupo.
    La invitación contendrá un código único que el usuario debe usar para unirse.
    """
    group_service = GroupService(db)
    invitation = group_service.create_invitation(group_id, current_user.id, invitation_data)
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear la invitación. Verifica que seas admin y no exista una invitación pendiente"
        )
    
    # Asegurar que el campo code esté presente en la respuesta incluso si el modelo no lo hidrata aún
    try:
        from sqlalchemy import text as _text
        code_row = db.execute(_text("SELECT code FROM invitations WHERE id = :id"), {"id": str(invitation.id)}).first()
        code_val = code_row[0] if code_row else None
        if code_val is not None:
            return {
                "id": invitation.id,
                "group_id": invitation.group_id,
                "email": invitation.email,
                "message": invitation.message,
                "invited_by": invitation.invited_by,
                "created_at": invitation.created_at,
                "expires_at": invitation.expires_at,
                "is_accepted": invitation.is_accepted,
                "responded_at": invitation.responded_at,
                "code": code_val,
            }
    except Exception:
        pass
    return invitation


@router.get(
    "/{group_id}/invitations",
    response_model=List[Invitation],
    summary="Obtener invitaciones de un grupo",
    description="""
    Obtiene la lista de todas las invitaciones pendientes y aceptadas de un grupo.
    
    - Solo los administradores del grupo pueden ver las invitaciones
    - Incluye invitaciones pendientes, aceptadas y rechazadas
    - Muestra quién invitó a cada usuario y cuándo
    - Incluye códigos de invitación para compartir
    """,
    responses={
        200: {
            "description": "Lista de invitaciones obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "group_id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "usuario@ejemplo.com",
                            "code": "ABC123DEF456",
                            "message": "¡Únete a nuestro grupo de lectura!",
                            "created_at": "2025-09-29T15:30:00",
                            "expires_at": "2025-10-06T15:30:00",
                            "is_accepted": None,
                            "responded_at": None,
                            "invited_by": "123e4567-e89b-12d3-a456-426614174001"
                        },
                        {
                            "id": "223e4567-e89b-12d3-a456-426614174002",
                            "group_id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "otro@ejemplo.com",
                            "code": "XYZ789ABC123",
                            "message": "Invitación al club de lectura",
                            "created_at": "2025-09-28T10:15:00",
                            "expires_at": "2025-10-05T10:15:00",
                            "is_accepted": True,
                            "responded_at": "2025-09-28T14:30:00",
                            "invited_by": "123e4567-e89b-12d3-a456-426614174001"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "No autorizado - Se requiere autenticación",
            "model": ErrorResponse
        },
        403: {
            "description": "Prohibido - No tienes permisos de administrador",
            "model": ErrorResponse
        },
        404: {
            "description": "Grupo no encontrado",
            "model": ErrorResponse
        }
    }
)
async def get_group_invitations(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recupera todas las invitaciones asociadas a un grupo específico.
    
    Proporciona una lista completa de invitaciones, incluyendo su estado actual
    (pendiente, aceptada o rechazada) y la información de quién realizó la invitación.
    """
    group_service = GroupService(db)
    invitations = group_service.get_group_invitations(group_id, current_user.id)
    
    if invitations is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado o no tienes permisos de administrador"
        )
    # Devolver también el code aunque el ORM no lo haya materializado aún
    try:
        from sqlalchemy import text as _text
        ids = [str(inv.id) for inv in invitations]
        if not ids:
            return []
        rows = db.execute(_text("SELECT id, code FROM invitations WHERE id = ANY(:ids)"), {"ids": ids}).fetchall()
        id_to_code = {str(r[0]): r[1] for r in rows}
        enriched = []
        for inv in invitations:
            code_val = id_to_code.get(str(inv.id))
            enriched.append({
                "id": inv.id,
                "group_id": inv.group_id,
                "email": inv.email,
                "message": inv.message,
                "invited_by": inv.invited_by,
                "created_at": inv.created_at,
                "expires_at": inv.expires_at,
                "is_accepted": inv.is_accepted,
                "responded_at": inv.responded_at,
                "code": code_val,
            })
        return enriched
    except Exception:
        return invitations


@router.get(
    "/invitations/by-code/{code}",
    response_model=Invitation,
    summary="Obtener detalles de una invitación por código",
    description="""
    Obtiene los detalles completos de una invitación utilizando su código único.
    
    - No requiere autenticación para permitir la previsualización de la invitación
    - Útil para mostrar información del grupo al usuario antes de aceptar
    - Incluye detalles del grupo, mensaje de invitación y fecha de expiración
    - Verifica si la invitación sigue siendo válida
    """,
    responses={
        200: {
            "description": "Detalles de la invitación obtenidos exitosamente",
            "model": Invitation
        },
        404: {
            "description": "Invitación no encontrada o ha expirado",
            "model": ErrorResponse
        },
        410: {
            "description": "La invitación ha expirado",
            "model": ErrorResponse
        }
    }
)
async def get_invitation_by_code(
    code: str,
    db: Session = Depends(get_db)
):
    """
    Recupera los detalles de una invitación utilizando su código único.
    
    Este endpoint es de acceso público y no requiere autenticación, lo que permite
    a los usuarios ver la información de la invitación antes de decidir si unirse.
    """
    from app.models.invitation import Invitation as InvitationModel
    inv = db.query(InvitationModel).filter(InvitationModel.code == code).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitación no encontrada")
    return inv


@router.get(
    "/invitations/pending",
    response_model=List[Invitation],
    summary="Obtener invitaciones pendientes del usuario",
    description="""
    Obtiene la lista de invitaciones pendientes del usuario autenticado.
    
    - Muestra solo las invitaciones dirigidas al correo del usuario
    - Incluye únicamente invitaciones que no han sido respondidas
    - Proporciona detalles del grupo y del usuario que realizó la invitación
    - Las invitaciones expiradas se filtran automáticamente
    """,
    responses={
        200: {
            "description": "Lista de invitaciones pendientes obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "group_id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "usuario@ejemplo.com",
                            "code": "ABC123DEF456",
                            "message": "¡Te invitamos a nuestro grupo de lectura!",
                            "created_at": "2025-09-29T15:30:00",
                            "expires_at": "2025-10-06T15:30:00",
                            "is_accepted": None,
                            "responded_at": None,
                            "invited_by": {
                                "id": "223e4567-e89b-12d3-a456-426614174001",
                                "username": "usuario_invitador",
                                "email": "invitador@ejemplo.com"
                            },
                            "group": {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "name": "Club de Lectura 2025",
                                "description": "Grupo para amantes de la lectura",
                                "created_at": "2025-09-01T10:00:00"
                            }
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Solicitud inválida - El usuario no tiene un correo electrónico configurado",
            "model": ErrorResponse
        },
        401: {
            "description": "No autorizado - Se requiere autenticación",
            "model": ErrorResponse
        }
    }
)
async def get_pending_invitations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recupera todas las invitaciones pendientes dirigidas al usuario actual.
    
    Este endpoint devuelve una lista de invitaciones que aún no han sido
    aceptadas ni rechazadas por el usuario y que no han expirado.
    """
    if not current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario debe tener un email para recibir invitaciones"
        )
    
    group_service = GroupService(db)
    invitations = group_service.get_user_invitations(current_user.email)
    return invitations


@router.post(
    "/invitations/{invitation_id}/respond",
    response_model=GroupMember,
    summary="Responder a una invitación por ID",
    description="""
    Permite a un usuario responder a una invitación específica.
    
    - El usuario debe estar autenticado y su email debe coincidir con el de la invitación
    - Si se acepta la invitación, el usuario se convierte en miembro del grupo
    - Si se rechaza, la invitación se marca como rechazada
    - Las invitaciones solo pueden responderse una vez
    - La respuesta debe incluir un campo 'accept' que indique si se acepta (true) o rechaza (false) la invitación
    """,
    responses={
        200: {
            "description": "Invitación respondida exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "group_id": "123e4567-e89b-12d3-a456-426614174001",
                        "user_id": "223e4567-e89b-12d3-a456-426614174002",
                        "role": "member",
                        "joined_at": "2025-09-29T16:30:00",
                        "user": {
                            "id": "223e4567-e89b-12d3-a456-426614174002",
                            "username": "nuevo_miembro",
                            "email": "usuario@ejemplo.com"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Solicitud inválida - Usuario sin email o invitación ya respondida",
            "model": ErrorResponse
        },
        403: {
            "description": "No autorizado - No tienes permiso para responder esta invitación",
            "model": ErrorResponse
        },
        404: {
            "description": "No encontrado - Invitación no encontrada o expirada",
            "model": ErrorResponse
        },
        410: {
            "description": "Invitación expirada - La invitación ha caducado",
            "model": ErrorResponse
        }
    }
)
async def respond_to_invitation(
    invitation_id: UUID,
    response_data: InvitationResponse,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Procesa la respuesta de un usuario a una invitación de grupo.
    
    Permite a un usuario aceptar o rechazar una invitación recibida.
    La respuesta debe incluir un campo 'accept' que indique si se acepta (true) o rechaza (false) la invitación.
    """
    if not current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario debe tener un email para responder a la invitación"
        )
    
    group_service = GroupService(db)
    member = group_service.respond_to_invitation(
        invitation_id, 
        current_user.email, 
        response_data.accept
    )
    
    if not member and response_data.accept:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo aceptar la invitación. Puede que ya seas miembro del grupo o la invitación haya expirado"
        )
    
    return member


@router.post(
    "/invitations/accept/{code}",
    response_model=GroupMember,
    summary="Aceptar una invitación por código",
    description="""
    Acepta una invitación a un grupo utilizando un código de invitación.
    
    - El código de invitación debe ser válido y no haber expirado
    - Solo el usuario al que fue enviada la invitación puede aceptarla
    - La invitación no debe haber sido previamente aceptada o rechazada
    - Al aceptar, el usuario se convierte en miembro del grupo
    """,
    responses={
        200: {
            "description": "Invitación aceptada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "323e4567-e89b-12d3-a456-426614174003",
                        "group_id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "323e4567-e89b-12d3-a456-426614174003",
                        "role": "member",
                        "joined_at": "2025-10-01T14:30:00"
                    }
                }
            }
        },
        400: {
            "description": "Solicitud inválida - La invitación ya ha sido usada o no es válida",
            "model": ErrorResponse
        },
        401: {
            "description": "No autorizado - Se requiere autenticación",
            "model": ErrorResponse
        },
        403: {
            "description": "Prohibido - No tienes permiso para aceptar esta invitación",
            "model": ErrorResponse
        },
        404: {
            "description": "Invitación no encontrada o ha expirado",
            "model": ErrorResponse
        },
        410: {
            "description": "La invitación ha expirado",
            "model": ErrorResponse
        }
    }
)

async def accept_invitation_by_code(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permite a un usuario aceptar una invitación a un grupo utilizando un código de invitación.
    
    El usuario debe estar autenticado y su correo electrónico debe coincidir con el de la invitación.
    La invitación debe estar en estado pendiente y no haber expirado.
    """
    from app.models.invitation import Invitation as InvitationModel
    
    # Buscar la invitación por código
    invitation = db.query(InvitationModel).filter(
        InvitationModel.code == code,
        InvitationModel.is_accepted.is_(None),
        InvitationModel.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitación no encontrada, ya ha sido usada o ha expirado"
        )
    
    # Verificar que el correo coincida con el usuario autenticado
    if current_user.email.lower() != invitation.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para aceptar esta invitación"
        )
    
    # Usar el servicio para procesar la aceptación
    group_service = GroupService(db)
    member = group_service.respond_to_invitation(invitation.id, current_user.email, True)
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo aceptar la invitación. Puede que ya seas miembro del grupo"
        )
    
    return member
