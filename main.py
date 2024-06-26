from task import Task
from EASH import EASH
from scheduler_simulator import SchedulerSimulator

def main():
    steps = 1000  # Number of steps to ensure sufficient task execution
    number_of_tasks = 1000  # Number of tasks

    # Initialize EASH scheduler
    input_dim = 50  # Adjust this value based on the state representation size
    output_dim = 3  # Three possible actions: MLFQ, EDF, WRR
    eash = EASH(input_dim, output_dim)

    # Add tasks
    for i in range(number_of_tasks):
        task_id = i + 1
        computation_time = 5 - (i % 5)
        deadline = 10 + i * 5
        priority = (i % 3) + 1
        arrival_time = i

        task = Task(task_id, computation_time, deadline, priority, arrival_time)
        eash.add_task(task)

    # Run simulation
    simulator = SchedulerSimulator(eash, steps)
    simulator.run_simulation()

if __name__ == "__main__":
    main()
