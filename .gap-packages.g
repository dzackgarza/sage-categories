#!/usr/bin/env gap

BindGlobal("SAGE_CATEGORIES_InstallPackages", function()
local InstallExactPackage, packages, package;

# GAP PackageManager 1.6.3 provides exact package installation and dependency resolution.
if LoadPackage("PackageManager") <> true then
    Error("PackageManager is required");
fi;

PKGMAN_SetCustomPackageDir(Filename(DirectoryCurrent(), ".gap/pkg"));

InstallExactPackage := function(package)
    local required;
    required := Concatenation("=", package[2]);
    if TestPackageAvailability(package[1], required) = fail then
        if InstallPackage(package[3]) <> true then
            Error("failed to install ", package[1], " ", package[2]);
        fi;
    fi;
    if LoadPackage(package[1], required) <> true then
        Error("failed to load ", package[1], " ", package[2]);
    fi;
end;

packages := [
    [ "CAP", "2026.07-04", "https://github.com/homalg-project/CAP_project/releases/download/CAP-2026.07-04/CAP-2026.07-04.tar.gz" ],
    [ "ToolsForHomalg", "2026.04-01", "https://github.com/homalg-project/homalg_project/releases/download/ToolsForHomalg-2026.04-01/ToolsForHomalg-2026.04-01.tar.gz" ],
    [ "MonoidalCategories", "2026.08-02", "https://github.com/homalg-project/CAP_project/releases/download/MonoidalCategories-2026.08-02/MonoidalCategories-2026.08-02.tar.gz" ],
    [ "CartesianCategories", "2026.08-02", "https://github.com/homalg-project/CAP_project/releases/download/CartesianCategories-2026.08-02/CartesianCategories-2026.08-02.tar.gz" ],
    [ "ToolsForCategoricalTowers", "2026.08-01", "https://github.com/homalg-project/CategoricalTowers/releases/download/ToolsForCategoricalTowers-2026.08-01/ToolsForCategoricalTowers-2026.08-01.tar.gz" ],
    [ "SubcategoriesForCAP", "2026.07-01", "https://github.com/homalg-project/CategoricalTowers/releases/download/SubcategoriesForCAP-2026.07-01/SubcategoriesForCAP-2026.07-01.tar.gz" ],
    [ "FpCategories", "2026.07-03", "https://github.com/homalg-project/CategoricalTowers/releases/download/FpCategories-2026.07-03/FpCategories-2026.07-03.tar.gz" ],
    [ "SliceCategories", "2026.06-01", "https://github.com/homalg-project/CategoricalTowers/releases/download/SliceCategories-2026.06-01/SliceCategories-2026.06-01.tar.gz" ],
    [ "CompilerForCAP", "2026.07-01", "https://github.com/homalg-project/CAP_project/releases/download/CompilerForCAP-2026.07-01/CompilerForCAP-2026.07-01.tar.gz" ],
    [ "FunctorCategories", "2026.08-01", "https://github.com/homalg-project/CategoricalTowers/releases/download/FunctorCategories-2026.08-01/FunctorCategories-2026.08-01.tar.gz" ]
];

for package in packages do
    InstallExactPackage(package);
od;
end);

CallFuncList(ValueGlobal("SAGE_CATEGORIES_InstallPackages"), []);
MakeReadWriteGlobal("SAGE_CATEGORIES_InstallPackages");
UnbindGlobal("SAGE_CATEGORIES_InstallPackages");

QUIT_GAP(0);
