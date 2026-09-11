"""Bootstrap ``Cat`` before importing modules that consume its declarations."""

from sage_categories.cat import category as _category

_category.bootstrap()
