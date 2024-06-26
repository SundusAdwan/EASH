from MLFQ import MLFQ
from EDF import EDF
from WRR import WRR
from PPOAgent import PPOAgent
import copy

class EASH:
    def __init__(self, input_dim, output_dim):
        self.mlfq = MLFQ(3)
        self.edf = EDF()
        self.wrr = WRR()
        self.ppo_agent = PPOAgent(input_dim, output_dim)
        self.tasks = []
        self.time = 0
        self.states = []
        self.actions = []
        self.rewards = []
        self.input_dim = input_dim

        # Metrics
        self.total_waiting_time = 0
        self.total_turnaround_time = 0
        self.total_response_time = 0
        self.total_context_switches = 0
        self.total_completed_tasks = 0
        self.total_missed_tasks = 0
        self.cpu_busy_time = 0
        self.max_turnaround_time = 0
        self.worst_case_execution_time = 0

        self.current_task = None

    def add_task(self, task):
        self.tasks.append(copy.deepcopy(task))
        self.mlfq.add_task(copy.deepcopy(task))
        self.edf.add_task(copy.deepcopy(task))
        self.wrr.add_task(copy.deepcopy(task))

    def schedule(self):
        state = []
        for task in self.tasks:
            state.extend([task.id, task.computation_time, task.deadline, task.priority, task.arrival_time])

        # Ensure the state matches the required dimension
        if len(state) < self.input_dim:
            state.extend([0] * (self.input_dim - len(state)))
        elif len(state) > self.input_dim:
            state = state[:self.input_dim]

        action = self.ppo_agent.choose_action(state)
        task = None

        if action == 0:
            task = self.mlfq.get_next_task()
        elif action == 1:
            task = self.edf.get_next_task()
        elif action == 2:
            task = self.wrr.get_next_task()

        reward = 0
        if task:
            if self.current_task is not task:
                self.total_context_switches += 1
                self.current_task = task

            if task.start_time is None:
                task.set_start_time(self.time)
                self.total_response_time += task.response_time()

            task.remaining_time -= 1
            self.cpu_busy_time += 1
            reward = 1  # This can be adjusted based on performance criteria
            if task.remaining_time <= 0:
                task.set_finish_time(self.time + 1)  # +1 because the task finished in this cycle
                waiting_time = task.waiting_time()
                turnaround_time = task.turnaround_time()
                self.total_waiting_time += waiting_time
                self.total_turnaround_time += turnaround_time
                self.max_turnaround_time = max(self.max_turnaround_time, turnaround_time)
                self.worst_case_execution_time = max(self.worst_case_execution_time, task.computation_time)
                self.total_completed_tasks += 1
                if task in self.tasks:  # Ensure task is in the list before removing
                    self.tasks.remove(task)
                self.current_task = None
                # Check if task missed its deadline
                if self.time + 1 > task.deadline:
                    self.total_missed_tasks += 1

        # Collect data
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)

    def run(self, steps):
        for _ in range(steps):
            self.schedule()
            self.time += 1
            self.mlfq.run(1)  # Run MLFQ for one time unit
            self.edf.run(1)   # Run EDF for one time unit
            self.wrr.run(1)   # Run WRR for one time unit

        # Update PPO model after collecting data
        self.ppo_agent.update(self.states, self.actions, self.rewards)

    def print_statistics(self):
        throughput = self.total_completed_tasks / self.time
        cpu_utilization = (self.cpu_busy_time / self.time) * 100 if self.time > 0 else 0
        task_completion_percentage = (self.total_completed_tasks / (self.total_completed_tasks + self.total_missed_tasks)) * 100 if (self.total_completed_tasks + self.total_missed_tasks) > 0 else 100

        print(f"Total Context Switches: {self.total_context_switches}")
        print(f"Total Waiting Time: {self.total_waiting_time * 1e9:.0f} ns")
        print(f"Total Turnaround Time: {self.total_turnaround_time * 1e9:.0f} ns")
        print(f"Total Response Time: {self.total_response_time * 1e9:.0f} ns")
        print(f"Maximum Turnaround Time: {self.max_turnaround_time * 1e9:.0f} ns")
        print(f"Worst Case Execution Time: {self.worst_case_execution_time * 1e9:.0f} ns")
        print(f"Throughput: {throughput:.2f} tasks/unit time")
        print(f"CPU Utilization: {cpu_utilization:.2f}%")
        print(f"Task Completion Percentage: {task_completion_percentage:.2f}%")
        print(f"Total Missed Tasks: {self.total_missed_tasks}")

        print("\nCPU Load Over Time:")
        print(f"Time CPU was busy: {self.cpu_busy_time * 1e9:.0f} ns")
        print(f"Total simulation time: {self.time * 1e9:.0f} ns")

        print("\nMLFQ Statistics:")
        self.mlfq.print_statistics()
        print("\nEDF Statistics:")
        self.edf.print_statistics()
        print("\nWRR Statistics:")
        self.wrr.print_statistics()
