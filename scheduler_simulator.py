class SchedulerSimulator:
    def __init__(self, scheduler, steps):
        self.scheduler = scheduler
        self.steps = steps

    def run_simulation(self):
        self.scheduler.run(self.steps)
        self.scheduler.print_statistics()
