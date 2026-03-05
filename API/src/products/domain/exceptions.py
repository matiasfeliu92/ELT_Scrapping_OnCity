class DomainError(Exception):
    """Base class for domain-level exceptions."""
    pass

class ProductNotFoundError(DomainError):
    """Raised when a requested product cannot be found in the repository."""
    pass