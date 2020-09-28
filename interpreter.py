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
            elif (operation=='Z'):
                circuit.z(j)
            
            # Pauli Y
            elif (operation=='Y'):
                circuit.y(j)
            
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
            
            # Ctrl operations
            elif (operation=='C'):
                
                # Getting control
                for k in range(len(circ_str)):
                    if (circ_str[k][i]=='o'):
                        ctrl=k
                
                # CNOT
                if (qbit[i+1]=='X'):
                    target=j
                    circuit.cx(ctrl, target)
                    

    circuit.draw(output='mpl', filename=fname)  

    job = execute(circuit, simulator, shots=100)
    result = job.result()
    counts = result.get_counts(circuit)
    return counts
    