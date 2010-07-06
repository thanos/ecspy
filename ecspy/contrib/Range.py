'''

Suggested class for arithmic where bounding values are automagically
kept within constraints

Hi Aaron, a quick design for the discussion earlier today.
Surely you'll out do me, but hey, we need something to discuss ;)

-jelle

'''

import random

# decorator that deals with the bounding values of the instance 
def check_range(_operator):
    def decorator1(instance,_val):
        value =  _operator(instance,_val)
        if value > instance._upperbound:
            value = instance._upperbound
        if value < instance._lowerbound:
            value = instance._lowerbound
        instance.value = value
        return value
    return decorator1

class Range(object):
    '''
    however you add, multiply or divide, it will always stay within boundaries
    '''
    def __init__(self, value, lowerbound, upperbound):
        '''
        
        @param lowerbound:
        @param upperbound:
        '''
        self._lowerbound = lowerbound
        self._upperbound = upperbound
        self.value = value
        
    def init(self):
        '''
        set a random value within bounds
        '''
        self.value = random.uniform(self._lowerbound, self._upperbound)
    
    @check_range
    def __mul__(self, other):
        return self.value * other
         
    @check_range
    def __div__(self, other):
        return self.value / float(other)
    
    def __truediv__(self, other):
        return self.div(other)     
    
    @check_range
    def __add__(self, other):
        return self.value + other
         
    @check_range
    def __sub__(self, other):
        return self.value - other
    
         
r = Range(11, -90.,90.)
print r * 3
assert r.value == 33
print r * 12 # should be 90
print r + 100 # 90
print r - 1100 # 90
print r / 0.0001 # -90

