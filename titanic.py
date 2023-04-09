import statistics
from thefuzz import process
import matplotlib.pyplot as plt
import folium
from load_data import load_data


COUNTRY_KEY = 'COUNTRY'
TYPE_KEY = 'TYPE_SUMMARY'
SHIP_NAME_KEY = 'SHIPNAME'
SPEED_KEY = 'SPEED'
LONGITUDE_KEY = 'LON'
LATITUDE_KEY = 'LAT'
SEARCH_ACCURACY = 85


# ========================= Dispatch Actions =========================
def print_functions(dispatch_dict):
    """Print available commands"""
    print('\nAvailable commands:')
    for func in dispatch_dict:
        if func == "top_countries":
            print(func, " <num_countries>")
        else:
            print(func)
    print()


def get_all_countries(traffic_data):
    """Takes traffic data, analyzes it, sorts it alphabetically, and prints
    each country in a new line.
    """
    countries_data = analyze_traffic_data_by(traffic_data, by_key=COUNTRY_KEY)
    sorted_countries = sorted(countries_data)
    print_iterable(sorted_countries)


def top_n_countries(traffic_data, num=5):
    """Takes countries and ships data, sorts it by amount of ships,
    and prints top n countries and their ships.
    """
    countries_data = analyze_traffic_data_by(traffic_data, by_key=COUNTRY_KEY,
                                             is_sorted=True)
    print_iterable(countries_data[:num], value=True)


def get_all_ship_types(traffic_data):
    """Takes traffic data, analyze it and print each ship type and
    amount of ships with that type in the data
    """
    type_data = analyze_traffic_data_by(traffic_data, by_key=TYPE_KEY,
                                        is_sorted=True)
    print_iterable(type_data, value=True)


def search_ship_by_name(traffic_data):
    """Get a set with all ships names from traffic data, get user to input
    search query and return search results which ratio is higher than
    SEARCH_ACCURACY.
    """
    ships_names = {ship[SHIP_NAME_KEY] for ship in traffic_data}
    search_key = input("Enter the search query: ")
    search_results = [ship_name for ship_name, ratio
                      in process.extract(search_key, ships_names)
                      if ratio > SEARCH_ACCURACY]
    if search_results:
        print("Did you mean any of these?")
        print_iterable(search_results)
    else:
        print("No results found")


def save_speed_histogram(traffic_data):
    """Asks the user to provide file name, then plots and saves ships
    speed histogram.
    """
    file_name = input("What's the file name should be? ")
    all_ships_speed = [float(ship[SPEED_KEY]) for ship in traffic_data]
    plt.hist(all_ships_speed, bins=14, color='green')
    plt.savefig(f'{file_name}.png')
    print(f'The ship speed histogram was saved as {file_name}.png')


def draw_plot_map(traffic_data):
    """Get a list of every ship's location data (Name, Latitude and
    Longitude) Create a map using folium library and add a marker to
    each location. Then save the interactive map to a html file and open it.
    """
    ship_locations = [(ship[SHIP_NAME_KEY], float(ship[LATITUDE_KEY]),
                       float(ship[LONGITUDE_KEY])) for ship in traffic_data]

    # Find mean latitude and longitude to center the map
    mean_lat = statistics.mean([float(ship[LATITUDE_KEY])
                                for ship in traffic_data])
    mean_lon = statistics.mean([float(ship[LONGITUDE_KEY])
                                for ship in traffic_data])

    # Create the map and plot each ship's location
    ship_map = folium.Map(location=[mean_lat, mean_lon],
                          control_scale=True, zoom_start=4)
    for name, lat, lon in ship_locations:
        folium.Marker([lat, lon], popup=name).add_to(ship_map)

    ship_map.save('ship_map.html')


DISPATCH_DICT = {
        'help': lambda _, __: print_functions(DISPATCH_DICT.keys()),
        'show_countries': lambda data_dict, _:
        get_all_countries(data_dict),
        'top_countries': lambda data_dict, num:
        top_n_countries(data_dict, num=int(num)),
        'ships_by_types': lambda data_dict, _:
        get_all_ship_types(data_dict),
        'search_ship': lambda data_dict, _:
        search_ship_by_name(data_dict),
        'speed_histogram': lambda data_dict, _:
        save_speed_histogram(data_dict),
        'draw_map': lambda data_dict, _:
        draw_plot_map(data_dict)
    }


# ========================= Assisting Functions =========================
def analyze_traffic_data_by(traffic_data, by_key, is_sorted=False):
    """Takes ships raw data analyzes it by the key and returns
    analyzed dictionary with shipnames in set as value, sorted by set length.
    """
    analyzed_dict = {}
    for ship in traffic_data:
        if ship[by_key] not in analyzed_dict:
            analyzed_dict[ship[by_key]] = set()
        analyzed_dict[ship[by_key]].add(ship[SHIP_NAME_KEY])
    if is_sorted:
        analyzed_dict = sorted(analyzed_dict.items(), key=lambda x: len(x[1]),
                               reverse=True)
    return analyzed_dict


def print_iterable(iterable, value=False):
    """For item in iterable print it in a new line"""
    if not value:
        for item in iterable:
            print(item)
    else:
        for key, val in iterable:
            print(f"{key}: {len(val)}")
    print()


def get_valid_action(dispatcher):
    """Ask user to input action, validate action and returns action
    as well as a secondary parameter or raise an error.
    """
    action = input().strip()
    if not action:
        raise ValueError("Empty input")

    if " " in action and action.startswith("top_countries"):
        action = action.split(maxsplit=1)
        if not action[1].isnumeric():
            print(f"Unknown parameter {action[1]}")
            raise ValueError("Parameter is not integer")
        return action[0], action[1]

    if action not in dispatcher or action == "top_countries":
        print(f"Unknown command {action}")
        raise ValueError("Command is not in dispatcher")
    return action, None


# ========================= Main Function =========================
def main():
    """Main function initiation"""
    all_data = load_data()['data']

    print("Welcome to the Ships CLI! Enter 'help' to view available commands.\n")

    # Initiate while loop to get valid input and initiate func from dispatcher
    while True:
        try:
            action, param = get_valid_action(DISPATCH_DICT)
        except ValueError:
            continue
        DISPATCH_DICT[action](all_data, param)


if __name__ == "__main__":
    main()
