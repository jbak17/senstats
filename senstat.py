"""
This program will return the hours of a public hearing in a .txt file, assuming that Hansard has used standard wordings naming committees.
This program will not work for a sub-committee.
"""
import re
import os
import glob
import datetime
import string

#consider each text file in directory and print start, finish and suspension times.
def cttee_type(file):
    '''
    Takes a file of format .txt and identifies if the committee is legislation, reference, or sub-committee.
    Returns the type of committee as string.
    '''
    cttee = None;
    sub_cttee = False
    with open(file) as f:
        while cttee == None:
            for line in f:
                line = line.rstrip()
                #looks for lines that start with a capital C and include a time.
                if re.search('REFERENCES COMMITTEE', line):
                    cttee = 'References'
                    break
                elif re.search('LEGISLATION COMMITTEE', line):
                    cttee = 'Legislation';
                    break
                else:
                    continue
    return cttee

cttee_type()
def witness_count():
    '''
    Takes a file of format .txt and counts the number of witnesses at a public hearing and returns an int.
    '''

def hearing_duration(path):
    '''
    Takes a path and iterates over the files in that folder ending in .txt.
    Function returns a string indicating how much time the hearing in the relevant folder ran for.
    '''
    for file in glob.glob((path+'/*.txt')):
        times = []
        with open(file) as f:
            for line in f:
                line = line.rstrip()
                #looks for lines that start with a capital C and include a time.
                if re.search('Committee.+[0-9][0-9]:[0-9][0-9]', line):
                    times.append(line)
                #looks for lines that start with a capital P and include a time.
                if re.search('Proceedings suspended.+[0-9][0-9]:[0-9][0-9]', line):
                    times.append(line)

            #extract times from lines and place into array.
            times_clean = []
            for line in times:
                temp = line.split()
                for i in temp:
                    if re.search('^[0-9].+?', i):
                        times_clean.append(i.translate(string.maketrans("",""), string.punctuation))
            #print times_clean      #degugging print statement

            #calculate durations
            try:
                assert True, len(times_clean) % 2 == 0
            except AssertionEror as e:
                raise 'An incorrect number of times were found, program cannot guarantee accuracy of reported times.'
            time_total = 0
            duration = []
            while len(times_clean) != 0:
                start = times_clean.pop(0)
                end = times_clean.pop(0)
                duration.append(datetime.timedelta(minutes=int(end[-2:]), hours=int(end[:2])) - datetime.timedelta(minutes=int(start[-2:]), hours=int(start[:2])))

            for i in duration:
                time_total += i.total_seconds()
            #convert the number of seconds into a user-readable format.
            m, s = divmod(time_total, 60)
            h, m = divmod(m, 60)
            out_time = '%d:%02d:%02d' % (h, m, s)

            #return duration
            return 'Hearing {} ran for {}.'.format(file, out_time)
