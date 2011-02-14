'''
Created on Dec 12, 2010

@author: Henrik Rudstrom
'''
import ecspy.contrib.smcgp.modification_functions as mod
from ecspy.contrib.smcgp.encoding import SMCGPGene, SMCGPEncoding, call_mod
import unittest
from ecspy.contrib.smcgp.phenotype import io_functions, SMCGPPhenotype

class SMCGPDummyEncoding(SMCGPEncoding):
    def random_gene(self, col):
        return SMCGPGene(3,[1,1],[0,0,0])

def input_gene():
    return SMCGPGene(0,[0,0], [0,0,0])    
def output_gene(inp):
    return SMCGPGene(2,[inp,inp],[0,0,0])
def func_gene(f, a):
    return SMCGPGene(f, a,[0,0,0])

def mod_gene(f, inp, vars):
    f = mod.all_functions.index(f)+5
    return SMCGPGene(f, inp, vars)


class ModTest(unittest.TestCase):
    def setUp(self):
        def add(gene, a, b):
            return a + b
        def sub(gene, a, b):
            return a - b
        
        self.enc = SMCGPDummyEncoding(2, 2, 1, 1)
        
        self.user = [add, sub]
        self.enc.set_functions(io_functions+self.user+mod.all_functions)
    
    def test_add(self):
        gen1 = [input_gene(), input_gene(), mod_gene(mod.add,[2,1],[1,2,0]), func_gene(3,[1,1]), func_gene(4,[2,1]), output_gene(1)]
        func = SMCGPPhenotype(self.enc, list(gen1))
        modified = func.get_modified()
        assert len(func.candidate) == 6
        assert len(modified.candidate) == 8
        assert func.candidate[:3] == modified.candidate[:3]
        assert func.candidate[3:] == modified.candidate[5:]
        #print "mod", modified.candidate
        
        mod2 = modified.get_modified()
        #print "mod2", mod2.candidate
        #print "mod2",len(mod2.candidate)
        assert len(mod2.candidate) == 10
        assert modified.candidate[:3] == mod2.candidate[:3]
        assert modified.candidate[3:] == mod2.candidate[5:]
        
    def test_del(self):
        gen1 = [input_gene(), input_gene(), mod_gene(mod.delete,[2,1],[1,2,0]), func_gene(3,[1,1]), func_gene(4,[2,1]),func_gene(4,[2,1]), output_gene(1)]
        func = SMCGPPhenotype(self.enc, list(gen1))
        modified = func.get_modified()
        assert len(func.candidate) == 7
        assert len(modified.candidate) == 5
        assert func.candidate[:3] == modified.candidate[:3]
        assert func.candidate[5:] == modified.candidate[3:] 
        mod2 = modified.get_modified()  
        print func.candidate
        print modified.candidate
        print mod2.candidate
        assert len(mod2.candidate) == 3; #no more to delete
        assert modified.candidate[:3] == mod2.candidate[:3]
        #assert modified.candidate[5:] == mod2.candidate[3:]
    def test_del_add(self):
        gen1 = [input_gene(), input_gene(), mod_gene(mod.add,[2,1],[3,3,0]), mod_gene(mod.delete,[2,1],[1,1,0]), func_gene(3,[1,2]), func_gene(4,[2,1]), output_gene(1)]
        func = SMCGPPhenotype(self.enc, list(gen1))
        modified = func.get_modified()
        assert len(func.candidate) == 7
        #print len(modified.candidate)
        assert len(modified.candidate) == 9
        deleted = gen1[4]
        #print deleted
        #print modified.candidate
        assert deleted not in modified.candidate
        assert func.candidate[:3] == modified.candidate[:3]
        assert func.candidate[5:] == modified.candidate[7:]
        
    def test_dup(self):
        gen1 = [input_gene(), input_gene(), mod_gene(mod.duplicate,[2,1],[1,2,1]), func_gene(3,[1,1]), func_gene(4,[2,1]), output_gene(1)]
        func = SMCGPPhenotype(self.enc, list(gen1))   
        modified = func.get_modified()
        assert len(modified.candidate) == len(func.candidate) + 2
        assert func.candidate[3:4] == modified.candidate[3:4]
        assert func.candidate[3:4] == modified.candidate[5:6]
        
    def test_overwrite(self):
        gen1 = [input_gene(), input_gene(), mod_gene(mod.overwrite,[2,1],[1,1,2]), func_gene(3,[1,1]), func_gene(4,[2,1]), output_gene(1)]
        func = SMCGPPhenotype(self.enc, list(gen1))   
        modified = func.get_modified()
        assert len(modified.candidate) == len(func.candidate)
        assert func.candidate[3] == modified.candidate[3]
        assert func.candidate[4] == modified.candidate[4]
        
    def test_dup_preserve(self):
        gen1 = [input_gene(), input_gene(), mod_gene(mod.duplicate_and_shift,[2,1],[1,2,3]), func_gene(3,[1,1]), func_gene(4,[2,1]), output_gene(1)]
        func = SMCGPPhenotype(self.enc, list(gen1))   
        modified = func.get_modified()
        assert len(modified.candidate) == len(func.candidate) + 2
        assert func.candidate[3:4] == modified.candidate[3:4]
        assert func.candidate[3].function == modified.candidate[5].function
        assert func.candidate[3].vars[0] == modified.candidate[5].vars[0]
        assert func.candidate[3].vars[1] == modified.candidate[5].vars[1]
        assert func.candidate[3].inputs[0] + 2 == modified.candidate[5].inputs[0]
        assert func.candidate[3].inputs[1] + 2 == modified.candidate[5].inputs[1]
        assert func.candidate[4].function == modified.candidate[6].function
        assert func.candidate[4].vars[0] == modified.candidate[6].vars[0]
        assert func.candidate[4].vars[1] == modified.candidate[6].vars[1]
        assert func.candidate[4].inputs[0] + 2 == modified.candidate[6].inputs[0]
        assert func.candidate[4].inputs[1] + 2 == modified.candidate[6].inputs[1]
        
    def test_dup_scale(self):
        gen1 = [input_gene(), input_gene(), mod_gene(mod.duplicate_and_scale,[2,1],[1,2,3]), func_gene(3,[1,1]), func_gene(4,[2,1]), output_gene(1)]
        func = SMCGPPhenotype(self.enc, list(gen1))   
        modified = func.get_modified()
        assert len(modified.candidate) == len(func.candidate) + 2
        assert func.candidate[3:4] == modified.candidate[3:4]
        assert func.candidate[3].function == modified.candidate[5].function
        assert func.candidate[3].vars[0] == modified.candidate[5].vars[0]
        assert func.candidate[3].vars[1] == modified.candidate[5].vars[1]
        assert func.candidate[3].inputs[0] * 3 == modified.candidate[5].inputs[0]
        assert func.candidate[3].inputs[1] * 3 == modified.candidate[5].inputs[1]
        assert func.candidate[4].function == modified.candidate[6].function
        assert func.candidate[4].vars[0] == modified.candidate[6].vars[0]
        assert func.candidate[4].vars[1] == modified.candidate[6].vars[1]
        assert func.candidate[4].inputs[0] * 3 == modified.candidate[6].inputs[0]
        assert func.candidate[4].inputs[1] * 3 == modified.candidate[6].inputs[1]
     
    
    def test_shift_connections(self):
        gen1 = [input_gene(), input_gene(), mod_gene(mod.shift_connections,[2,1],[1,2,3]), func_gene(3,[1,1]), func_gene(4,[2,1]), output_gene(1)]
        func = SMCGPPhenotype(self.enc, list(gen1))   
        modified = func.get_modified()
        
        assert len(modified.candidate) == len(func.candidate)
        assert func.candidate[3].inputs[0] + 3 == modified.candidate[3].inputs[0]
        assert func.candidate[3].inputs[1] + 3 == modified.candidate[3].inputs[1]
    
    def test_scale_connections(self):
        gen1 = [input_gene(), input_gene(), mod_gene(mod.scale_connections,[2,1],[1,2,3]), func_gene(3,[1,1]), func_gene(4,[2,1]), output_gene(1)]
        func = SMCGPPhenotype(self.enc, list(gen1))   
        modified = func.get_modified()
        
        assert len(modified.candidate) == len(func.candidate)
        assert func.candidate[3].inputs[0] * 3 == modified.candidate[3].inputs[0]
        assert func.candidate[3].inputs[1] * 3 == modified.candidate[3].inputs[1] 
        
    def test_change_functions(self):
        gen1 = [input_gene(), input_gene(),func_gene(3,[1,1]),func_gene(4,[1,1]),
                mod_gene(mod.change_connection,[2,1],[2,0,2]),
                mod_gene(mod.change_function,[2,1],[2,3,0]),
                mod_gene(mod.change_parameter,[2,1],[2,0,3]),  output_gene(1)]
        func = SMCGPPhenotype(self.enc, list(gen1))   
        modified = func.get_modified()
        assert modified.candidate[2].function == modified.candidate[3].function
        
        assert modified.candidate[2].inputs[0] == 3
        assert modified.candidate[2].vars[0] == 3
        assert len(modified.candidate) == len(func.candidate)
        
    def test_input_output(self):
        enc = SMCGPEncoding(2, 1, 1, 2)
        enc.set_functions(io_functions)
        gen = [input_gene(), input_gene(), output_gene(2), output_gene(2), output_gene(3)]
        
        #gen = list_to_genes([[0,0],[0,0], [2, 2], [2,2], [2,3]])
        input = [5,2]
        func = SMCGPPhenotype(enc, gen)
        #print "funcs", func.functions
        res = func(input)
        assert res[0] == input[0]
        assert res[1] == input[1]
        assert res[2] == input[1]
        
    def test_no_outputs(self):
        enc = SMCGPEncoding(2, 1, 1, 2)
        enc.set_functions(io_functions)
        gen = [input_gene(), input_gene()]
        input = [5,2]
        func = SMCGPPhenotype(enc, gen)  

        res = func(input)
        
        assert res[0] == input[0], "res"+res[0]
        assert res[1] == input[1], "res"+res[1]

    def test_too_few_outputs(self):
        enc = SMCGPEncoding(2, 1, 1, 2)
        enc.set_functions(io_functions)
        gen = [input_gene(), input_gene(), output_gene(2)]
        input = [5,2]
        func = SMCGPPhenotype(enc, gen)    
        res = func(input)
        
        assert res[0] == input[0]
        assert res[1] == input[1]  
        
    def test_no_inputs(self):
        enc = SMCGPEncoding(2, 1, 1, 2)
        enc.set_functions(io_functions)
        gen = [output_gene(2), output_gene(2)]
        func = SMCGPPhenotype(enc, gen)
        assert func([1,2]) == [1,1] #first node becomes input
        
        
    def test_arithmetics(self):
        def add(gene, a, b):
            
            return a + b
        def sub(gene, a, b):
            return a - b
        enc = SMCGPEncoding(2, 2, 1, 1)
        
        enc.set_functions(io_functions+[add, sub])
        gen1 = [input_gene(),input_gene(), func_gene(3,[2,1]), func_gene(4,[2,1]), output_gene(1)]
        
        #gen1 = list_to_genes([[0,0,0],[0,0,0], [3,2,1], [3,2,2], [4, 2, 1], [2,1,0]])
        func = SMCGPPhenotype(enc, gen1) 
        input = [1,10]
        #(1 + 10) - (10 + 10) 
        res = func(input)
        #print "RES", res
        assert res[0] == -1
        
        
    def test_bias(self):
        
        count = [0,0,0]
        ranges = [self.enc.io_func_range, self.enc.user_func_range, self.enc.mod_func_range]
        
        for _ in xrange(1000):
            f = self.enc.random_func(0)
            for i,(s,e) in enumerate(ranges):
                if f >= s and f < e:
                    count[i] += 1
                    break

        def almost_equal(c1, c2):
            print c1, c2
            return abs(c1-c2) < 50
        for a in count:
            for b in count:
                assert almost_equal(a,b)
            
            

if __name__ == '__main__':
    unittest.main()