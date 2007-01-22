#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# mutable_iterators_test.py: test the easystates StateMachine

import sys, itertools
import iterqueue
from iterqueue import *

wrappers = [obj for obj in iterqueue.__dict__.values() 
            if is_iterator_wrapper(obj)]
print "\n".join(repr(wrapper) for wrapper in wrappers)

print "Peekables"
peekables = [obj for obj in wrappers if is_peekable(obj)]
print "\n".join(repr(peekable) for peekable in peekables)

print "Pushables"
pushables = [obj for obj in wrappers if is_pushable(obj)]
print "\n".join(repr(pushable) for pushable in pushables)

print "State Reporters"
state_reporters = [obj for obj in wrappers if is_state_reporting(obj)]
print "\n".join(repr(state_reporter) for state_reporter in state_reporters)

print "Iterator Queues"
iqueues = [obj for obj in wrappers if is_iterator_queue(obj)]
print "\n".join(repr(iqueue) for iqueue in iqueues)


# XLIter Tests
# ------------

class IQtests:
    """Base class for tests of Iteratorqueues"""
    def setUp(self):
        self.it = self.IterClass(range(3))
        
    def test__init__(self):
        """initialization returns an iterator object"""
        assert is_iterator(self.it)
    
    def test_extend(self):
        """extend(iterable) shall append `iterable` to iterator"""
        self.it.extend([9])
        assert list(self.it) == range(3) + [9]
    
    def test_extendleft(self):
        """extendleft(iterable) shall prepend `iterable` to iterator"""
        self.it.extendleft([9])
        assert [i for i in self.it] == [9] + range(3)
        
    def test_append(self):
        """append(value) shall append `value` to iterator"""
        self.it.append(9)
        # print self.it
        assert [i for i in self.it] == range(3) + [9]
    
    def test_appendleft(self):
        """appendleft(value) shall prepend `value` to iterator"""
        self.it.appendleft(9)
        assert [i for i in self.it] == [9] + range(3)
        
    def test_appendleft_while_iterating(self):
        """appendleft shall work even in an iteration loop"""
        result = []
        for i in self.it:
            if i == 1:
                self.it.appendleft("xx")
            result.append(i)
        assert result == [0, 1, 'xx', 2]  
    
    def test_peek(self):
        """peek() should return next value but not advance the iterator"""
        print self.it.peek()
        print self.it.peek()
        assert self.it.peek() == 0
        # peek() doesnot "use up" values
        assert list(self.it) == range(3)
    
    def test_bool(self):
        "Empty iterator should evaluate to False"
        assert bool(self.IterClass([])) == False
        assert bool(self.IterClass([1])) == True
        # assert bool(self.IterClass([], [])) == False
        assert bool(self.IterClass(iter([]))) == False
        assert bool(self.IterClass(iter([1]))) == True


class TestIterQueue(IQtests):
    """Test the deque with iterator add-ons"""
    IterClass = IterQueue
    #
    
class TestIQueue(IQtests):
    """Test the IQueue mutable iterator queue
    """
    IterClass = IQueue
    #
    def test__init__chain(self):
        """initialzation shall put the arguments in the chain"""
        it = self.IterClass(range(3), [], xrange(2))
        assert list(it) == range(3) + range(2)
    
class TestIQueue2(IQtests):
    """Test the optimized iterator queue"""
    IterClass = XIter

if __name__ == "__main__":  
    import nose
    nose.configure(["test.py", "--detailed-errors"])
    nose.runmodule() # requires nose 0.9.1
