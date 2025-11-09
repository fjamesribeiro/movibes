"""
Type hints customizados para Django.
Facilita a vida de quem vem de linguagens tipadas!
"""
from typing import TypeVar, Union, Protocol
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpRequest

# ===== USER TYPES =====

# Usuário autenticado (nunca AnonymousUser)
AuthenticatedUser = User  # Use isso em views com @login_required

# Usuário que pode ser anônimo
RequestUser = Union[User, AnonymousUser]


# ===== PROTOCOL PARA MODELS COM PERFIL =====

class UserWithProfile(Protocol):
    """
    Protocol para usuários que TEM perfil (Aluno ou Profissional).
    Use isso para garantir type safety.
    """
    id: int
    username: str
    email: str
    cadastro_completo: bool

    # Adicione seus campos customizados aqui:
    # aluno: 'Aluno'  # Se tiver
    # profissional: 'Profissional'  # Se tiver


# ===== TYPE GUARDS (CHECAGENS DE TIPO) =====

def is_authenticated_user(user: RequestUser) -> bool:
    """
    Type guard para verificar se é usuário autenticado.

    Uso:
        if is_authenticated_user(request.user):
            # Aqui o type checker sabe que é User, não AnonymousUser
            print(request.user.email)
    """
    return isinstance(user, User) and user.is_authenticated


# ===== GENERIC TYPES =====

# Para querysets tipados
T = TypeVar('T')


# ===== REQUEST TIPADO =====

class TypedRequest(HttpRequest):
    """
    HttpRequest com user sempre autenticado.
    Use em views com @login_required.
    """
    user: User  # Sobrescreve o tipo padrão Union[User, AnonymousUser]