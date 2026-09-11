"""Install the joint ``cat_kernel`` readers before the public ``Cat`` package loads.

D175 puts the callbacks here in the package bootstrap order: importing this module
installs them, and only after this import returns does ``sage_categories.__init__``
import the modules that construct ``Cat``.
"""

from sage_categories import cat_kernel as _cat_kernel

_cat_kernel.install()
