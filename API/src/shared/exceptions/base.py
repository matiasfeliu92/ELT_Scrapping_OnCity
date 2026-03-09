class AppException(Exception):
    status_code = 500

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code


class DomainError(AppException):
    status_code = 400


class ValidationError(AppException):
    status_code = 400


class AuthenticationError(AppException):
    status_code = 401


class AuthorizationError(AppException):
    status_code = 403


class NotFoundError(AppException):
    status_code = 404

class AlreadyExistsError(AppException):
    status_code = 409


class InternalServerError(AppException):
    status_code = 500
