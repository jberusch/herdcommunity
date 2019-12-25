from app import db
from app.models import Destination

dests_to_be_deleted = ['The Pub at Overcup Oak', 'Richland Creek Greenway', 'Broadway Historic District', 'Papa John’s Pizza', 'Domino’s Pizza', 'The Loving Pie Company - Temp.', 'Movies in the Park', 'Applebee’s Grill + Bar', 'O’Charley’s Restaurant & Bar', 'Reserva Cigars', 'Panda Express', 'Belmont Mansion', 'Bicentennial mall state park', 'Starbucks', 'Five Guys', 'Dunkin', 'Jimmy Johns', 'Play', '21 C Museum Hotel Nashville', 'Chilis', 'Aladdin’s Hookah Lounge and Bar', 'White Castle', 'Elliston Place Soda Shop - Temp.', 'Potbellys', 'Tennessee State Capitol', 'Wendy’s', 'Cannery Ballroom', 'Sevier Park', 'Love Circle', 'Lexus Lounge', 'Subway Restaurants', 'Cumberland Park', 'Craft Vapor', 'Dairy Queen Grill & Chill', 'Yelp Cocktail Society: Mason Bar Edition', 'YSB - UYE - Karaoke Like A Star!', 'Music Row', 'Yelp Spring Break Event: Nashville Brew Bus', 'Fort Negley Park and Visitors Center', 'Nordstrom Ebar Artisan Coffee', 'H-Cue’s Upstairs Poolroom', 'Caesar’s Italian & Pizza Restaurant', 'IHOP', 'Upper Room', 'Riverfront Park', 'The Gulch', 'Yelp Spring Break Event: It’s Spring Break Y’all Party',
    'The Loving Pie Company - Temp. CLOSED',
    'Bicentennial Capitol Mall State Park',
    'Dunkin’',
    'Jimmy John’s',
    'Chili’s',
    'Elliston Place Soda Shop - Temp. CLOSED',
    'Potbelly Sandwich Shop']

for dest_name in dests_to_be_deleted:
    dests = Destination.query.filter_by(name=dest_name).all()
    if len(dests) < 1:
        print('Failed to delete destination with name {}'.format(dest_name))
        continue
    for d in dests:
        db.session.delete(d)

db.session.commit()