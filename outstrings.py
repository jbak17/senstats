def time_to_str(seconds):
    '''
    convert the number of seconds into a user-readable format.
    Takes number of seconds
    Returns human readable string in HH:MM:SS
    '''
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    out_time = '%d:%02d:%02d' % (h, m, s)
    #return duration
    return out_time

class Outstrings(object):
    """
    Module contains a list of functions to format strings for different senate stat purposes
    """
    def __init__(self):
        pass


    def publicHearingOutString(self, cttee_dictionary):
        '''
        Takes a dictionary and returns a string with:
            -number of meetings by state
            -number of witnesses
            -durations of hearings
        '''
        #cttee_type
        print 'Senate {} Committee'.format(cttee_dictionary['type'])
        print '='*15
        #hearings
        print 'There were  {}  hearings'.format(cttee_dictionary['hearings'])
        #states
        print cttee_dictionary['locations']
        #duration
        time = time_to_str(cttee_dictionary['duration'])
        print 'The total duration of these hearings was  {}'.format(time)

        #witnesses
        print '{}  people appeared before the committee as witnesses'.format(cttee_dictionary['witnesses'])
        #hansard pages
        print '{}  pages of evidence were gathered in Hansard'.format(cttee_dictionary['hansard'])
        print '-'*15
        return ''

    def submissionsOutString(self, arg):
        '''
        Takes a tuple of number of submissions and number of page and returns string
        '''
        pass

    # locations = {'ACT': 0, 'WA': 1, 'NT': 0, 'SA': 0, 'QLD': 2, 'NSW': 0, 'VIC': 0, 'TAS': 0}
    # leg_cttee = {'type': 'Legislation', 'hearings': 0, 'duration': 1, 'witnesses': 23, 'locations': locations.copy(), 'hansard': 200 };
    # publicHearingOutString(leg_cttee)

class Converters(object):
    '''
    Class to hold all the converter functions for senstats
    '''
    def __init__(self):
        pass
