'''
Establishes database for Senstat program.
Tables:
    State ;; jurisdiction:
        -id
        -city
        -state
'''

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Jurisdiction(Base):
    __tablename__ = 'Jurisdiction' #name of table
    id = Column(Integer, primary_key = True)
    city = Column(String(50), nullable = False)
    state = Column(String(50), nullable = False)

    def __repr__(self):
        return "<  Table entry: ID  %d, city  %s, state  %s  >" % (self.id, self.city, self.state)

engine = create_engine('sqlite:///senstat_db.db')

Base.metadata.create_all(engine)
