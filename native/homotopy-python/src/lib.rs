use homotopy_core::{
    common::BoundaryPath,
    signature::{GeneratorInfo, Invertibility, Signature as CoreSignature},
    typecheck::{typecheck, Mode},
    Boundary, Diagram, Diagram0, DiagramN, Generator,
};
use pyo3::{exceptions::PyValueError, prelude::*};

#[derive(Clone)]
struct GeneratorRecord {
    generator: Generator,
    diagram: Diagram,
    invertibility: Invertibility,
}

impl GeneratorInfo for GeneratorRecord {
    fn diagram(&self) -> &Diagram {
        &self.diagram
    }

    fn invertibility(&self) -> Invertibility {
        self.invertibility
    }
}

#[derive(Clone, Default)]
struct ProductionSignature {
    generators: Vec<GeneratorRecord>,
}

impl CoreSignature for ProductionSignature {
    type Info = GeneratorRecord;

    fn generators(&self) -> impl Iterator<Item = Generator> {
        self.generators.iter().map(|record| record.generator)
    }

    fn generator_info(&self, generator: Generator) -> Option<&Self::Info> {
        self.generators
            .get(generator.id)
            .filter(|record| record.generator == generator)
    }
}

fn parse_invertibility(kind: &str, dualisable: Option<usize>) -> PyResult<Invertibility> {
    match (kind, dualisable) {
        ("directed", None) => Ok(Invertibility::Directed),
        ("invertible", None) => Ok(Invertibility::Invertible),
        ("dualisable", Some(level)) => Ok(Invertibility::Dualisable(level)),
        _ => Err(PyValueError::new_err(
            "invertibility must be 'directed', 'invertible', or 'dualisable' with a level",
        )),
    }
}

fn boundary(side: &str) -> PyResult<Boundary> {
    match side {
        "source" => Ok(Boundary::Source),
        "target" => Ok(Boundary::Target),
        _ => Err(PyValueError::new_err(
            "boundary must be 'source' or 'target'",
        )),
    }
}

#[pyclass(
    name = "Cell",
    module = "sage_categories_homotopy",
    unsendable,
    skip_from_py_object
)]
#[derive(Clone)]
struct PyCell {
    diagram: Diagram,
    generator: Option<Generator>,
}

#[pymethods]
impl PyCell {
    fn dimension(&self) -> usize {
        self.diagram.dimension()
    }

    fn same_as(&self, other: &Self) -> bool {
        self.diagram == other.diagram
    }

    fn source(&self) -> PyResult<Self> {
        match &self.diagram {
            Diagram::Diagram0(_) => Err(PyValueError::new_err("a 0-cell has no source boundary")),
            Diagram::DiagramN(diagram) => Ok(Self {
                diagram: diagram.source(),
                generator: None,
            }),
        }
    }

    fn target(&self) -> PyResult<Self> {
        match &self.diagram {
            Diagram::Diagram0(_) => Err(PyValueError::new_err("a 0-cell has no target boundary")),
            Diagram::DiagramN(diagram) => Ok(Self {
                diagram: diagram.target(),
                generator: None,
            }),
        }
    }

    fn identity(&self) -> Self {
        Self {
            diagram: self.diagram.clone().identity().into(),
            generator: None,
        }
    }

    fn inverse(&self) -> PyResult<Self> {
        match &self.diagram {
            Diagram::Diagram0(_) => Err(PyValueError::new_err("a 0-cell has no inverse diagram")),
            Diagram::DiagramN(diagram) => Ok(Self {
                diagram: diagram.inverse().into(),
                generator: None,
            }),
        }
    }

    fn boundary(&self, side: &str, depth: usize) -> PyResult<Self> {
        let side = boundary(side)?;
        match &self.diagram {
            Diagram::Diagram0(_) => Err(PyValueError::new_err("a 0-cell has no boundary")),
            Diagram::DiagramN(diagram) => diagram
                .boundary(BoundaryPath(side, depth))
                .map(|value| Self {
                    diagram: value,
                    generator: None,
                })
                .ok_or_else(|| PyValueError::new_err("the requested boundary does not exist")),
        }
    }

    fn embeddings(&self, cell: &Self) -> PyResult<Vec<Vec<usize>>> {
        match &self.diagram {
            Diagram::Diagram0(_) => Err(PyValueError::new_err("a 0-cell has no embedding search")),
            Diagram::DiagramN(diagram) => Ok(diagram.embeddings(&cell.diagram).collect()),
        }
    }

    fn attach(&self, cell: &Self, side: &str, embedding: Vec<usize>) -> PyResult<Self> {
        let side = boundary(side)?;
        let Diagram::DiagramN(haystack) = &self.diagram else {
            return Err(PyValueError::new_err(
                "attachment requires a positive-dimensional cell",
            ));
        };
        let Diagram::DiagramN(added) = &cell.diagram else {
            return Err(PyValueError::new_err(
                "attachment requires a positive-dimensional attached cell",
            ));
        };
        haystack
            .attach(added, side, &embedding)
            .map(|diagram| Self {
                diagram: diagram.into(),
                generator: None,
            })
            .map_err(|error| PyValueError::new_err(format!("invalid attachment: {error}")))
    }
}

#[pyclass(
    name = "Signature",
    module = "sage_categories_homotopy",
    unsendable,
    skip_from_py_object
)]
#[derive(Clone, Default)]
struct PySignature {
    signature: ProductionSignature,
}

#[pymethods]
impl PySignature {
    #[new]
    fn new() -> Self {
        Self::default()
    }

    fn add_object(&mut self) -> PyCell {
        let generator = Generator::new(self.signature.generators.len(), 0);
        let diagram = Diagram0::from(generator);
        self.signature.generators.push(GeneratorRecord {
            generator,
            diagram: diagram.into(),
            invertibility: Invertibility::Directed,
        });
        PyCell {
            diagram: diagram.into(),
            generator: Some(generator),
        }
    }

    #[pyo3(signature = (source, target, invertibility="directed", dualisable=None))]
    fn add_generator(
        &mut self,
        source: &PyCell,
        target: &PyCell,
        invertibility: &str,
        dualisable: Option<usize>,
    ) -> PyResult<PyCell> {
        let classification = parse_invertibility(invertibility, dualisable)?;
        let dimension = source.diagram.dimension() + 1;
        let generator = Generator::new(self.signature.generators.len(), dimension);
        let diagram =
            DiagramN::from_generator(generator, source.diagram.clone(), target.diagram.clone())
                .map_err(|error| {
                    PyValueError::new_err(format!("invalid generator boundary: {error}"))
                })?;
        self.signature.generators.push(GeneratorRecord {
            generator,
            diagram: diagram.clone().into(),
            invertibility: classification,
        });
        Ok(PyCell {
            diagram: diagram.into(),
            generator: Some(generator),
        })
    }

    #[pyo3(signature = (cell, invertibility="invertible", dualisable=None))]
    fn strengthen_invertibility(
        &mut self,
        cell: &PyCell,
        invertibility: &str,
        dualisable: Option<usize>,
    ) -> PyResult<()> {
        let generator = cell.generator.ok_or_else(|| {
            PyValueError::new_err("only generator cells have an invertibility classification")
        })?;
        let classification = parse_invertibility(invertibility, dualisable)?;
        let record = self
            .signature
            .generators
            .get_mut(generator.id)
            .ok_or_else(|| PyValueError::new_err("generator is not in this signature"))?;
        if record.generator != generator {
            return Err(PyValueError::new_err("generator is not in this signature"));
        }
        let strengthens = match (record.invertibility, classification) {
            (Invertibility::Directed, Invertibility::Directed) => true,
            (Invertibility::Directed, Invertibility::Dualisable(_)) => true,
            (Invertibility::Directed, Invertibility::Invertible) => true,
            (Invertibility::Dualisable(old), Invertibility::Dualisable(new)) => new >= old,
            (Invertibility::Dualisable(_), Invertibility::Invertible) => true,
            (Invertibility::Invertible, Invertibility::Invertible) => true,
            _ => false,
        };
        if !strengthens {
            return Err(PyValueError::new_err(
                "invertibility classification cannot be weakened",
            ));
        }
        record.invertibility = classification;
        Ok(())
    }

    fn typecheck(&self, cell: &PyCell, recursive: bool) -> PyResult<()> {
        typecheck(&cell.diagram, &self.signature, Mode::default(), recursive)
            .map_err(|error| PyValueError::new_err(format!("cell typecheck failed: {error}")))
    }
}

#[pymodule]
fn sage_categories_homotopy(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PySignature>()?;
    module.add_class::<PyCell>()?;
    Ok(())
}
