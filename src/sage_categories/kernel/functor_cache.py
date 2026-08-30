"""Store generic functor images in CAP-owned caches."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, NewType

from sage.libs.gap.libgap import libgap
from sage.structure.coerce_dict import MonoDict

if TYPE_CHECKING:
    from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, ObjectOfCategory

__all__: list[str] = []


CAP_VERSION = "2026.07-04"
TOOLS_FOR_HOMALG_VERSION = "2026.04-01"
CacheHandle = NewType("CacheHandle", int)


def _load_cap() -> None:
    package_root = Path(__file__).resolve().parents[3] / ".gap" / "pkg"
    tools_directory = package_root / f"ToolsForHomalg-{TOOLS_FOR_HOMALG_VERSION}"
    cap_directory = package_root / f"CAP-{CAP_VERSION}"
    assert tools_directory.is_dir(), (
        f"ToolsForHomalg {TOOLS_FOR_HOMALG_VERSION} is not provisioned at {tools_directory}; "
        "run the repository-owned GAP package installer"
    )
    assert cap_directory.is_dir(), (
        f"CAP {CAP_VERSION} is not provisioned at {cap_directory}; run the repository-owned GAP package installer"
    )
    libgap.SetPackagePath("ToolsForHomalg", str(tools_directory))
    assert bool(libgap.LoadPackage("ToolsForHomalg", f"={TOOLS_FOR_HOMALG_VERSION}")), (
        f"ToolsForHomalg {TOOLS_FOR_HOMALG_VERSION} is required"
    )
    libgap.SetPackagePath("CAP", str(cap_directory))
    assert bool(libgap.LoadPackage("CAP", f"={CAP_VERSION}")), f"CAP {CAP_VERSION} is required"
    package_info = libgap.PackageInfo("CAP")
    loaded_version = str(package_info[0]["Version"])
    assert loaded_version == CAP_VERSION, f"loaded CAP {loaded_version}, expected {CAP_VERSION}"


_load_cap()


class FunctorImageCache:
    """A functor's object and morphism images, keyed by opaque handles in CAP."""

    def __init__(self) -> None:
        source = libgap.CreateCapCategory("sage_categories_private_cache_source")
        target = libgap.CreateCapCategory("sage_categories_private_cache_target")
        carrier = libgap.CapFunctor("sage_categories_private_image_cache", source, target)
        self._objects = libgap.ObjectCache(carrier)
        self._morphisms = libgap.MorphismCache(carrier)
        libgap.SetCachingObjectCrisp(self._objects)
        libgap.SetCachingObjectCrisp(self._morphisms)
        self._source_handles: MonoDict = MonoDict()
        self._object_handles: MonoDict = MonoDict()
        self._morphism_handles: MonoDict = MonoDict()
        self._object_images_by_handle: dict[CacheHandle, ObjectOfCategory] = {}
        self._morphism_images_by_handle: dict[CacheHandle, MorphismOfCategory] = {}
        self._next_handle = 1

    def _handle(self, table: MonoDict, value: CategoryPoint) -> CacheHandle:
        if value not in table:
            table[value] = CacheHandle(self._next_handle)
            self._next_handle += 1
        return table[value]

    def object_image(
        self,
        source: ObjectOfCategory,
        construct: Callable[[ObjectOfCategory], ObjectOfCategory],
    ) -> ObjectOfCategory:
        source_handle = self._handle(self._source_handles, source)
        cached = libgap.CacheValue(self._objects, [source_handle])
        if len(cached) != 0:
            return self._object_images_by_handle[CacheHandle(int(cached[0]))]
        image = construct(source)
        image_handle = self._handle(self._object_handles, image)
        self._object_images_by_handle[image_handle] = image
        libgap.SetCacheValue(self._objects, [source_handle], image_handle)
        return image

    def _morphism_key(
        self,
        source: MorphismOfCategory,
        domain_image: ObjectOfCategory,
        codomain_image: ObjectOfCategory,
    ) -> list[CacheHandle]:
        return [
            self._handle(self._object_handles, domain_image),
            self._handle(self._source_handles, source),
            self._handle(self._object_handles, codomain_image),
        ]

    def morphism_image(
        self,
        source: MorphismOfCategory,
        on_object: Callable[[ObjectOfCategory], ObjectOfCategory],
        construct: Callable[[MorphismOfCategory], MorphismOfCategory],
    ) -> MorphismOfCategory:
        key = self._morphism_key(source, on_object(source.domain()), on_object(source.codomain()))
        cached = libgap.CacheValue(self._morphisms, key)
        if len(cached) != 0:
            return self._morphism_images_by_handle[CacheHandle(int(cached[0]))]
        image = construct(source)
        image_handle = self._handle(self._morphism_handles, image)
        self._morphism_images_by_handle[image_handle] = image
        libgap.SetCacheValue(self._morphisms, key, image_handle)
        return image
