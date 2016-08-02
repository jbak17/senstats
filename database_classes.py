#file for classes that operate the Senstat database.
#the database is established once using 'database_declarative.py' and then all further actions are taken from this file.

from database_declarative import Base, Jurisdiction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# class Initialise():
#     def __init__(self):
#         self.engine = create_engine('sqlite:///senstat_db.db')
#         Base.metadata.bind = self.engine
#         self.DBSession = sessionmaker()
#         self.DBSession.bind = self.engine
#         self.session = self.DBSession()
def initialise():
    engine = create_engine('sqlite:///senstat_db.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker()
    DBSession.bind = engine
    return DBSession()

class Query(object):
    def __init__(self):
        self.session = initialise()

    def getJurisdiction(self, place): #place is hearing location
        '''
        Takes a hearing location string and returns the Jurisdiction of the hearing if the location is already in the database.
        If the location is not in the database already it will prompt the user for an answer as to which jurisdiction the location is in.
        '''
        print 'Database being queried...searching for {}'.format(place)
        if self.session.query(Jurisdiction).filter(Jurisdiction.city == place).count() >= 1:
            cit = self.session.query(Jurisdiction).filter(Jurisdiction.city == place)
        else:
            #need to implement function to request location and add that to the database.
            pass
        for instance in cit:
            state = instance.state
        return state

class Insert(object):
    def __init__(self):
        pass

    def __str__(self):
        'Class to hold functions to insert into senstat_db.db'

query = Query()
stat = query.getJurisdiction('SYDNEY')
print stat
