# -*- coding: utf-8 -*-
"""
Created on Sat May  4 14:11:03 2013

@author: david
"""
from copy import deepcopy


class Scoreboard:
    def __init__(self, fu, reg, data, inst):
        self.Mem = Memory(data, inst)
        self.FU = Units(fu)
        self.Reg = Registers(reg)
        self.Clock = Clock()
        self.Records = {}
        self.fetched = None
        self.halting = False
        self.halted = False
        self.icounter = 0
        self.imm = Immediate()

    def Cycle(self):
        #Increment the clock and update the FU countdowns
        self.Clock.increment()
        self.Mem.Work()
        for U in self.FU.All:
            if U.time > -1:
                self.FU.Int.time -= 1
        #Writebacks
        delres = []
        for dest,U in self.Reg.Reserve:
            if U.time == -1 and U.busy:
                delres.append(dest)
                U.op.write = self.Clock.time
                dest = U.result
                U.busy = False
                U.red1 = False
                U.red2 = False
                U.dat1 = None
                U.dat2 = None
                U.dest = None
                U.op = None
                U.result = None
                U.src1 = None
                U.src2 = None
        #Executions
        for U in self.FU.All:
            if U.time == 0:
                U.op.execute = self.Clock.time
        #Reads
        for U in self.FU.All:
            if U.op.read == -1:
                red = [U.red1, U.red2]
                src = [U.src1, U.src2]
                dat = [U.dat1, U.dat2]
                imm = [U.op.imm1, U.op.imm2]
                for x in range(2):
                    if not red[x]:
                        if src[x] is None:
                            red[x] = True
                        elif src[x] is self.imm:
                            red[x] = True
                            dat[x] = imm[x]
                        else:
                            if src[x] in self.Reg.Reserve:
                                U.op.raw = True
                            else:
                                red[x] = True
                                i = int(src[x][1:])
                                if src[x][0] == 'F':
                                    dat[x] = self.Reg.F[i]
                                else:
                                    dat[x] = self.Reg.R[i]
                if U.red1 and U.red2:
                    U.op.read = self.Clock.time
                    if U in self.FU.Div:
                        U.time = 50
                        U.result = float(U.dat1) / float(U.dat2)
                    if U in self.FU.Mul:
                        U.time = 30
                        U.result = float(U.dat1) * float(U.dat2)
                    if U in self.FU.Add:
                        U.time = 2
                        if U.op.instruction.Op == 'SUB.D':
                            U.result = float(U.dat1) - float(U.dat2)
                        else:
                            U.result = float(U.dat1) + float(U.dat2)
                    if U is self.FU.Int:
                        o = ['LW','SW','L.D','S.D']
                        if U.op.instruction.Op in o:
                            U.time = 100000
                            self.Mem.DataInst(U)
                        else:
                            U.time = 1
                            if U.op.instruction.Op in ['DADD','DADDI']:
                                U.result = U.dat1 + U.dat2
                            elif U.op.instruction.Op in ['DSUB','DSUBI']:
                                U.result = U.dat1 - U.dat2
                            elif U.op.instruction.Op in ['AND','ANDI']:
                                U.result = U.dat1 & U.dat2
                            elif U.op.instruction.Op in ['OR','ORI']:
                                U.result = U.dat1 | U.dat2
        while len(delres) > 0:
            del self.Reg.Reserve[delres.pop()]
        #Issue
        if not (self.fetched is None):  # If there is a fetched instruct
            fu = self.fetched.instruction.Unit
            issueto = None  # Figure out which FU the instruction needs
            if fu == 'Int':
                issueto = self.FU.Int
            elif fu == 'Add':
                for U in self.FU.Add:
                    if not U.busy:
                        issueto = U
                        break
            elif fu == 'Mul':
                for U in self.FU.Mul:
                    if not U.busy:
                        issueto = U
                        break
            elif fu == 'Div':
                for U in self.FU.Div:
                    if not U.busy:
                        issueto = U
                        break
            elif fu == 'J':
                pass
            elif fu == 'HLT':
                pass
            if issueto is None:
                if not (fu in ['J', 'HLT']):
                    self.fetched.struct = True
                elif fu == 'J':
                    pass
                elif fu == 'HLT':
                    self.fetched.issue = self.Clock.time
                    self.halting = True
                    self.fetched = None
            else:  # See if the destination is free
                dest = self.fetched.instruction.dest
                if dest is None:
                    pass
                else:
                    if dest in self.Reg.Reserve:
                        self.fetched.waw = True
                    else:
                        issueto.op = self.fetched
                        issueto.busy = True
                        issueto.src1 = issueto.op.src1
                        issueto.src2 = issueto.op.src2
                        issueto.dest = dest
                        self.Reg.Reserve[dest] = self.fetched
                        self.fetched.issue = self.Clock.time
                        self.fetched = None
        #Fetch
        if not self.halting:  # Fetch if not halting
            if self.fetched is None:  # If nothing waiting to issue
                self.fetched = self.Mem.Fetch()  # Mem fetch returns a rec
                if not (self.fetched is None):  # Mem fetch may delay
                    self.icounter += 1
                    self.fetched.ID = self.icounter
                    self.fetched.fetch = self.Clock.time
                    self.Records[self.icounter] = self.fetched
        #Check halt
        self.halted = self.halting and (self.fetched is None)
        self.halted = self.halted and (not self.FU.Int.busy)
        for U in self.FU.All:
            self.halted = self.halted and (not U.busy)
        self.halted = self.halted and (len(self.Reg.Reserve) == 0)
        #Return whether done
        return self.halted


class Record:
    def __init__(self):
        self.ID = -1
        self.instruction = None
        self.fetch = -1
        self.issue = -1
        self.read = -1
        self.execute = -1
        self.write = -1
        self.raw = False
        self.war = False
        self.waw = False
        self.struct = False


class FuncUnit:
    def __init__(self):
        self.time = -1
        self.busy = False
        self.op = None
        self.dest = None
        self.dat1 = None
        self.dat2 = None
        self.src1 = None
        self.src2 = None
        self.red1 = False
        self.red2 = False
        self.result = None


class Units:
    def __init__(self, FU):
        self.Int = FuncUnit()
        self.Add = [FuncUnit() for x in range(FU[0])]
        self.Mul = [FuncUnit() for x in range(FU[1])]
        self.Div = [FuncUnit() for x in range(FU[2])]
        self.All = []
        self.All.append(self.Int)
        for U in self.Add:
            self.All.append(U)
        for U in self.Mul:
            self.All.append(U)
        for U in self.Div:
            self.All.append(U)


class Clock:
    def __init__(self):
        self.time = 0

    def increment(self):
        self.time += 1


class Registers:
    def __init__(self, reg):
        self.R = reg
        self.F = [0 for x in range(32)]
        self.Reserve = {}


class Instruction:
    def __init__(self, inst):
        self.label = ''
        inst = inst.strip()
        self.inst = inst
        L = inst.split(':')
        if len(L) == 2:
            self.label = L[0].strip()
            inst = L[1].strip()
        C = inst.split(' ')
        self.Op = C[0]
        self.Unit = ''
        self.Xtime = 0
        self.dest = None
        self.imm1 = 0
        self.imm2 = 0
        if self.Op == 'L.D':
            pass
        elif self.Op == 'S.D':
            pass
        elif self.Op == 'LW':
            pass
        elif self.Op == 'SW':
            pass
        elif self.Op == 'HLT':
            pass
        elif self.Op == 'J':
            pass
        elif self.Op == 'BEQ':
            pass
        elif self.Op == 'BNE':
            pass
        elif self.Op == 'DADD':
            pass
        elif self.Op == 'DADDI':
            pass
        elif self.Op == 'DSUB':
            pass
        elif self.Op == 'DSUBI':
            pass
        elif self.Op == 'AND':
            pass
        elif self.Op == 'ANDI':
            pass
        elif self.Op == 'OR':
            pass
        elif self.Op == 'ORI':
            pass
        elif self.Op == 'ADD.D':
            pass
        elif self.Op == 'MUL.D':
            pass
        elif self.Op == 'DIV.D':
            pass
        elif self.Op == 'SUB.D':
            pass
        else:
            raise Exception('Invalid Instruction', inst)


class Memory:
    def __init__(self, data, inst, clock):
        self.Clock = clock
        self.PC = 0
        self.iWaiting = 0
        self.iCache = [-1,-1,-1,-1]  # 4 cached addresses
        self.dCache = [{'valid':False, 'TLU':-1, 'mem':[0,0]},
                       {'valid':False, 'TLU':-1, 'mem':[0,0]}
                       ]
        self.icreq = 0
        self.ichit = 0
        self.dcreq = 0
        self.dchit = 0
        self.iMem = []
        self.iLabels = {}
        for line in inst:
            self.iMem.append(Instruction(line))
        for i,ins in self.iMem:
            if ins.label != '':
                self.iLabels[ins.label] = i
        self.dMem = [None for i in range(0x100)]
        for val in data:
            self.dMem.append(val)
        self.tasks = []

    def Fetch(self):
        if self.iWaiting == 2:
            return None
        elif self.iWaiting == 1:
            self.iWaiting = 0
            out = Record()
            out.instruction = deepcopy(self.iMem[self.PC])
            self.PC += 1
            return out
        self.icreq += 1
        if self.PC in self.iCache[0:4]:
            self.ichit += 1
            out = Record()
            out.instruction = deepcopy(self.iMem[self.PC])
            self.PC += 1
            return out
        else:
            self.iWaiting = 2
            self.tasks.append(['ifetch',11])
            start = self.PC - (self.PC % 4)
            self.iCache = range(start,start+4)
            return None

    def Work(self):
        if len(self.tasks) > 0:
            if self.tasks[0][0] == 'ifetch':
                self.tasks[0][1] -= 1
                if self.tasks[0][1] == 0:
                    self.iWaiting == 1
            else:
                pass
    
    def DataInst(self,U):
        pass


class Immediate:
    def __init__(self):
        self.val = True
