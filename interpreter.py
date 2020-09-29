from qiskit import(
  QuantumCircuit,
  execute,
  Aer)
from qiskit.visualization import circuit_drawer as cirtuit_drawer

def parse_and_run(circ_str, fname):
    # Use Aer's qasm_simulator
    simulator = Aer.get_backend('qasm_simulator')

    circuit = QuantumCircuit(len(circ_str), len(circ_str))
                
    for i in range(len(circ_str[0])):
        for j in range(len(circ_str)):
            qbit = circ_str[j]
            operation = qbit[i]

            # Hadamard
            if (operation=='H'):
                circuit.h(j)

            # NOT / Pauli X
            elif (operation=='X' and qbit[i-1]!='C'):
                circuit.x(j)

            # Pauli Z
            elif (operation=='Z' and qbit[i-1]!='C'):
                circuit.z(j)

            # Pauli Y
            elif (operation=='Y' and qbit[i-1]!='C'):
                circuit.y(j)

            # T-gate
            elif (operation=='T'):
                circuit.t(j)

            # S-gate
            elif (operation=='S'):
                circuit.s(j)
                
            # Set qubit to |0>
            elif (operation=='0'):
                circuit.reset(j)

            # Measure
            elif (operation=='M'):
                circuit.measure(j, j)

            # Barrier
            elif (operation=='|'):
                circuit.barrier(j)

            # Identity
            elif (operation=='i'):
                circuit.iden(j)
                
            # Swap (2 qubits)
            elif (operation=='x'):
                swap1=j
                swap2=-1
                for k in range(j+1, len(circ_str)):
                    if (circ_str[k][i]=='x'):
                        swap2=k
                # checks if swap2 was found
                if (swap2!=-1):
                    circuit.swap(swap1, swap2)

            # Ctrl operations (2 qubits)
            elif (operation=='C'):
                
                # Getting control
                ctrl=[]
                for k in range(len(circ_str)):
                    if (circ_str[k][i]=='o'):
                        ctrl.append(k)

                # CNOT
                if (qbit[i+1]=='X'):
                    target=j
                    circuit.cx(ctrl, target)
                    
                # CZ
                if (qbit[i+1]=='Z'):
                    target=j
                    circuit.cz(ctrl, target)
                    
                # CY
                if (qbit[i+1]=='Y'):
                    target=j
                    circuit.cy(ctrl, target)

                    
            # Toffoli gate (CCNOT; 3 qubits)
            elif (operation=='t'):
                target=j
                
                # Getting controls
                ctrl=[]
                for k in range(len(circ_str)):
                    if (circ_str[k][i]=='o'):
                        ctrl.append(k)    
                circuit.ccx(ctrl[0], ctrl[1], target)               

    circuit.draw(output='mpl', filename=fname)  

    job = execute(circuit, simulator, shots=100)
    result = job.result()
    counts = result.get_counts(circuit)
    return counts
    