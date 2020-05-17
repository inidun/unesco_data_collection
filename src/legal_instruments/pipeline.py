
class Pipeline():

    def __init__(self, args=None):
        self.tasks = args or []

    def add(self, task, *payload):
        self.tasks.append(lambda x: task(x, *payload))
        return self

    def apply(self, target):

        for task in self.tasks:
            target = task(target)

        return target


