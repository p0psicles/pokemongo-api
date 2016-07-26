#!/usr/bin/python
import argparse
import logging
import time
import sys
from custom_exceptions import GeneralPogoException

from api import PokeAuthSession
from location import Location
from inventory import items
import traceback

from pokedex import pokedex
from pogo.POGOProtos.Settings.Master.Item.PokeballAttributes_pb2 import PokeballAttributes

water_locations = [
    'Den Bosch, Zuidwal 11',
    '51.683096, 5.302949',
    '51.684959, 5.301098',
    '51.683661, 5.296121',
    '51.679782, 5.294437',
    '51.682904, 5.293952',
    '51.681795, 5.289870',
    '51.687805, 5.293879',
    '51.691384, 5.299243',
    '51.694217, 5.299179',
    '51.702921, 5.290038',
]

tilburg = ['51.560125, 5.083498',
           '51.559538, 5.091222',
           '51.562606, 5.091137',
           '51.567434, 5.088304',
           '51.567141, 5.081867',
           '51.563860, 5.083498',
           '51.560178, 5.078005',
           '51.556843, 5.077704',
           '51.552147, 5.080708',
           '51.557670, 5.081309',
           '51.558657, 5.087532',
           '51.556124, 5.091115',
           '51.553803, 5.089023',
           '51.552575, 5.092692',
           '51.552195, 5.094827',
           '51.552702, 5.097338',
           '51.555715, 5.096345',
           '51.558365, 5.094457',
           '51.560284, 5.081264',
           ]

denbosch_centrum = ['Den Bosch, Postelstraat',
                    'Den Bosch, Vughterstraat 89',
                    'Den Bosch, Sint Jorisstraat',
                    'Den Bosch, Spinhuiswal 1',
                    'Den Bosch, Zuidwal 11',
                    'Den Bosch, Waterstraat 3',
                    'Den Bosch, Parade 23',
                    "Hinthamerstraat 76, 5211 MS 's-Hertogenbosch",
                    "Torenstraat 2-18, 5211 's-Hertogenbosch",
                    "Kerkstraat 48, 5211 KH 's-Hertogenbosch",
                    "Korte Putstraat 13, 5211 KP 's-Hertogenbosch",
                    "Achter Het Stadhuis 10, 5211 HN 's-Hertogenbosch",
                    "Citadellaan 26, 5211 XB 's-Hertogenbosch",
                    "Markt 53, 5211 JW 's-Hertogenbosch"]

bijlmer = ['52.313873, 4.951974',
           '52.312925, 4.924999',
           '52.298204, 4.939119',
           '52.307218, 4.964653',
           '52.312935, 4.981653',
           '52.316280, 4.979121',
           '52.316745, 4.969101',
           '52.340654, 4.992044',
           '52.349149, 5.004146',
           '52.355597, 4.980886',
           '52.314502, 4.941578',
           ]

zuiderplas = [
              '51.672547, 5.312482',
              '51.674729, 5.311774',
              '51.677204, 5.312976',
              '51.675621, 5.318319',
              '51.677909, 5.318469',
              '51.678002, 5.323812',
              "Pettelaarse Schans, De Pettelaarse Schans, 's-Hertogenbosch",
              '51.677714, 5.328566',
              '51.678105, 5.334394',
              '51.676092, 5.333203',
              '51.672882, 5.323460',
              '51.671574, 5.314402',
              ]

zandvoort = ['2042 AG Zandvoort',
             'Schelpenplein 19, 2042 HJ Zandvoort',
             'Zuidstrand 7, 2042 AG Zandvoort',
             '52.342815, 4.503499',
             '52.333376, 4.497319',
             '52.322832, 4.489809',
             '52.311919, 4.481741',
             '52.322832, 4.489809',
             '52.333376, 4.497319',
             '52.342815, 4.503499',
             'Zuidstrand 7, 2042 AG Zandvoort',
             ]

texel = ['52.998429, 4.766776',
         '53.000082, 4.738967',
         '53.011238, 4.735190',
         '53.019706, 4.719741',
         '53.032509, 4.710814',
         '53.049229, 4.716651',
         '53.068315, 4.725920',
         'Ruijslaan 92, 1796 AZ De Koog',
         '53.094918, 4.748751',
         '53.131573, 4.788706',
         '53.146814, 4.818231',
         '53.167194, 4.825441',
         '53.183968, 4.846894',
         '53.158861, 4.875390',
         '53.136829, 4.905945',
         '53.116846, 4.897362',
         '53.101801, 4.894272',
         '53.077471, 4.892899',
         '53.056842, 4.871956',
         '53.032717, 4.829935',
         '53.006488, 4.783930',
         ]

blacklist = [46]

search_locations = tilburg

last_search_location = 0

SEARCH_POKEMON = 1
SEARCH_STOPS = 2
POKEBALL = 1
GREATBALL = 2
ULTRABALL = 3
MAX_EMPTY_SEARCHES = 1
BLACKLIST = [60, 69, 90, 98, 116, 118, 120]
search_mode = SEARCH_POKEMON


def get_nex_location():
    global last_search_location
    if last_search_location + 1 > len(search_locations) - 1:
        last_search_location = 0
    last_search_location += 1
    return search_locations[last_search_location]


def setupLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('Line %(lineno)d,%(filename)s - %(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


# Example functions
# Get profile
def getProfile(session):
        logging.info("Printing Profile:")
        profile = session.getProfile()
        logging.info(profile)


def sortClosePokemon(session, minimum_id=None, blacklist=None):
    """Get Map details and print pokemon"""

    ordered_pokemons = []
    logging.info("Searching for pokemon")
    cells = session.getMapObjects(radius=20)

    latitude, longitude, _ = session.getCoordinates()
    for cell in cells.map_cells:
        # Heap in pokemon protos where we have long + lat
        pokemons = [p for p in cell.wild_pokemons]
        for pokemon in pokemons:
            # Log the pokemon found
            pokemon_id = getattr(pokemon, "pokemon_id", None)
            if not pokemon_id:
                pokemon_id = pokemon.pokemon_data.pokemon_id

            if minimum_id:
                if pokemon_id < minimum_id:
                    logging.debug('Ignoring pokemon {0} with id {1}, because its below {2}'.format(pokedex[pokemon_id],
                                                                                                   pokemon_id,
                                                                                                   minimum_id))
                    continue

            if blacklist:
                if pokemon_id in blacklist:
                    logging.info('Ignoring pokemon {0} with id {1}, because its blacklisted'.format(pokedex[pokemon_id],
                                                                                                    pokemon_id))
                    continue

            rarity = pokedex.getRarityById(pokemon_id)

            # Fins distance to pokemon
            dist = Location.getDistance(
                latitude,
                longitude,
                pokemon.latitude,
                pokemon.longitude
            )

            # Log the pokemon found
            logging.info("%s, %f meters away" % (
                pokedex[pokemon_id],
                dist
            ))

            ordered_pokemons.append({'distance': dist, 'pokemon': pokemon})

    # Remove visited forts if provided
    ordered_pokemons = sorted(ordered_pokemons, key=lambda k: k['distance'])
    return [instance['pokemon'] for instance in ordered_pokemons]


# Wrap both for ease
def encounterAndCatch(session, pokemon, thresholdP=0.5, limit=5, delay=2):
    # Start encounter
    encounter = session.encounterPokemon(pokemon)

    # Grab needed data from proto
    chances = encounter.capture_probability.capture_probability
    balls = encounter.capture_probability.pokeball_type
    bag = session.checkInventory().bag

    # Have we used a razz berry yet?
    berried = False

    # Make sure we aren't oer limit
    count = 0

    # Attempt catch
    while True:
        bestBall = items.UNKNOWN
        altBall = items.UNKNOWN

        # Check for balls and see if we pass
        # wanted threshold
        for i in range(len(balls)):
            if balls[i] in bag:
                altBall = balls[i]
                if chances[i] > thresholdP:
                    bestBall = balls[i]
                    break

        # If we can't determine a ball, try a berry
        # or use a lower class ball
        if bestBall == items.UNKNOWN:
            if not berried and items.RAZZ_BERRY in bag and bag[items.RAZZ_BERRY]:
                logging.info("Using a RAZZ_BERRY")
                session.useItemCapture(items.RAZZ_BERRY, pokemon)
                berried = True
                time.sleep(delay)
                continue

            # if no alt ball, there are no balls
            elif altBall == items.UNKNOWN:
                raise GeneralPogoException("Out of usable balls")
            else:
                bestBall = altBall

        # Try to catch it!!
        logging.info("Using a %s" % items[bestBall])
        attempt = session.catchPokemon(pokemon, bestBall)
        time.sleep(delay)

        # Success or run away
        if attempt.status == 1:
            return attempt

        # CATCH_FLEE is bad news
        if attempt.status == 3:
            logging.info("Possible soft ban.")
            return attempt

        # Only try up to x attempts
        count += 1
        if count >= limit:
            logging.info("Over catch limit")
            return None


def findClosestPokemon(session):
    """Grab the nearest pokemon details"""
    logging.info("Finding Nearest Fort:")
    return sortClosePokemon(session)[0]


# Catch a pokemon at a given point
def walkAndCatch(session, pokemon, pokeball=None):
    if pokemon:
        pokemon_id = getattr(pokemon, "pokemon_id", None)
        if not pokemon_id:
            pokemon_id = pokemon.pokemon_data.pokemon_id

        logging.info("Catching %s:", pokedex[pokemon_id])

        rarity = pokedex.getRarityById(pokemon_id)

        logging.info("Catching %s:" % pokedex[pokemon_id])
        session.walkTo(pokemon.latitude, pokemon.longitude, step=4.5)
        logging.info(encounterAndCatch(session, pokemon))


# Do Inventory stuff
def getInventory(session):
    logging.info("Get Inventory:")
    logging.info(session.getInventory())


# Basic solution to spinning all forts.
# Since traveling salesman problem, not
# true solution. But at least you get
# those step in
def sortCloseForts(session, visited=[]):
    # Sort nearest forts (pokestop)
    logging.info("Sorting Nearest Forts:")
    cells = session.getMapObjects()
    latitude, longitude, _ = session.getCoordinates()
    ordered_forts = []
    for cell in cells.map_cells:
        for fort in cell.forts:
            dist = Location.getDistance(
                latitude,
                longitude,
                fort.latitude,
                fort.longitude
            )
            if fort.type == 1:
                ordered_forts.append({'distance': dist, 'fort': fort})

    # Remove visited forts if provided
    ordered_forts = [fort for fort in ordered_forts if fort['fort'].id not in visited]
    ordered_forts = sorted(ordered_forts, key=lambda k: k['distance'])
    return [instance['fort'] for instance in ordered_forts]


# Find the fort closest to user
def findClosestFort(session):
    # Find nearest fort (pokestop)
    logging.info("Finding Nearest Fort:")
    return sortCloseForts(session)[0]


# Walk to fort and spin
def walkAndSpin(session, fort):
    # No fort, demo == over
    if fort:
        logging.info("Spinning a Fort:")
        # Walk over
        session.walkTo(fort.latitude, fort.longitude, step=4.5)
        # Give it a spin
        fortResponse = session.getFortSearch(fort)
        # Change my current location to the pokemons location
        session.setCoordinates(fort.latitude, fort.longitude)
        logging.info(fortResponse)


# Walk and spin everywhere
def walkAndSpinMany(session, forts):
    for fort in forts:
        walkAndSpin(fort)


# A very brute force approach to evolving
def evolveAllPokemon(session):
    inventory = session.checkInventory()
    for pokemon in inventory["party"]:
        logging.info(session.evolvePokemon(pokemon))
        time.sleep(1)


# You probably don't want to run this
def releaseAllPokemon(session):
    inventory = session.checkInventory()
    for pokemon in inventory["party"]:
        session.releasePokemon(pokemon)
        time.sleep(1)


# Just incase you didn't want any revives
def tossRevives(session):
    bag = session.checkInventory()["bag"]

    # 201 are revives.
    # TODO: We should have a reverse lookup here
    return session.recycleItem(201, bag[201])


# Set an egg to an incubator
def setEgg(session):
    inventory = session.checkInventory()

    # If no eggs, nothing we can do
    if len(inventory["eggs"]) == 0:
        return None

    egg = inventory["eggs"][0]
    incubator = inventory["incubators"][0]
    return session.setEgg(incubator, egg)


# Basic bot
def simpleBot(session):
    # Trying not to flood the servers
    cooldown = 1

    # Run the bot
    while True:
        try:
            forts = sortCloseForts(session)
            for fort in forts:
                pokemon = findClosestPokemon(session)
                walkAndCatch(session, pokemon)
                walkAndSpin(session, fort)
                cooldown = 1
                time.sleep(1)

        # Catch problems and reauthenticate
        except GeneralPogoException as e:
            logging.critical('GeneralPogoException raised: %s', e)
            session = poko_session.reauthenticate(session)
            time.sleep(cooldown)
            cooldown *= 2

        except Exception as e:
            logging.critical('Exception raised: %s', e)
            session = poko_session.reauthenticate(session)
            time.sleep(cooldown)
            cooldown *= 2


def botTheStops(session):
    # Trying not to flood the servers
    cooldown = 1

    stop = False
    while not stop:
        visited_stops = []
        try:
            forts = sortCloseForts(session, visited=visited_stops)
            logging.info("Detected %s forts, going to spin first 10", len(forts))
            for fort in forts[:100]:
                walkAndSpin(session, fort)
                # visited_stops.append(fort.id)
                # forts = sortCloseForts(session, visited=visited_stops)
                time.sleep(1)
        except Exception:
            logging.critical("Exception detected! [%s], trying to continue!", traceback.format_exc())
            session = poko_session.authenticate(search_locations[1])
            time.sleep(cooldown)
            cooldown *= 2
            continue


def botThePokemon(session):
    # Trying not to flood the servers
    cooldown = 1

    # Pokemon related
    empty_searches = 0
    stop = False
    while not stop:
        try:
            inventory = session.getInventory()
            # stop for now, when we have 250 pokemon
            if len(inventory.party) >= 250:
                stop = True

            # Use greatballs if all your pokeballs have been used
            # Then if greatballs are used, bot the stops
            if inventory.bag[2] < 2:
                botTheStops(session)

            # When we haven't found a pokemon for 10 searches in a row, let's move on
            if empty_searches >= MAX_EMPTY_SEARCHES:
                changeLocation(session, get_nex_location())
                empty_searches = 0
                continue

            sorted_list_of_pokemon = sortClosePokemon(session, minimum_id=60, blacklist=BLACKLIST)
            if not sorted_list_of_pokemon:
                empty_searches += 1

            for pokemon in sorted_list_of_pokemon:
                walkAndCatch(session, pokemon)
                empty_searches = 0
                time.sleep(3)

            time.sleep(2)
        except Exception:
            logging.critical("Exception detected! [%s], trying to continue!", traceback.format_exc())
            session = poko_session.reauthenticate(session)
            time.sleep(cooldown)
            cooldown *= 2
            continue


def changeLocation(session, maps_location):
    location = Location(maps_location, geo_key=None).getGeo(maps_location)
    session.setCoordinates(location.latitude, location.longitude)
    logging.info("Continue to search on location: %s", location)

# Entry point
# Start off authentication and demo
if __name__ == '__main__':
    setupLogger()
    logging.debug('Logger set up')

    # Read in args
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--auth", help="Auth Service", required=True)
    parser.add_argument("-u", "--username", help="Username", required=True)
    parser.add_argument("-p", "--password", help="Password", required=True)
    parser.add_argument("-l", "--location", help="Location", required=True)
    parser.add_argument("-c", "--action", help="Action", required=False)
    parser.add_argument("-g", "--geo_key", help="GEO API Secret")
    args = parser.parse_args()

    # Check service
    if args.auth not in ['ptc', 'google']:
        logging.error('Invalid auth service {}'.format(args.auth))
        sys.exit(-1)

    if 'stop' in args.action.lower():
        search_mode = SEARCH_STOPS
    if 'pokemon' in args.action.lower():
        search_mode = SEARCH_POKEMON

    # Create PokoAuthObject
    poko_session = PokeAuthSession(
        args.username,
        args.password,
        args.auth,
        geo_key=args.geo_key
    )

    # Authenticate with a given location
    # Location is not inherent in authentication
    # But is important to session
    # session = poko_session.authenticate(args.location)
    session = poko_session.authenticate(search_locations[1])

    # Time to show off what we can do
    if session:

        # General
        session.getProfile()
        session.getInventory()

        if search_mode == SEARCH_POKEMON:
            botThePokemon(session)

        elif search_mode == SEARCH_STOPS:
            # Pokestop related
            # Keep track of stops we just visited
            botTheStops(session)

    else:
        logging.critical('Session not created successfully')
