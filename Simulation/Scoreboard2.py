# -*- coding: utf-8 -*-
"""
Created on Sat May  4 14:11:03 2013

@author: david
"""

class Scoreboard:
    def __init__(self,fu,reg,data,inst):
        self.Mem = Memory(data,inst)
        self.FU = Units(fu)
        self.Reg = Registers(reg)
        self.Clock = Clock()
        self.Records = {}
        self.fetched = None
        self.halting = False
        self.halted = False
        self.icounter = 0
    def Cycle(self):
        #Increment the clock and update the FU countdowns
        self.Clock.increment()
        if self.FU.Int.time > -1:
           self.FU.Int.time -= 1
        for i in len(self.FU.Add):
            if self.FU.Add[i].time > -1:
                self.FU.Add[i].time -= 1
        for i in len(self.FU.Mul):
            if self.FU.Mul[i].time > -1:
                self.FU.Mul[i].time -= 1
        for i in len(self.FU.Div):
            if self.FU.Div[i].time > -1:
                self.FU.Div[i].time -= 1
        #Writebacks
        #Executions
        #Reads
        #Issue
        if not (self.fetched is None):
            fu = self.fetched.instruction.Unit
            issueto = None
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
                if not (fu in ['J','HLT']):
                    self.fetched.struct = True
                elif fu == 'J':
                    pass
                elif fu == 'HLT':
                    self.fetched.issue = self.Clock.time
                    self.halting = True
                    self.fetched = None
            else:
                issueto.op = self.fetched
                issueto.busy = True
                self.fetched.issue = self.Clock.time
        #Fetch
        if not self.halting:#Fetch if not halting
            if self.fetched is None:#If nothing waiting to issue
                self.fetched = self.Mem.fetch()#Mem fetch returns a record
                if not (self.fetched is None):#Mem fetch may delay
                    self.icounter +=1
                    self.fetched.ID = self.icounter
                    self.fetched.fetch = self.Clock.time
                    self.Records[self.icounter] = self.fetched
        #Check halt
        self.halted = self.halting and (self.fetched is None)
        self.halted = self.halted and (not self.FU.Int.busy)
        for U in self.FU.Add:
            self.halted = self.halted and (not U.busy)
        for U in self.FU.Div:
            self.halted = self.halted and (not U.busy)
        for U in self.FU.Mul:
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
        self.op   = None
        self.dest = None
        self.src1 = None
        self.src2 = None
        self.red1 = False
        self.red2 = False
        
class Units:
    def __init__(self,FU):
        self.Int = FuncUnit()
        self.Add = [FuncUnit() for x in range(FU[0])]
        self.Mul = [FuncUnit() for x in range(FU[1])]
        self.Div = [FuncUnit() for x in range(FU[2])]

class Clock:
    def __init__(self):
        self.time = 0
    def increment(self):
        self.time += 1

class Registers:
    def __init__(self,reg):
        self.R = reg
        self.F = [0 for x in range(32)]
        self.Reserve = {}

class Instruction:
    def __init__(self,inst):
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
            raise Exception('Invalid Instruction',inst)
            
class Memory:
    def __init__(self,data,inst):
        pass