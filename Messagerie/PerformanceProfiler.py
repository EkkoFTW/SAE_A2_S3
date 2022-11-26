import time

class PerformanceProfiler:
    Name = None
    timer = None
    nbRank = -1

    def __init__(self, Name):
        self.Name = Name
        self.timer = time.time()
        PerformanceProfiler.nbRank += 1
        print("  " * self.nbRank + str(self.Name + " : begin"))

    def __del__(self):
        print("  "*self.nbRank + str(self.Name) + " : " + str((time.time() - self.timer)*1000))
        PerformanceProfiler.nbRank -= 1

