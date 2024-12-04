from .circuit import Circuit
from .gates import Gate
from .qreg import QReg
from .stdgates import I, X, Y, Z

_pauli_gates: dict[str, type[Gate]] = {gate.name: gate for gate in (I, X, Y, Z)}


def pauli_circuit(pauli_string: str) -> type[Circuit]:
    """
    Generate a quantum circuit for a Pauli string.

    Args:
        pauli_string (str): Pauli string representing the operation.

    Returns:
        list: A list of Gate objects representing the quantum circuit.
    """
    pauli_string = pauli_string.lower()

    class Pauli(Circuit):
        target_reg = QReg(len(pauli_string))

        body: list[Gate] = []
        for i, op in enumerate(pauli_string):
            if op != "I":
                body.append(_pauli_gates[op](target_reg[i]))

    return Pauli


def pauli_gate(pauli_string: str) -> type[Gate]:
    """
    Generate a quantum gate for a Pauli string.

    Args:
        pauli_string (str): Pauli string representing the operation.

    Returns:
        list: A list of Gate objects representing the quantum circuit.
    """
    pauli_string = pauli_string.lower()

    class PauliGate(Gate):
        no_qubits = len(pauli_string)
        # When it isn't remapped, the qubit indices are from zero to n-1
        body = list(pauli_circuit(pauli_string).__body__)

    return PauliGate
