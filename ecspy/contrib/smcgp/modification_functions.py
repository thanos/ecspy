'''
Created on Dec 11, 2010
@author: Henrik Rudstrom

example self modification function set as defined in
Table 1 of "Developments in Cartesian Genetic Programming: self-modifying CGP"


'''
import copy


def self_modification(name=None):
    '''decorator for self modification functions'''
    
    def mod(func):
        if name != None:
            func.__name__ = name 
        func.mod = True
        return func
    return mod

def val_to_index(cand, val, end=False):
    return max(0,min(len(cand)-int(not end), int(val)))

def decode_relative_range(gene, cand, x):
    '''decodes gene as range (P0 + x) and (P0 + x + P1)'''
    #gene = cand[index]
    start = val_to_index(cand,int(gene.vars[0]) + x)
    end = val_to_index(cand,start + int(gene.vars[1]), True)
    return (min(start, end), max(start, end)) 

def decode_relative_index(gene, cand, x, input_index):
    #gene = cand[index]
    return val_to_index(cand,int(gene.vars[input_index]) + x) 



def insert_range(cand, new, i):
    return cand[:i]+new+cand[i:]

# Self modification functions. 
# see 
@self_modification('ADD')
def add(encoding, gene, cand, index):
    s,e = decode_relative_range(gene,cand,index)
    new = [encoding.random_gene(col) for col in xrange(int(gene.vars[1]))]
    #print "new",len(new)
    return insert_range(cand, new, s)

@self_modification('MOV')
def move(encoding, gene, cand, index):
    s,e = decode_relative_range(gene,cand,index)
    ins = decode_relative_index(gene,cand,index,2)
    if ins >= s:
        cand = cand[:s]+cand[e:ins]+cand[s:e]+cand[ins:]
    else:
        cand = cand[:ins]+cand[s:e]+cand[ins:s]+cand[e:]
    return cand

@self_modification('DEL')
def delete(encoding, gene, cand, index):
    s,e = decode_relative_range(gene,cand,index)
    return cand[:s]+cand[e:]

@self_modification('DUP')
def duplicate(encoding, gene, cand, index):
    s,e = decode_relative_range(gene,cand,index)
    ins = decode_relative_index(gene,cand,index,2)
    return cand[:ins]+cand[s:e]+cand[ins:]

@self_modification('OVR')
def overwrite(encoding, gene, cand, index):
    s,e = decode_relative_range(gene,cand,index)
    for i in xrange(s, e):
        ofsi = decode_relative_index(gene,cand,0,2)
        cand[ofsi] = cand[i]
    return cand

@self_modification('DU3')
def duplicate_and_shift(encoding, gene, cand, index):
    s,e = decode_relative_range(gene,cand,index)
    ins = decode_relative_index(gene,cand,index,2)
    connection_offset = -(s - ins)
    #print "OFS", connection_offset
    duped = [copy.deepcopy(c) for c in cand[s:e]]
    for d in duped:
        for i in xrange(len(d.inputs)):
            d.inputs[i] += connection_offset
    return cand[:ins]+duped+cand[ins:]
    
@self_modification('DU4')
def duplicate_and_scale(encoding, gene, cand, index):
    s,e = decode_relative_range(gene,cand,index)
    ins = e#decode_relative_index(gene,cand,index,2)
    duped = [copy.deepcopy(c) for c in cand[s:e]]
    for d in duped:
        for i in xrange(len(d.inputs)):
            d.inputs[i] = int(d.inputs[i] * gene.vars[2])
    return cand[:ins]+duped+cand[ins:]

@self_modification('SHIFTCONNECTION')
def shift_connections(encoding, gene, cand, x):
    '''Starting at node index (P0 + x), add P2 to the values of the cij of next P1 nodes'''
    s, e = decode_relative_range(gene,cand,x)
    for i in xrange(s,e):
        for j in xrange(len(cand[i].inputs)):
            cand[i].inputs[j] += int(gene.vars[2])
    return cand

@self_modification('MULTCONNECTION')
def scale_connections(encoding, gene, cand, x):
    '''Starting at node index (P0 + x), multiply the cij of the next P1 nodes by P2'''
    s, e = decode_relative_range(gene,cand,x)
    for i in xrange(s,e):
        for j in xrange(len(cand[i].inputs)):
            cand[i].inputs[j] = int(cand[i].inputs[j] * gene.vars[2])
    return cand

@self_modification('CHC')      
def change_connection(encoding, gene, cand, x):
    '''Change the (P1 mod 3)th connection of node P0 to P2'''
    inp = int(gene.vars[1]) % len(gene.inputs)
    i = val_to_index(cand, gene.vars[0])
    cand[i].inputs[inp] = 1+abs(int(gene.vars[2]) % (i+1))
    return cand

@self_modification('CHF')
def change_function(encoding, gene, cand, x):
    '''Change the function of node P0 to the function associated with P1'''
    i1 = val_to_index(cand, gene.vars[0])
    i2 = val_to_index(cand, gene.vars[1])
    cand[i1].function = cand[i2].function
    return cand

@self_modification('CHP')
def change_parameter(encoding, gene, cand, x):
    '''Change the (P1 mod 3)th parameter of node P0 to P2'''
    
    var = int(gene.vars[1]) % len(gene.vars)
    i = val_to_index(cand, gene.vars[0])
    #print i, var, len(gene.vars), len(cand) 
    cand[i].vars[var] = int(gene.vars[2])
    return cand


all_functions = [add, move, delete, duplicate, overwrite, 
                 duplicate_and_shift, duplicate_and_scale, 
                 shift_connections, scale_connections, 
                 change_connection, change_function, change_parameter]