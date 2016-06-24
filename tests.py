'''
Module to hold unit tests for the senstat.py program.
'''
def test_witness_count(paths):
    for f in paths:
        num = witness_count(f)
        print 'file: {} \n{}'.format(f, num)
        print '\n'

def test_cttee_type():
# block comment below for testing test_cttee_type. Passed on 23/6/16.
    outstring = cttee_type(path); #debugging test
    print outstring;
