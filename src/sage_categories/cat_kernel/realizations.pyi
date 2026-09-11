from sage_categories.kernel.compiler import realize_implementation_class as realize_implementation_class
from sage_categories.kernel.construction import (
    active_object_context as active_object_context,
)
from sage_categories.kernel.construction import (
    install_object_realization as install_object_realization,
)
from sage_categories.kernel.construction import (
    retained_object_input as retained_object_input,
)
from sage_categories.kernel.refinement import place as place
from sage_categories.kernel.roles import ObjectOfCategory as ObjectOfCategory

def realize_object(value: ObjectOfCategory, category_type: type[ObjectOfCategory]) -> None: ...
def install() -> None: ...
