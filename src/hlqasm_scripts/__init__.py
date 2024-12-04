import argparse
import importlib.util
import tempfile
from typing import Any

from qiskit import qasm3  # type: ignore

from hlqasm import CIRCUIT, emit_circuit


def load_hlqasm_module(file_path: str) -> CIRCUIT:
    spec = importlib.util.spec_from_file_location("hlqasm_module", file_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load module from {file_path}")

    hlqasm_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hlqasm_module)

    # Extract the `circuit` variable
    circuit = getattr(hlqasm_module, "circuit", None)
    if circuit is None:
        raise ValueError("No circuit found in module")

    return circuit


def plot_circuit(circuit: CIRCUIT) -> None:
    with tempfile.TemporaryDirectory() as td:
        fname = f"{td}/circuit.qasm"
        with open(fname, "w") as f:
            f.write(emit_circuit(circuit))
        qiskit_circuit: Any = qasm3.load(fname)  # type: ignore
        print(qiskit_circuit)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a hlqasm script.")
    parser.add_argument(
        "hlqasm_script",
        type=argparse.FileType("r"),
        help="The hlqasm script to evaluate.",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Plot the circuit using qiskit.",
    )

    args = parser.parse_args()

    # Evaluate hlqasm script as a python file and extract the variable `circuit` from it.
    circuit = load_hlqasm_module(args.hlqasm_script.name)

    if args.plot:
        plot_circuit(circuit)
    else:
        print(emit_circuit(circuit))
