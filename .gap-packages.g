#!/usr/bin/env gap

BindGlobal("SAGE_CATEGORIES_InstallPackages", function()
local IsExactPackageInstalled, InstallExactPackage, packages, package;

# GAP PackageManager provides exact package installation and dependency resolution.
if LoadPackage("PackageManager") <> true then
    PrintTo("*errout*", "PackageManager is required\n");
    QUIT_GAP(1);
fi;

PKGMAN_SetCustomPackageDir(Filename(DirectoryCurrent(), ".gap/pkg"));

IsExactPackageInstalled := function(package)
    return ForAny(
        PKGMAN_UserPackageInfo(package[1]),
        info -> info.Version = package[2]
    );
end;

InstallExactPackage := function(package)
    local required;
    required := Concatenation("=", package[2]);
    if not IsExactPackageInstalled(package) then
        if InstallPackage(package[3]) <> true then
            PrintTo("*errout*", "failed to install ", package[1], " ", package[2], "\n");
            QUIT_GAP(1);
        fi;
    fi;
    if not IsExactPackageInstalled(package) then
        PrintTo("*errout*", "package is not installed locally: ", package[1], " ", package[2], "\n");
        QUIT_GAP(1);
    fi;
    if LoadPackage(package[1], required) <> true then
        PrintTo("*errout*", "failed to load ", package[1], " ", package[2], "\n");
        QUIT_GAP(1);
    fi;
end;

packages := [
    [ "ToolsForHomalg", "2026.04-01", "https://github.com/homalg-project/homalg_project/releases/download/ToolsForHomalg-2026.04-01/ToolsForHomalg-2026.04-01.tar.gz" ],
    [ "CAP", "2026.07-04", "https://github.com/homalg-project/CAP_project/releases/download/CAP-2026.07-04/CAP-2026.07-04.tar.gz" ],
    [ "MonoidalCategories", "2026.08-02", "https://github.com/homalg-project/CAP_project/releases/download/MonoidalCategories-2026.08-02/MonoidalCategories-2026.08-02.tar.gz" ],
    [ "CartesianCategories", "2026.08-02", "https://github.com/homalg-project/CAP_project/releases/download/CartesianCategories-2026.08-02/CartesianCategories-2026.08-02.tar.gz" ],
    [ "ToolsForCategoricalTowers", "2026.08-01", "https://github.com/homalg-project/CategoricalTowers/releases/download/ToolsForCategoricalTowers-2026.08-01/ToolsForCategoricalTowers-2026.08-01.tar.gz" ],
    [ "Toposes", "2025.12-02", "https://github.com/homalg-project/CategoricalTowers/releases/download/Toposes-2025.12-02/Toposes-2025.12-02.tar.gz" ],
    [ "FinSetsForCAP", "2025.12-08", "https://github.com/homalg-project/FinSetsForCAP/releases/download/v2025.12-08/FinSetsForCAP-2025.12-08.tar.gz" ],
    [ "QuotientCategories", "2026.04-01", "https://github.com/homalg-project/CategoricalTowers/releases/download/QuotientCategories-2026.04-01/QuotientCategories-2026.04-01.tar.gz" ],
    [ "CompilerForCAP", "2026.07-01", "https://github.com/homalg-project/CAP_project/releases/download/CompilerForCAP-2026.07-01/CompilerForCAP-2026.07-01.tar.gz" ],
    [ "AdditiveClosuresForCAP", "2026.06-02", "https://github.com/homalg-project/CAP_project/releases/download/AdditiveClosuresForCAP-2026.06-02/AdditiveClosuresForCAP-2026.06-02.tar.gz" ],
    [ "GroupsAsCategoriesForCAP", "2025.07-01", "https://github.com/homalg-project/CAP_project/releases/download/GroupsAsCategoriesForCAP-2025.07-01/GroupsAsCategoriesForCAP-2025.07-01.tar.gz" ],
    [ "LinearClosuresForCAP", "2026.06-01", "https://github.com/homalg-project/CAP_project/releases/download/LinearClosuresForCAP-2026.06-01/LinearClosuresForCAP-2026.06-01.tar.gz" ],
    [ "FreydCategoriesForCAP", "2026.06-01", "https://github.com/homalg-project/CAP_project/releases/download/FreydCategoriesForCAP-2026.06-01/FreydCategoriesForCAP-2026.06-01.tar.gz" ],
    [ "LinearAlgebraForCAP", "2026.04-02", "https://github.com/homalg-project/CAP_project/releases/download/LinearAlgebraForCAP-2026.04-02/LinearAlgebraForCAP-2026.04-02.tar.gz" ],
    [ "FpCategories", "2026.07-03", "https://github.com/homalg-project/CategoricalTowers/releases/download/FpCategories-2026.07-03/FpCategories-2026.07-03.tar.gz" ],
    [ "Locales", "2026.08-01", "https://github.com/homalg-project/CategoricalTowers/releases/download/Locales-2026.08-01/Locales-2026.08-01.tar.gz" ],
    [ "SubcategoriesForCAP", "2026.07-01", "https://github.com/homalg-project/CategoricalTowers/releases/download/SubcategoriesForCAP-2026.07-01/SubcategoriesForCAP-2026.07-01.tar.gz" ],
    [ "SliceCategories", "2026.06-01", "https://github.com/homalg-project/CategoricalTowers/releases/download/SliceCategories-2026.06-01/SliceCategories-2026.06-01.tar.gz" ],
    [ "PresheafCategories", "2026.05-01", "https://github.com/homalg-project/CategoricalTowers/releases/download/PresheafCategories-2026.05-01/PresheafCategories-2026.05-01.tar.gz" ],
    [ "FpLinearCategories", "2026.07-02", "https://github.com/homalg-project/CategoricalTowers/releases/download/FpLinearCategories-2026.07-02/FpLinearCategories-2026.07-02.tar.gz" ],
    [ "QPA", "2.0-dev", "https://github.com/homalg-project/QPA2/archive/8ffbde256214f5bcef6e3e86b29ccf0e0acd5afa.tar.gz" ],
    [ "Algebroids", "2026.07-04", "https://github.com/homalg-project/CategoricalTowers/releases/download/Algebroids-2026.07-04/Algebroids-2026.07-04.tar.gz" ],
    [ "FiniteCocompletions", "2026.07-01", "https://github.com/homalg-project/CategoricalTowers/releases/download/FiniteCocompletions-2026.07-01/FiniteCocompletions-2026.07-01.tar.gz" ],
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
