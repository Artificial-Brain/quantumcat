# (C) Copyright Artificial Brain 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from quantumcat.utils import constants, helper
from qiskit import Aer, execute, IBMQ
from qiskit.providers.ibmq import least_busy
import cirq
import cirq.ionq as ionq
from braket.devices import LocalSimulator


def on_qiskit(q_circuit, simulator_name, repetitions, api, device_name,
              hub='ibm-q', group=None, project=None):
    """
    Initializes backend for running the circuit in the IBM Qiskit device.
    
    Args:
        q_circuit: quantum circuit to be executed.
        simulator_name: simulator name as string input, where the circuit is to be simulated.
        repetitions: number of executions of the circuit.
        api: API token as string input, linked with the IBMQ account.
        device_name: name of IBM quantum devices where the execution takes place, as string input.
                    The standard list of devices are provided in the IBMQ account.
        hub: IBM Quantum hub name
        group: gives access to all of IBM Quantum devices available to all users. Input to be given as "open".
        project: gives access to all of IBM Quantum devices available to all users. Input to be given as "main".

    Returns:
        counts of the state or the statevector of the output, depending on the input.
    """
    if api is None:
        backend = Aer.get_backend(simulator_name)
    else:
        IBMQ.save_account(api, overwrite=True)
        IBMQ.load_account()
        provider = IBMQ.get_provider(hub=hub, group=group, project=project)
        backend = least_busy(provider.backends(simulator=False)) if device_name is None \
            else provider.get_backend(device_name)

    results = execute(q_circuit, backend, shots=repetitions).result()

    if simulator_name == constants.DEFAULT_SIMULATOR:
        return results.get_counts()
    elif simulator_name == constants.STATEVECTOR_SIMULATOR:
        return results.get_statevector()


def on_cirq(q_circuit, simulator_name, repetitions, api, operations):
    """
    Initializes backend for running the circuit in the Google Cirq device.
    
    Args:
        q_circuit: quantum circuit to be executed.
        simulator_name: simulator name as string input, where the circuit is to be simulated.
        repetitions: number of executions of the circuit.
        api: API name linked with the Google Cirq account.
        operations: 

    Returns:
        Statevector of the output.
    """
    simulator = cirq.Simulator()
    if simulator_name == constants.DEFAULT_SIMULATOR:
        result = simulator.run(q_circuit, repetitions=repetitions)
        qubits_index = helper.measure_qubits_index(operations)
        if len(qubits_index) > 0:
            return helper.cirq_measurment_in_reverse(result.multi_measurement_histogram
                                              (keys=qubits_index, fold_func=helper.bitstring))
        else:
            return helper.cirq_measurment_in_reverse(result.histogram(key='result', fold_func=helper.bitstring))
    elif simulator_name == constants.STATEVECTOR_SIMULATOR:
        return simulator.simulate(q_circuit).final_state_vector


# Need testing
def on_ionq(q_circuit, repetitions, api, default_target, operations):
    service = ionq.Service(api_key=api, default_target=default_target)
    result = service.run(q_circuit, repetitions=repetitions)
    qubits_index = helper.measure_qubits_index(operations)
    if len(qubits_index) > 0:
        return helper.cirq_measurment_in_reverse(result.multi_measurement_histogram
                                              (keys=qubits_index, fold_func=helper.bitstring))
    else:
        return helper.cirq_measurment_in_reverse(result.histogram(key='result', fold_func=helper.bitstring))


def on_braket(q_circuit, simulator_name, repetitions, api):
    """
    Initializes backend for running the circuit in the AWS Braket device.

    Args:
        q_circuit: quantum circuit to be executed.
        simulator_name: simulator name as string input, where the circuit is to be simulated.
        repetitions: number of executions of the circuit.
        api: API token as string input.

    Returns:
        Statevector of the output.
    """
    if simulator_name == constants.DEFAULT_SIMULATOR:
        results = LocalSimulator().run(q_circuit, shots=repetitions).result()
        return dict(results.measurement_counts)
    elif simulator_name == constants.STATEVECTOR_SIMULATOR:
        return LocalSimulator().run(q_circuit.state_vector(), shots=0).result().values[0]
