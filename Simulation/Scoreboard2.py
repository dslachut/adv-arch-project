# -*- coding: utf-8 -*-
"""
Created on Sat May  4 14:11:03 2013

@author: david
"""
from copy import deepcopy


class Scoreboard:
    def __init__(self, fu, reg, data, inst):
        self.imm = Immediate()
        self.Clock = Clock()
        self.Mem = Memory(data, inst, self.Clock, self.imm)
        self.FU = Units(fu)
        self.Reg = Registers(reg)
        self.Records = {}
        self.fetched = None
        self.halting = False
        self.halted = False
        self.stalled = False
        self.icounter = 0
    
    def Flush(self):
        self.halted = False
        self.halting = False
        self.fetched = None

    def Cycle(self):
        #Increment the clock and update the FU countdowns
        #print self.Reg.Reserve
        self.Clock.increment()
        self.Mem.Work()
        for U in self.FU.All:
            if U.time > -1:
                U.time -= 1
        #Writebacks
        delres = []
        notbusy = []
        for dest,U in self.Reg.Reserve.iteritems():
            #print dest,'/', U
            if U.time == -1 and U.busy and U.red1 and U.red2:
                if U.op.instruction.Op in \
                ['LW','DADD','DADDI','DSUB','DSUBI',
                 'AND','ANDI','OR','ORI']:
                     regnum = int(U.dest[1:])
                     self.Reg.R[regnum] = U.result
                delres.append(dest)
                U.op.write = self.Clock.time
                #dest = U.result
                notbusy.append(U)
                U.red1 = False
                U.red2 = False
                U.dat1 = None
                U.dat2 = None
                U.dest = None
                U.op = None
                U.result = None
                U.src1 = None
                U.src2 = None
                U.time = -1
        #Executions
        for U in self.FU.All:
            if U.time == 0:
                U.op.execute = self.Clock.time
                #print U.op.ID, U.op.instruction.Op, U.op.execute, 'X'
            #elif U.op is not None:
            #    print U.time, U.op.instruction.Op
        #Reads
        if self.FU.Bra.op is None:
            pass
        else:
            U = self.FU.Bra
            if U.op.read == -1:
                if not U.red1:
                    if U.src1 in self.Reg.Reserve:
                        U.op.raw = True
                    else:
                        U.red1 = True
                        i = int(U.src1[1:])
                        if U.src1[0] == 'F':
                            U.dat1 = self.Reg.F[i]
                        else:
                            U.dat1 = self.Reg.R[i]
                if not U.red2:
                    if U.src2 in self.Reg.Reserve:
                        U.op.raw = True
                    else:
                        U.red2 = True
                        i = int(U.src2[1:])
                        if U.src2[0] == 'F':
                            U.dat2 = self.Reg.F[i]
                        else:
                            U.dat2 = self.Reg.R[i]
                if U.red1 and U.red2:
                    U.op.read = self.Clock.time
                    #print U.op.ID, U.op.instruction.Op, U.op.read, 'R'
                    if ((U.op.instruction.Op=='BNE') and \
                    (U.dat1!=U.dat2)) or ((U.op.instruction.Op=='BEQ') \
                    and (U.dat1==U.dat2)):
                        self.Mem.Retarget(U.op.instruction.target)
                        self.Flush()
                    #self.stalled = False
                    notbusy.append(U)
                    delres.append(U.dest)
                    U.red1 = False
                    U.red2 = False
                    U.dat1 = None
                    U.dat2 = None
                    U.dest = None
                    U.op = None
                    U.result = None
                    U.src1 = None
                    U.src2 = None
                    U.time = -1
        for U in self.FU.All:
            #print U.op, '!'
            if U.op is None:
                continue
            if U.op.read == -1:
                #red = [U.red1, U.red2]
                #src = [U.src1, U.src2]
                #dat = [U.dat1, U.dat2]
                imm = [U.op.instruction.imm1, U.op.instruction.imm2]
                if not U.red1:
                    #print U.op.ID, '!'
                    if U.src1 is None:
                        U.red1 = True
                    elif self.imm.__eq__(U.src1):
                        #print '!'
                        U.red1 = True
                        U.dat1 = imm[0]
                    else:
                        #print src[x]
                        if (U.src1 in self.Reg.Reserve) and \
                        not (self.Reg.Reserve[U.src1] == U):
                            U.op.raw = True
                            #print '!'
                        else:
                            U.red1 = True
                            i = int(U.src1[1:])
                            if U.src1[0] == 'F':
                                U.dat1 = self.Reg.F[i]
                            else:
                                U.dat1 = self.Reg.R[i]
                if not U.red2:
                    #print U.src2
                    if U.src2 is None:
                        U.red2 = True
                    elif self.imm.__eq__(U.src2):
                        #print '!'
                        U.red2 = True
                        U.dat2 = imm[1]
                    else:
                        #print src[x]
                        if (U.src2 in self.Reg.Reserve) and \
                        not (self.Reg.Reserve[U.src2] == U):
                            U.op.raw = True
                            #print '!'
                        else:
                            U.red2 = True
                            i = int(U.src2[1:])
                            if U.src2[0] == 'F':
                                U.dat2 = self.Reg.F[i]
                            else:
                                U.dat2 = self.Reg.R[i]
                if U.red1 and U.red2:
                    #print U.op.read
                    #print U.dat1, U.dat2
                    U.op.read = self.Clock.time
                    #print U.op.ID, U.op.instruction.Op, U.op.read, 'R'
                    #print U.op.read
                    if U in self.FU.Div:
                        U.time = 50
                        try:
                            U.result = float(U.dat1) / float(U.dat2)
                        except:
                            U.result = 0
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
                            self.Mem.DataInst(U,self.Reg)
                        else:
                            U.time = 1
                            if U.op.instruction.Op in ['DADD','DADDI']:
                                U.result = U.dat1 + U.dat2
                                print U.result
                            elif U.op.instruction.Op in ['DSUB','DSUBI']:
                                U.result = U.dat1 - U.dat2
                            elif U.op.instruction.Op in ['AND','ANDI']:
                                U.result = U.dat1 & U.dat2
                            elif U.op.instruction.Op in ['OR','ORI']:
                                U.result = U.dat1 | U.dat2
        #Issue
        if not (self.fetched is None):# and not self.stalled:
            fu = self.fetched.instruction.Unit
            #print fu
            issueto = None  # Figure out which FU the instruction needs
            if fu == 'Int':
                if not self.FU.Int.busy:
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
                self.Mem.Retarget(self.fetched.instruction.target)
                self.stalled = True
                self.fetched.issue  = self.Clock.time
                self.fetched = None
            elif fu == 'HLT':
                pass
            elif fu in ['BNE','BEQ']:
                if not self.FU.Bra.busy:
                    issueto = self.FU.Bra
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
                #print issueto
                if dest is None and not (fu in ['BNE','BEQ']) and\
                not (self.fetched.instruction.Op in ['SW','S.D']):
                    pass
                else:
                    if (not (dest is None)) and \
                    (dest in self.Reg.Reserve) and \
                    not (fu in ['S.D','SW']):
                    #if dest in self.Reg.Reserve:
                        #if fu == 'BNE': print dest
                        self.fetched.waw = True
                    else:
                        issueto.op = self.fetched
                        issueto.busy = True
                        issueto.src1 = issueto.op.instruction.src1
                        issueto.src2 = issueto.op.instruction.src2
                        issueto.dest = dest
                        self.Reg.Reserve[dest] = issueto
                        self.fetched.issue = self.Clock.time
                        self.fetched = None
                        #print issueto.op.ID, issueto.op.instruction.Op, 
                        #print self.Clock.time, 'I'
        #Fetch
        if not self.halting and not self.stalled:  # Fetch if not halting
            if self.fetched is None:  # If nothing waiting to issue
                self.fetched = self.Mem.Fetch()  # Mem fetch returns a rec
                if not (self.fetched is None):  # Mem fetch may delay
                    self.icounter += 1
                    self.fetched.ID = self.icounter
                    self.fetched.fetch = self.Clock.time
                    self.Records[self.icounter] = self.fetched
                    print self.fetched.ID, self.fetched.instruction.Op, 
                    print self.Clock.time, 'F'
        #Bookeeping
        for U in notbusy:
            U.busy = False
        while len(delres) > 0:
            del self.Reg.Reserve[delres.pop()]       
        #if self.FU.Bra.busy: self.stalled = True
        self.stalled = self.FU.Bra.busy
        #Check halt
        self.halted = self.halting and (self.fetched is None)
        for U in self.FU.All:
            self.halted = self.halted and (not U.busy)
        self.halted = self.halted and (len(self.Reg.Reserve) == 0)
        #print self.Reg.Reserve
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
    
    def __str__(self):
        outs = []
        outs.append(self.instruction.inst)
        for t in [self.fetch,self.issue,self.read,self.execute,self.write]:
            if t > -1:
                outs.append(' '+str(t))
            else: outs.append('')
        for h in [self.raw,self.war,self.waw,self.struct]:
            if h:
                outs.append(' Y')
            else:
                outs.append(' N')
        if self.instruction.label == '':
            outs[0] = '    ' + outs[0]
        if (self.instruction.Op=='HLT') and (self.instruction.label==''):
            outs[0] = outs[0] + '\t\t'
        elif self.instruction.Op in ['HLT','J']:
            outs[0] = outs[0] + '\t'
        return '\t'.join(outs)


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
        self.Bra = FuncUnit()
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
    def __init__(self, inst,imm):
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
        self.dest = None
        self.imm1 = 0
        self.imm2 = 0
        self.src1 = None
        self.src2 = None
        self.target = None
        #print "'",self.Op,"'"
        if self.Op in ['LW','L.D']:
            self.Unit = 'Int'
            O = inst.split(',')
            self.dest = O[0].strip()[-2:]
            Os = O[1].strip().split('(')
            self.imm1 = int(Os[0].strip())
            self.src1 = imm
            self.src2 = Os[1].strip()[0:2]
        elif self.Op in ['SW','S.D']:
            self.Unit = 'Int'
            O = inst.split(',')
            self.target = O[0].strip()[-2:]
            Os = O[1].strip().split('(')
            self.imm1 = int(Os[0].strip())
            self.src1 = imm
            self.src2 = Os[1].strip()[0:2]
        elif self.Op == 'HLT':
            self.Unit = 'HLT'
        elif self.Op == 'J':
            O = inst.split()
            self.target = O[-1].strip()
            self.Unit = 'J'
        elif self.Op in ['BEQ','BNE']:
            O = inst.split(',')
            self.target = O[2].strip()
            self.src2 = O[1].strip()
            self.src1 = O[0].strip()[-2:]
            self.Unit = self.Op
        elif self.Op in ['DADD','DSUB','AND','OR']:
            O = inst.split(',')
            self.src2 = O[2].strip()
            self.src1 = O[1].strip()
            self.dest = O[0].strip()[-2:]
            self.Unit = 'Int'
        elif self.Op in ['DADDI','DSUBI','ANDI','ORI']:
            O = inst.split(',')
            self.src2 = imm
            self.imm2 = int(O[2].strip())
            self.src1 = O[1].strip()
            self.dest = O[0].strip()[-2:]
            self.Unit = 'Int'
        elif self.Op in ['ADD.D','SUB.D']:
            O = inst.split(',')
            self.src2 = O[2].strip()
            self.src1 = O[1].strip()
            self.dest = O[0].strip()[-2:]
            self.Unit = 'Add'
        elif self.Op == 'MUL.D':
            O = inst.split(',')
            self.src2 = O[2].strip()
            self.src1 = O[1].strip()
            self.dest = O[0].strip()[-2:]
            self.Unit = 'Mul'
        elif self.Op == 'DIV.D':
            O = inst.split(',')
            self.src2 = O[2].strip()
            self.src1 = O[1].strip()
            self.dest = O[0].strip()[-2:]
            self.Unit = 'Div'
        else:
            raise Exception('Invalid Instruction', inst)


class Memory:
    def __init__(self, data, inst, clock, imm):
        self.Clock = clock
        self.Imm = imm
        self.PC = 0
        self.iWaiting = 0
        self.iCache = [-1 for i in range(16)]  # 16 cached addresses
        self.icreq = 0
        self.ichit = 0
        self.dcreq = 0
        self.dchit = 0
        self.iMem = []
        self.iLabels = {}
        for line in inst:
            self.iMem.append(Instruction(line,self.Imm))
        for i,ins in enumerate(self.iMem):
            if ins.label != '':
                self.iLabels[ins.label] = i
        self.dMem = [None for i in range(0x100)]
        for val in data:
            self.dMem.append(val)
        self.tasks = []
        self.dCache = DCache(clock)#,self.dMem)
        self.adjust = []

    def Fetch(self):
        #print self.PC
        if self.iWaiting == 2:
            return None
        elif self.iWaiting == 1:
            self.iWaiting = 0
            out = Record()
            out.instruction = deepcopy(self.iMem[self.PC])
            self.PC += 1
            return out
        self.icreq += 1
        if self.PC in self.iCache:
            self.ichit += 1
            out = Record()
            out.instruction = deepcopy(self.iMem[self.PC])
            self.PC += 1
            return out
        else:
            print 'miss'
            self.iWaiting = 2
            #print self.Clock.time, '!!!'
            if (len(self.tasks) > 0)and(self.tasks[0][2]>=self.Clock.time):
                self.tasks = [['ifetch',11,self.Clock.time]] + self.tasks
                for task in self.tasks:
                    if task[0] == 'dfetch':
                        task[3].time += 11
            else:
                self.tasks.append(['ifetch',11,self.Clock.time])
            start = self.PC - (self.PC % 4)
            b = (self.PC % 16) - (self.PC % 4)
            for x in range(start,start+4):
                self.iCache[b] = x
                b += 1
            return None
    
    def Retarget(self,label):
        if label in self.iLabels:
            #self.adjust.append(self.iLabels[label])
            self.PC = self.iLabels[label]
            print self.PC

    def Work(self):
        #print 'memwork', len(self.tasks)
        if len(self.tasks) > 0:
            if self.tasks[0][0] == 'ifetch':
                self.tasks[0][1] -= 1
                if self.tasks[0][1] == 0:
                    self.iWaiting = 1
                    self.tasks.remove(self.tasks[0])
            else:
                self.tasks[0][1] -= 1
                if self.tasks[0][1] == 0:
                    self.tasks.remove(self.tasks[0])
        #if len(self.adjust) > 0:
        #    self.PC = self.adjust[0]
        #    self.adjust.remove(self.adjust[0])
        #    print self.PC
    
    def DataInst(self,U,reg):
        op = U.op.instruction.Op
        addr = U.dat1 + U.dat2
        print U.dat1, U.dat2
        if op == 'LW':
            outTime = 1
            self.dcreq += 1
            U.result = self.dMem[addr]
            if self.dCache.hit(addr):
                outTime +=1
                self.dchit += 1
            else:
                busTime = self.dCache.replace(addr)
                outTime += busTime
                self.tasks.append(['dfetch',busTime,self.Clock.time+1,U])
            U.time = outTime
        elif op == 'L.D':
            self.dcreq += 2
            outTime = 2
            busTime = 0
            U.result = int(bin(self.dMem[addr])[2:] + \
            bin(self.dMem[addr+1])[2:],2)
            if self.dCache.hit(addr):
                outTime += 1
                self.dchit += 1
            else:
                busTime = self.dCache.replace(addr)
                outTime += busTime
                self.tasks.append(['dfetch',busTime,self.Clock.time+1,U])
            if self.dCache.hit(addr+1):
                #if busTime == 0:
                    outTime += 0
                    self.dchit += 1
            else:
                busTime = self.dCache.replace(addr+1)
                outTime += busTime
                self.tasks.append(['dfetch',busTime,self.Clock.time+1,U])
            U.time = outTime
            #print self.Clock.time, '!!'
        elif op == 'SW':
            outTime = 1
            self.dcreq += 1
            target = U.op.instruction.target
            self.dMem[addr] = reg.R[int(target[1:])]
            if self.dCache.hit(addr):
                self.dCache.Dirty(addr)
                outTime += 1
                self.dchit += 1
            else:
                busTime = self.dCache.replace(addr)
                outTime += busTime
                self.tasks.append((['dfetch',busTime,self.Clock.time+1,U]))
                self.dCache.Dirty(addr)
            U.time = outTime
        elif op == 'S.D':
            self.dcreq += 2
            outTime = 2
            busTime = 0
            target = U.op.instruction.target
            v = reg.F[int(target[1:])]
            v1 = bin(v)[2:]
            v1 = ('0'*(64 - len(v1))) + v1
            self.dMem[addr] = int(v1[:32],2)
            self.dMem[addr+1] = int(v1[32:],2)
            if self.dCache.hit(addr):
                outTime += 1
                self.dchit += 1
                self.dCache.Dirty(addr)
            else:
                busTime = self.dCache.replace(addr)
                outTime += busTime
                self.tasks.append(['dfetch',busTime,self.Clock.time+1,U])
                self.dCache.Dirty(addr)
            if self.dCache.hit(addr+1):
                outTime += 0
                self.dchit += 1
                self.dCache.Dirty(addr+1)
            else:
                busTime = self.dCache.replace(addr+1)
                outTime += busTime
                self.tasks.append(['dfetch',busTime,self.Clock.time+1,U])
                self.dCache.Dirty(addr+1)
            U.time = outTime


class DCache:
    def __init__(self,clock):#,mem):
        self.blocks = [[-1]*4]*4
        self.dirty = [False]*4
        self.TLU = [-1]*4
        self.Clock = clock
        #self.Mem = mem
    
    def replace(self, addr):
        time = 0
        repl = -1
        # Pick cache block
        assoc = (addr % 8) / 4
        if self.TLU[assoc] > self.TLU[assoc+2]:
            repl = assoc + 2
        else: 
            repl = assoc
        # If dirty, write it back
        if self.dirty[repl]:
            time += 12
        # Read in new data
        blockstart = addr - (addr % 4)
        self.blocks[repl] = range(blockstart,blockstart+4)
        time += 12
        # Mark clean
        self.dirty[repl] = False
        self.TLU[repl] = self.Clock.time + time
        return time
    
    def hit(self, addr):
        for i,block in enumerate(self.blocks):
            if addr in block:
                self.TLU[i] = self.Clock.time
                return True
        return False
    
    def Dirty(self,addr):
        for i, block in enumerate(self.blocks):
            if addr in block:
                self.dirty[i] = True


class StoreDest:
    def __init__(self):
        self.val = "I am a Dummy Object, AMA!"

class Immediate:
    def __init__(self):
        self.val = True
        self.val2 = {}
        self.val3 = [1,2,False,{}]
    def __eq__(self,other):
        try:
            return (self.val and other.val)
        except:
            return False
