class Task:
    def __init__(self, id, computation_time, deadline, priority, arrival_time):
        self.id = id
        self.computation_time = computation_time
        self.deadline = deadline
        self.priority = priority
        self.arrival_time = arrival_time
        self.remaining_time = computation_time
        self.start_time = None
        self.finish_time = None

    def __lt__(self, other):
        return self.deadline < other.deadline

    def set_start_time(self, start_time):
        if self.start_time is None:
            self.start_time = start_time

    def set_finish_time(self, finish_time):
        self.finish_time = finish_time

    def waiting_time(self):
        if self.start_time is not None:
            return self.start_time - self.arrival_time
        return 0

    def turnaround_time(self):
        if self.finish_time is not None:
            return self.finish_time - self.arrival_time
        return 0

    def response_time(self):
        if self.start_time is not None:
            return self.start_time - self.arrival_time
        return 0
    
    def __str__(self) -> str:
        return f'ID: {self.id}, Priority: {self.priority}, Arrival: {self.arrival_time}, Start: {self.start_time}, Finish: {self.finish_time}'
