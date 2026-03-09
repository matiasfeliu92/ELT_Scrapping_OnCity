from API.src.shared.common.exceptions.domain_error import DomainError

class UserNotFoundError(DomainError):
    """Raised when a requested product cannot be found in the repository."""
    pass