# MAssemble, the M-Machine Assembler
# Assembles .mmc files into .bin.
# Currently only supports up to one page (1024 instructions) at a time

import sys
from os import path

if len(sys.argv) < 2:
    print('Usage: python massemble.py [source].mmc')
    sys.exit(0)
    
fname = sys.argv[1]
if not path.isfile(fname):
    print('Error: file', fname, 'does not exist')
    sys.exit(0)
    
fp = open(fname, 'r')
lines = [line for line in fp]
fp.close()

program = [[0, 0, 0, 0] for i in range(1024)]
counter = 0
left_brackets = []
breaks = []
labels = {}
routines = []

def set23(arr, val):
    if val < 0:
        val += 65536
    arr[2] = val % 256
    arr[3] = (val // 256) % 256

def parseValue(val):
    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    if val in alphabet:
        return {'RegisterValue': alphabet.index(val) + 3, 'ImmediateValue': None, 'LabelValue': val}
    try:
        num = int(val)
        if num < 0:
            num += 65536
        out = {'RegisterValue': None, 'ImmediateValue': num, 'LabelValue': val}
        if num == 0:
            out['RegisterValue'] = 0
        elif num == 1:
            out['RegisterValue'] = 1
        elif num == 65535:
            out['RegisterValue'] = 2
        return out
    except ValueError:
        pass
    if val[0] == '@':
        try:
            num = int(val[1:])
            return {'RegisterValue': num, 'ImmediateValue': None, 'LabelValue': val}
        except ValueError:
            return {'RegisterValue': None, 'ImmediateValue': None, 'LabelValue': val}
    if val[0:2] == '0x' or val[0:2] == '0X':
        try:
            num = int(val, base=16)
            return {'RegisterValue': None, 'ImmediateValue': num, 'LabelValue': val}
        except ValueError:
            return {'RegisterValue': None, 'ImmediateValue': None, 'LabelValue': val}
    if val[0] == '(':
        try:
            hl = val[1:-1].split(',')
            num = None
            if len(hl) > 2:
                red = int(hl[0])
                green = int(hl[1])
                blue = int(hl[2])
                num = 2048*(red // 8) + 32*(green // 4) + (blue // 8)
            else:
                high = int(hl[0])
                low = int(hl[1])
                num = 256*high+low
            if num < 0:
                num += 65536
            return {'RegisterValue': None, 'ImmediateValue': num, 'LabelValue': val}
        except ValueError:
            return {'RegisterValue': None, 'ImmediateValue': None, 'LabelValue': val}
    return {'RegisterValue': None, 'ImmediateValue': None, 'LabelValue': val}

for line in lines:
    line = line.strip()
    if len(line) == 0:
        continue
    if line[0] == '#':
        continue
        
    if line[-1] == ':':
        labels[line[:-1]] = counter
        continue
    
    words = line.split(' ')
    # print(words)
    opcode = words[0]
    if len(words) > 1:
        val1 = parseValue(words[1])
    else:
        val1 = {'RegisterValue': None, 'ImmediateValue': None, 'LabelValue': None}
    if len(words) > 2:
        val2 = parseValue(words[2])
    else:
        val2 = {'RegisterValue': None, 'ImmediateValue': None, 'LabelValue': None}
    if len(words) > 3:
        val3 = parseValue(words[3])
    else:
        val3 = {'RegisterValue': None, 'ImmediateValue': None, 'LabelValue': None}
    
    instruction = [0, 0, 0, 0]
    if opcode == 'nop':
        pass # Nothing to do, as instruction is already 0 0 0 0
    elif opcode == 'end':
        instruction[0] = 0x01
        # Find the corresponding if/while/def and pop the bracket
        lb = left_brackets[-1]
        left_brackets = left_brackets[:-1]
        other_instruction = program[lb]
        set23(other_instruction, counter - lb)
        if other_instruction[0] == 0x03:
            set23(instruction, lb - counter - 1)
            breaklist = breaks[-1]
            breaks = breaks[:-1]
            for bk in breaklist:
                break_instruction = program[bk]
                set23(break_instruction, counter - bk)
    elif opcode == 'if':
        instruction[0] = 0x02
        instruction[1] = val1['RegisterValue']
        instruction[2] = None
        instruction[3] = None
        left_brackets += [counter]
    elif opcode == 'while':
        instruction[0] = 0x03
        instruction[1] = val1['RegisterValue']
        instruction[2] = None
        instruction[3] = None
        left_brackets += [counter]
        breaks += [[]]
    elif opcode == 'else':
        instruction[0] = 0x04
        instruction[2] = None
        instruction[3] = None
        lb = left_brackets[-1]
        left_brackets[-1] = counter
        other_instruction = program[lb]
        set23(other_instruction, counter - lb)
    elif opcode == 'switch':
        instruction[0] = 0x05
        instruction[1] = val1['RegisterValue']
    elif opcode == 'gz':
        instruction[0] = 0x06
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['LabelValue']
        instruction[3] = None
    elif opcode == 'gnz':
        instruction[0] = 0x07
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['LabelValue']
        instruction[3] = None
    elif opcode == 'def':
        instruction[0] = 0x08
        routines += [val1['LabelValue']]
        if len(routines) > 256:
            print('Error: more than 256 routines')
            sys.exit(0)
        instruction[1] = len(routines) - 1
        instruction[2] = None
        instruction[3] = None
        left_brackets += [counter]
    elif opcode == 'call':
        instruction[0] = 0x09
        instruction[1] = val1['LabelValue']
    elif opcode == 'goto':
        instruction[0] = 0x0a
        instruction[2] = val1['LabelValue']
        instruction[3] = None
    elif opcode == 'break':
        instruction[0] = 0x0b
        instruction[2] = None
        instruction[3] = None
        breaks[-1] += [counter]
    elif opcode == 'continue':
        instruction[0] = 0x0c
        i = -1
        while program[left_brackets[i]][0] != 0x03:
            i -= 1
        set23(instruction, left_brackets[i] - counter - 1)
    elif opcode == 'return':
        instruction[0] = 0x0d
    elif opcode == 'reset':
        instruction[0] = 0x0e
    elif opcode == 'print':
        instruction[0] = 0x0f
        instruction[1] = val1['RegisterValue']
    elif opcode == '+':
        instruction[0] = 0x10
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '-':
        instruction[0] = 0x11
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '*':
        instruction[0] = 0x12
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '/':
        instruction[0] = 0x13
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 's/':
        instruction[0] = 0x14
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '%':
        instruction[0] = 0x15
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 's%':
        instruction[0] = 0x16
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 'frac':
        instruction[0] = 0x17
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 'sfrac':
        instruction[0] = 0x18
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '==':
        instruction[0] = 0x19
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '!=':
        instruction[0] = 0x1a
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '<':
        instruction[0] = 0x1b
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 's<':
        instruction[0] = 0x1c
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '<=':
        instruction[0] = 0x1d
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 's<=':
        instruction[0] = 0x1e
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '&':
        instruction[0] = 0x1f
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '&&':
        instruction[0] = 0x20
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '|':
        instruction[0] = 0x21
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '^':
        instruction[0] = 0x22
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '<<':
        instruction[0] = 0x23
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '>>':
        instruction[0] = 0x24
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '?':
        instruction[0] = 0x25
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 'absgn':
        instruction[0] = 0x26
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 'sqrt':
        instruction[0] = 0x27
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 'red':
        instruction[0] = 0x28
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 'green':
        instruction[0] = 0x29
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 'blue':
        instruction[0] = 0x2a
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '+c':
        instruction[0] = 0x2b
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '-c':
        instruction[0] = 0x2c
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == '*c':
        instruction[0] = 0x2d
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 'conc':
        instruction[0] = 0x2e
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 'high':
        instruction[0] = 0x2f
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == '=':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0x30
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
        else:
            instruction[0] = 0x31
            instruction[1] = val1['RegisterValue']
            set23(instruction, val2['ImmediateValue'])
    elif opcode == 'load':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0x32
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
        else:
            instruction[0] = 0x33
            instruction[1] = val1['RegisterValue']
            set23(instruction, val2['ImmediateValue'])
    elif opcode == 'store':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0x34
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
        else:
            instruction[0] = 0x35
            instruction[1] = val1['RegisterValue']
            set23(instruction, val2['ImmediateValue'])
    elif opcode == 'window':
        if val1['RegisterValue'] is not None:
            instruction[0] = 0x36
            instruction[2] = val1['RegisterValue']
        else:
            instruction[0] = 0x37
            set23(instruction, val1['ImmediateValue'])
    elif opcode == 'skip':
        if val1['RegisterValue'] is not None:
            instruction[0] = 0x38
            instruction[2] = val1['RegisterValue']
        else:
            instruction[0] = 0x39
            set23(instruction, val1['ImmediateValue'])
    elif opcode == 'skim':
        if val1['RegisterValue'] is not None:
            instruction[0] = 0x3a
            instruction[2] = val1['RegisterValue']
        else:
            instruction[0] = 0x3b
            set23(instruction, val1['ImmediateValue'])
    elif opcode == 'read':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0x40
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
        else:
            instruction[0] = 0x41
            instruction[1] = val1['RegisterValue']
            set23(instruction, val2['ImmediateValue'])
    elif opcode == 'write':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0x42
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
        else:
            instruction[0] = 0x43
            instruction[1] = val1['RegisterValue']
            set23(instruction, val2['ImmediateValue'])
    elif opcode == 'readb':
        instruction[0] = 0x44
        instruction[1] = val1['RegisterValue']
    elif opcode == 'reads':
        instruction[0] = 0x45
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == 'readp':
        instruction[0] = 0x46
        instruction[1] = val1['RegisterValue']
    elif opcode == 'rex':
        instruction[0] = 0x47
        instruction[1] = val1['RegisterValue']
    elif opcode == 'refresh':
        instruction[0] = 0x50
    elif opcode == 'clear':
        instruction[0] = 0x51
        instruction[1] = val1['RegisterValue']
    elif opcode == 'dbg':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0x56
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
            instruction[3] = val3['RegisterValue']
        else:
            instruction[0] = 0x52
            if val1['RegisterValue'] is not None:
                instruction[1] = val1['RegisterValue']
    elif opcode == 'dbg16':
        instruction[0] = 0x53
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == 'dbg8':
        instruction[0] = 0x54
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == 'dbg4':
        instruction[0] = 0x55
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == 'dss':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0x5b
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
            instruction[3] = val3['RegisterValue']
        else:
            instruction[0] = 0x57
            instruction[1] = val1['RegisterValue']
    elif opcode == 'dss16':
        instruction[0] = 0x58
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == 'dss8':
        instruction[0] = 0x59
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == 'dss4':
        instruction[0] = 0x5a
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == 'dpx':
        instruction[0] = 0x5c
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == 'dchar':
        instruction[0] = 0x5d
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 'dstr':
        instruction[0] = 0x5e
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 'clearp':
        instruction[0] = 0x60
        instruction[2] = val1['RegisterValue']
        instruction[3] = val2['RegisterValue']
    elif opcode == 'setp':
        instruction[0] = 0x61
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 'getp':
        instruction[0] = 0x62
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
        instruction[3] = val3['RegisterValue']
    elif opcode == 'setpoffs':
        if val1['RegisterValue'] is not None:
            instruction[0] = 0x63
            instruction[2] = val1['RegisterValue']
        else:
            instruction[0] = 0x64
            set23(instruction, val1['ImmediateValue'])
    elif opcode == 'frame':
        instruction[0] = 0x70
        if val1['RegisterValue'] is not None:
            instruction[1] = val1['RegisterValue']
    elif opcode == 'delay':
        if val1['RegisterValue'] is not None:
            instruction[0] = 0x71
            instruction[2] = val1['RegisterValue']
        else:
            instruction[0] = 0x72
            set23(instruction, val1['ImmediateValue'])
    elif opcode == 'button':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0x80
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
        else:
            instruction[0] = 0x81
            instruction[1] = val1['RegisterValue']
            set23(instruction, val2['ImmediateValue'])
    elif opcode == 'buttonp':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0x82
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
        else:
            instruction[0] = 0x83
            instruction[1] = val1['RegisterValue']
            set23(instruction, val2['ImmediateValue'])
    elif opcode == 'buttonr':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0x84
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
        else:
            instruction[0] = 0x85
            instruction[1] = val1['RegisterValue']
            set23(instruction, val2['ImmediateValue'])
    elif opcode == 'colflags':
        if val1['RegisterValue'] is not None:
            instruction[0] = 0x90
            instruction[2] = val1['RegisterValue']
        else:
            instruction[0] = 0x91
            set23(instruction, val1['ImmediateValue'])
    elif opcode == 'col':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0x96
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
            instruction[3] = val3['RegisterValue']
        else:
            instruction[0] = 0x92
            instruction[1] = val1['RegisterValue']
    elif opcode == 'col16':
        instruction[0] = 0x93
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == 'col8':
        instruction[0] = 0x94
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == 'col4':
        instruction[0] = 0x95
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == 'itoa':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0xa0
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
        else:
            instruction[0] = 0xa1
            instruction[1] = val1['RegisterValue']
            set23(instruction, val2['ImmediateValue'])
    elif opcode == 'sitoa':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0xa2
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
        else:
            instruction[0] = 0xa3
            instruction[1] = val1['RegisterValue']
            set23(instruction, val2['ImmediateValue'])
    elif opcode == 'strw':
        instruction[0] = 0xa4
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == 'strh':
        instruction[0] = 0xa5
        instruction[1] = val1['RegisterValue']
        instruction[2] = val2['RegisterValue']
    elif opcode == 'loadsnd':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0xb0
            instruction[2] = val1['RegisterValue']
        else:
            instruction[0] = 0xb1
            set23(instruction, val1['ImmediateValue'])
    elif opcode == 'playsnd':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0xb2
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
        else:
            instruction[0] = 0xb3
            instruction[1] = val1['RegisterValue']
            set23(instruction, val2['ImmediateValue'])
    elif opcode == 'stopsnd':
        instruction[0] = 0xb4
        instruction[1] = val1['RegisterValue']
    elif opcode == 'random':
        if val2['RegisterValue'] is not None:
            instruction[0] = 0xf0
            instruction[1] = val1['RegisterValue']
            instruction[2] = val2['RegisterValue']
        else:
            instruction[0] = 0xf1
            instruction[1] = val1['RegisterValue']
            set23(instruction, val2['ImmediateValue'])
    else:
        print('Error: unknown instruction', opcode)
        sys.exit(0)
    
    program[counter] = instruction
    counter += 1
    
for counter2 in range(counter):
    if program[counter2][0] in [0x06, 0x07, 0x0a]:
        label = program[counter2][2]
        if label not in labels:
            print('Error: unknown label', label)
            sys.exit(0)
        set23(program[counter2], labels[label] - counter2)
    elif program[counter2][0] == 0x09:
        routine = program[counter2][1]
        if routine not in routines:
            print('Error: unknown routine', routine)
            sys.exit(0)
        program[counter2][1] = routines.index(routine)
    
programb = [b for inst in program for b in inst]

fname2 = fname[:-3] + 'bin'
fp = open(fname2, 'wb+')
fp.write(bytes(programb))
fp.close()