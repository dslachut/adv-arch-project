from Scoreboard2 import Scoreboard
#from Memory import Memory

class Simulation:
    def __init__(self,instFname,dataFname,regFname,configFname):
        print 'Setting up Simulation'
        FU = []
        reg = []
        data = []
        inst = []
        with open(instFname) as FILE:
            inst = FILE.readlines()
        with open(dataFname) as FILE:
            lines = FILE.readlines()
            data = map(lines, lambda x: int(x,2))
        with open(regFname) as FILE:
            lines = FILE.readlines()
            reg = map(lines, lambda x: int(x,2))
        with open(configFname) as FILE:
            for line in FILE:
                FU.append(int(line))
        #self.memory = Memory(data,inst)
        self.scoreboard = Scoreboard(FU,reg,data,inst)
    
    def Run(self):
        done = False
        while not done:
            done = self.scoreboard.Cycle()