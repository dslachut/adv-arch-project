# -*- coding: utf-8 -*-
"""
Created on Sat May  4 14:11:03 2013

@author: david
"""

class FuncUnit:
    def __init__(self):
        self.time = -1
        self.busy = False
        self.op   = None
        self.dest = None
        self.src1 = None
        self.src2 = None
        self.red1 = True
        self.red2 = True
        
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
        L = inst.split(':')
        if len(L) == 2:
            self.label = L[0].strip()
            inst = L[1].strip()
        C = inst.split(' ')
        self.Op = C[0]
        if self.Op == 'L.D':
            pass
        elif self.Op == 'S.D':
            pass
        elif self.Op == 'LW':
            pass
        elif self.Op == 'SW':
            pass
        elif self.Op = 'HLT':
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