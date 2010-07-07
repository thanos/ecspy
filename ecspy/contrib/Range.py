'''

Suggested class for arithmic where bounding values are automagically
kept within constraints

Hi Aaron, a quick design for the discussion earlier today.
Surely you'll out do me, but hey, we need something to discuss ;)

-jelle

'''

import random


#===============================================================================
# OLD AND RUSTY
#===============================================================================

## decorator that deals with the bounding values of the instance 
#def check_range(_operator):
#    def decorator1(instance,_val):
#        value =  _operator(instance,_val)
#        if value > instance._upperbound:
#            value = instance._upperbound
#        if value < instance._lowerbound:
#            value = instance._lowerbound
#        instance.value = value
#        return Range(value, instance._lowerbound, instance._upperbound)
#    return decorator1
#
#class Range(object):
#    '''
#    however you add, multiply or divide, it will always stay within boundaries
#    '''
#    def __init__(self, value, lowerbound, upperbound):
#        '''
#        
#        @param lowerbound:
#        @param upperbound:
#        '''
#        self._lowerbound = lowerbound
#        self._upperbound = upperbound
#        self.value = value
#        
#    def init(self):
#        '''
#        set a random value within bounds
#        '''
#        self.value = random.uniform(self._lowerbound, self._upperbound)
#        
#    def __str__(self):
#        return self.__repr__()
#    
#    def __repr__(self):
#        return "<Range: %s>" % (self.value)
#    
#    @check_range
#    def __mul__(self, other):
#        return self.value * other
#         
#    @check_range
#    def __div__(self, other):
#        return self.value / float(other)
#    
#    def __truediv__(self, other):
#        return self.div(other)     
#    
#    @check_range
#    def __add__(self, other):
#        return self.value + other
#         
#    @check_range
#    def __sub__(self, other):
#        return self.value - other
    


#===============================================================================
# See: http://stackoverflow.com/questions/3191125/decorating-arithmetic-operators-should-i-be-using-a-metaclass
#===============================================================================
import operator

class Range(object):

    def __init__(self, value, lowerbound, upperbound):
        self._lowerbound = lowerbound
        self._upperbound = upperbound
        if value < self._lowerbound:
            self.value = self._lowerbound
        elif value > self._upperbound:
            self.value = self._upperbound
        else:
            self.value = value
        

    def __repr__(self):
        return "<Range: %s>" % (self.value)

    def _from_value(self, val):
        val = max(min(val, self._upperbound), self._lowerbound)
        # NOTE: it's nice to use type(self) instead of writing the class
        # name explicitly; it then continues to work if you change the
        # class name, or use a subclass
        return type(self)(val, rng._lowerbound, rng._upperbound)

    def _make_binary_method(fn):
        # this is NOT a method, just a helper function that is used
        # while the class body is being evaluated
        def bin_op(self, other):
            return self._from_value(fn(self.value, other))
        return bin_op

    __mul__ = _make_binary_method(operator.mul)
    __div__ = _make_binary_method(operator.truediv)
    __truediv__ = __div__
    __add__ = _make_binary_method(operator.add)
    __sub__ = _make_binary_method(operator.sub)

class RRRange(Range):
    def __init__(self, *args):
        Range.__init__(self, *args)
    
    def whatsmytype(self):
        return type( self )
    

rng = Range(7, 0, 10)
print rng + 5
print rng * 50
print rng - 10
print rng / 100

rng = RRRange(7, 0, 10)
print rng + 5
print rng * 50
print rng - 10
print rng / 100
print rng.whatsmytype()

class Better(object):
    def __irshift__(self, other):
        print 'BETTER!'

b = Better()
b >>= 12

#    
#         
#r = Range(11, -90.,90.)
#print r * 3.
#assert r.value == 33
#print r * 12 # should be 90
#print r + 100 # 90
#print r - 1100 # 90
#print r / 0.0001 # -90
