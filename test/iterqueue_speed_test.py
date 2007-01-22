import os, itertools, profile
import hotshot, hotshot.stats
from iterqueue import XIter, IQueue, PushIterator

# Set up profiler
logfile = "/tmp/iterqueue.profile"

# Speed comparisions (benchmarks)
# ------------------

def loop(iterator):
    """empty `for` loop over the iterator"""
    for _ in iterator:
        pass

def peek_and_loop(iterator):
    """loop over iterator, peek in the loop"""
    for _ in iterator:
        try:
            iterator.peek()
        except StopIteration:
            pass
    
def peek_once_and_loop(iterator):
    """peek at first value once, then loop"""
    try:
        iterator.peek()
    except StopIteration:
        pass
    for _ in iterator:
        pass
    
def bool_and_loop(iterator):
    """loop over iterator, test for values in the loop"""
    for _ in iterator:
        bool(iterator)
        
def bool_once_and_loop(iterator):
    """test for values once, then loop"""
    bool(iterator)
    for _ in iterator:
        pass

def run_benchmarks(iter_wrapper, iterator):
    """run the iterator benchmarks on the given iterators"""
    
    print str(iter_wrapper), str(iterator)

    prof = hotshot.Profile(logfile)
    
    prof.runcall(loop, iter_wrapper(iterator))
    prof.runcall(peek_and_loop, iter_wrapper(iterator))
    prof.runcall(peek_once_and_loop, iter_wrapper(iterator))
    prof.runcall(bool_and_loop, iter_wrapper(iterator))
    prof.runcall(bool_once_and_loop, iter_wrapper(iterator))
    
    prof.close
    
    stats = hotshot.stats.load(logfile)
    stats.strip_dirs()
    stats.sort_stats('file', 'time', 'calls')
    # stats.sort_stats('nfl')  # 'name, file, line'
    stats.print_stats(20)
    
    os.remove(logfile)


        
run_benchmarks(XIter, xrange(1000))
run_benchmarks(PushIterator, xrange(1000))
        
# mutable_iterators_speed_test.py:19 test_chain_peek[0] ok (0.00)
# mutable_iterators_speed_test.py:19 test_chain_peek[1] ok (0.03)
# mutable_iterators_speed_test.py:19 test_chain_peek[2] ok (0.39)


def test_chain_get(peeks_nr, get_nr):
    it = chain_peek(itertools.count(), peeks_nr)
    chain_get(it, get_nr)
    
# prof.runcall(test_chain_get, 1000, 1000)
# prof.close()

   
# itertools_chain nesting
#     10 iterations: 0.00202894210815
#    100 iterations: 0.0580220222473
#   1000 iterations: 8.09108090401
# itertools_chain repetitive
#     10       runs: 0.00154113769531
#    100       runs: 0.0154590606689
#   1000       runs: 0.157324075699
# XIter nesting
#     10 iterations: 0.00176215171814
#    100 iterations: 0.0178871154785
#   1000 iterations: 0.179019927979
# XIter repetitive
#     10       runs: 0.00194001197815
#    100       runs: 0.0194261074066
#   1000       runs: 0.187463998795


# An peekable iterator with itertools.chain

def peek_with_chain(iterator):
    """peek at first value in iterator and push it back with chain
    
    Return result and new iterator
    """
    result = iterator.next()
    return result, itertools.chain((result,), iterator)

# Peeking at first value
# ----------------------

def chain_peek(iterator, N):
    """peek at first value in iterator and push it back with chain"""
    for _ in xrange(N):
        result, iterator = peek_with_chain(iterator)
    assert iterator.next() == 0
    return iterator

def chain_get(iterator, N):
    """get M values from iterator"""
    for _ in xrange(N):
        result = iterator.next()

