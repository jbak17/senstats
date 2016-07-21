import os
import shutil
import senstat
from nose import with_setup

'''
Module to hold unit tests for the senstat.py program.
'''
def setup_module():
    os.mkdir('/home/jarrod/workspace/senstats/test_docs/randomplace')
    shutil.copy2('/home/jarrod/workspace/senstats/test_docs/word/7jul.docx', '/home/jarrod/workspace/senstats/test_docs/randomplace')

def teardown_module():
    # path = '/home/jarrod/workspace/senstats/test_docs/activeTest'
    # files = list ( set ( glob.glob (path+'/*.pdf') + glob.glob (path+'/*.docx') + glob.glob(path+'/*.txt') ) )
    # for i in files:
    #     os.remove(i)
    shutil.rmtree('/home/jarrod/workspace/senstats/test_docs/randomplace')

@with_setup(setup_module, teardown_module)
def test_witness_count():
    assert witness_count('/home/jarrod/workspace/senstats/test_docs/randomplace/7jul.docx') == 3

# def test_cttee_type():
# # block comment below for testing test_cttee_type. Passed on 23/6/16.
#     outstring = cttee_type(path); #debugging test
#     print outstring;

# def test_subcount():
#     subtool = classes.SubmissionTools()
#     subs = subtool.count_subs(get_files('/home/jarrod/workspace/senstats/test_docs/subs', 'pdf'))
#     print subs
