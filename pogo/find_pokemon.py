#!/usr/bin/python
import argparse
import logging
import time
import sys
from custom_exceptions import GeneralPogoException

from api import PokeAuthSession
from location import Location
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

blacklist = [46]

search_locations = denbosch_centrum + water_locations

last_search_location = 0

SEARCH_POKEMON = 1
SEARCH_STOPS = 2
POKEBALL = 1
GREATBALL = 2
ULTRABALL = 3
MAX_EMPTY_SEARCHES = 2

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


def sortClosePokemon(session, minimum_id=None):
    """Get Map details and print pokemon"""

    ordered_pokemons = []
    logging.info("Searching for pokemon")
    cells = session.getMapObjects()

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
                    logging.debug('Ignoring pokemon {0} with id {1}, because its below {2}'.format(pokedex.Pokemons[pokemon_id],
                                                                                                   pokemon_id,
                                                                                                   minimum_id))
                    continue

            rarity = pokedex.RarityByNumber(pokemon_id)

            # Fins distance to pokemon
            dist = Location.getDistance(
                latitude,
                longitude,
                pokemon.latitude,
                pokemon.longitude
            )

            # Log the pokemon found
            logging.info("%s, %f meters away" % (
                pokedex.Pokemons[pokemon_id],
                dist
            ))

            ordered_pokemons.append({'distance': dist, 'pokemon': pokemon})

    # Remove visited forts if provided
    ordered_pokemons = sorted(ordered_pokemons, key=lambda k: k['distance'])
    return [instance['pokemon'] for instance in ordered_pokemons]


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

        logging.info("Catching %s:", pokedex.Pokemons[pokemon_id])

        rarity = pokedex.RarityByNumber(pokemon_id)
        if rarity > 3 and session.getInventory()["bag"][3]:
            pokeball = ULTRABALL

        # Use greatballs if all your pokeballs have been used
        if not pokeball:
            if session.getInventory()["bag"][1]:
                pokeball = POKEBALL
            elif session.getInventory()["bag"][2]:
                pokeball = GREATBALL
            elif session.getInventory()["bag"][3]:
                pokeball = ULTRABALL

        session.walkTo(pokemon.latitude, pokemon.longitude, step=3.2)
        logging.info(session.encounterAndCatch(pokemon, pokeball=pokeball))
        session.setCoordinates(pokemon.latitude, pokemon.longitude)


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
        session.walkTo(fort.latitude, fort.longitude, step=3.2)
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

    stop = False
    while not stop:
        visited_stops = []
        forts = sortCloseForts(session, visited=visited_stops)
        for fort in forts:
            walkAndSpin(session, fort)
            visited_stops.append(fort.id)
            forts = sortCloseForts(session, visited=visited_stops)
            time.sleep(1)
        session = poko_session.authenticate(get_nex_location())


def botThePokemon(session):
    # Trying not to flood the servers
    cooldown = 1

    # Pokemon related
    empty_searches = 0
    stop = False
    while not stop:
        try:
            # stop for now, when we have 250 pokemon
            if len(session.getInventory()["party"]) >= 250:
                stop = True

            # Use greatballs if all your pokeballs have been used
            if session.getInventory()["bag"][2] < 2:
                botTheStops(session)

            # When we haven't found a pokemon for 10 searches in a row, let's move on
            if empty_searches >= MAX_EMPTY_SEARCHES:
                session = poko_session.authenticate(get_nex_location())
                empty_searches = 0

            sorted_list_of_pokemon = sortClosePokemon(session, minimum_id=53)
            if not sorted_list_of_pokemon:
                empty_searches += 1

            for pokemon in sorted_list_of_pokemon:
                walkAndCatch(session, pokemon)
                empty_searches = 0
            time.sleep(3)
        except Exception as e:
            logging.critical("Exception detected! [%s], trying to continue!", traceback.format_exc())
            session = poko_session.authenticate(search_locations[1])
            time.sleep(cooldown)
            cooldown *= 2
            continue

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
