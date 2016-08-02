from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_declarative import Base, Jurisdiction #importing tables 

engine = create_engine('sqlite:///senstat_db.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)

session = DBSession()
library = {'SYDNEY': 'NSW', 'NEWCASTLE': 'NSW', 'MELBOURNE': 'VIC', 'GEELONG': 'VIC', 'BENDIGO': 'VIC', 'CANBERRA': 'ACT', 'ADELAIDE': 'SA', 'PERTH': 'WA', 'HOBART': 'TAS', 'DARWIN': 'NT'}

keys = library.keys()
for i in keys:
    new_location = Jurisdiction(city= i, state=library[i])
    session.add(new_location)

session.commit()
