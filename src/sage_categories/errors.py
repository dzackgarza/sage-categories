"""Errors raised by the category compiler."""


class CategoryFrameworkError(Exception):
    """Base error for invalid category declarations."""


class MethodCollisionError(CategoryFrameworkError):
    """Two unrelated categories declare one inherited method name."""


class IncoherentRouteError(CategoryFrameworkError):
    """A category has more than one structural route to a target."""


class MissingImplementationRouteError(CategoryFrameworkError):
    """No structural functor route reaches the requested category."""
