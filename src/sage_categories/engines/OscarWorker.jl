"""Dedicated OSCAR process for Sage Categories.

This process owns every OSCAR value. Python exchanges only JSON primitives and opaque
integer handles, so OSCAR's Julia project never shares a process or dependency graph
with the package-global Catlab/GATlab JuliaCall environment.
"""

@assert length(ARGS) == 2 "OSCAR worker requires its private home and bridge source"
worker_home, bridge_source = ARGS
mkpath(worker_home)
ENV["HOME"] = worker_home
const _PROTOCOL_STDOUT = stdout
redirect_stdout(stderr)

using Pkg
Pkg.instantiate(; io=stderr)
using JSON
using Oscar

include(bridge_source)
using .SageCategoriesOscarBridge

const _VALUES = Dict{Int,Any}()
const _HANDLES = IdDict{Any,Int}()
const _NEXT_HANDLE = Ref(0)
const _OPERATIONS = Set([
    "version",
    "prime_field",
    "polynomial_ring_with_generators",
    "quotient_ring",
    "localization_at_element",
    "localization_at_prime",
    "ring_hom",
    "localization_hom",
    "prime_ideal_from_generators",
    "prime_ideal_preimage",
    "stalk_map",
    "map_apply",
    "map_domain",
    "map_codomain",
    "ring_identity",
    "ring_compose",
    "ring_map_equal",
    "ring_generators",
    "ring_contains",
    "ring_equal",
    "ring_zero",
    "ring_one",
    "ring_add",
    "ring_multiply",
    "ring_negate",
    "ring_coerce",
    "ring_inverse",
    "same_native",
    "affine_spec",
    "affine_coordinate_ring",
    "affine_morphism_from_pullback",
    "affine_pullback",
    "affine_domain",
    "affine_codomain",
    "covered_scheme_of",
    "structure_sheaf",
    "sheaf_value",
    "sheaf_restriction",
    "principal_open_subset",
    "principal_open_ambient",
    "principal_open_inclusion",
    "affine_morphism_direct",
    "simple_gluing",
    "glued_covered_scheme",
    "covered_patches",
    "covered_chart_inclusion",
    "gluing_mediator",
    "covered_chart_map",
    "covered_domain",
    "covered_codomain",
    "covered_identity",
    "covered_compose",
    "covered_equal",
])

function _retain(value)
    if haskey(_HANDLES, value)
        return _HANDLES[value]
    end
    handle = _NEXT_HANDLE[]
    _NEXT_HANDLE[] += 1
    _VALUES[handle] = value
    _HANDLES[value] = handle
    handle
end

function _decode(value)
    if value isa AbstractDict && haskey(value, "__oscar_handle__")
        handle = Int(value["__oscar_handle__"])
        haskey(_VALUES, handle) || error("unknown OSCAR handle $(handle)")
        return _VALUES[handle]
    elseif value isa AbstractVector
        return [_decode(part) for part in value]
    elseif value isa AbstractDict
        return Dict(key => _decode(part) for (key, part) in value)
    end
    value
end

function _encode(value)
    if value === nothing || value isa Bool || value isa Integer ||
       value isa AbstractFloat || value isa AbstractString
        return value
    elseif value isa Tuple || value isa AbstractVector
        return [_encode(part) for part in value]
    end
    Dict("__oscar_handle__" => _retain(value))
end

function _handle(request)
    operation = String(request["op"])
    operation in _OPERATIONS || error("unknown OSCAR operation $(operation)")
    operation == "version" && return string(Base.pkgversion(Oscar))
    arguments = [_decode(argument) for argument in request["args"]]
    function_value = getfield(SageCategoriesOscarBridge, Symbol(operation))
    _encode(function_value(arguments...))
end

for line in eachline(stdin)
    try
        request = JSON.parse(line)
        response = Dict("ok" => true, "result" => _handle(request))
        println(_PROTOCOL_STDOUT, JSON.json(response))
    catch error
        response = Dict(
            "ok" => false,
            "error" => "$(typeof(error)): $(sprint(showerror, error))",
        )
        println(_PROTOCOL_STDOUT, JSON.json(response))
    end
    flush(_PROTOCOL_STDOUT)
end
