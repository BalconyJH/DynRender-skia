from typing import Optional


class DynRenderException(Exception):
    """Base class for exceptions in this module."""

    def __str__(self) -> str:
        return self.__repr__()


class SkiaBaseError(DynRenderException):
    """Skia Base Error."""

    def __init__(self, message: Optional[str] = None, status: int = 0) -> None:
        self.message = message
        self.status = status

    def __repr__(self) -> str:
        return f"SkiaBaseError(status={self.status}, message={self.message})"


class ImageDecodeError(SkiaBaseError):
    """Exception raised for errors in the image decoding process."""


class DrawingError(SkiaBaseError):
    """Exception raised for errors during drawing operations."""
