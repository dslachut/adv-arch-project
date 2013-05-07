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
            #data = map(lines, lambda x: int(x,2))
            for line in lines:
                data.append(int(line,2))
        with open(regFname) as FILE:
            lines = FILE.readlines()
            #reg = map(lines, lambda x: int(x,2))
            for line in lines:
                reg.append(int(line,2))
        with open(configFname) as FILE:
            for line in FILE:
                FU.append(int(line))
        #self.memory = Memory(data,inst)
        self.scoreboard = Scoreboard(FU,reg,data,inst)
    
    def Run(self,fname='result.txt'):
        print 'Running simulation'
        done = False
        try:
            while not done:
                done = self.scoreboard.Cycle()
        except KeyboardInterrupt:
            print self.scoreboard.Clock.time
        with open(fname,'w') as FILE:
            FILE.write('\tInstruction\tFetch\tIssue\tRead\tExec\tWrite\t')
            FILE.write('RAW\tWAR\tWAW\tStruct\n')
            for k in sorted(self.scoreboard.Records.iterkeys()):
                FILE.write(str(self.scoreboard.Records[k]))
                FILE.write('\n')
            FILE.write('Total number of access requests ')
            FILE.write('for instruction cache: ')
            FILE.write(str(self.scoreboard.Mem.icreq))
            FILE.write('\nNumber of instruction cache hits: ')
            FILE.write(str(self.scoreboard.Mem.ichit))
            FILE.write('\nTotal number of access requests for data cache: ')
            FILE.write(str(self.scoreboard.Mem.dcreq))
            FILE.write('\nNumber of data cache hits: ')
            FILE.write(str(self.scoreboard.Mem.dchit))
            FILE.write('\n')