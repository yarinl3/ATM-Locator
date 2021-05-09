from geopy.geocoders import Nominatim
from geopy import distance
from prettytable import PrettyTable
import json
import requests
import warnings


def error_check(func):
    try:
        warnings.simplefilter("ignore", UserWarning)
        func()
    except Exception as error:
        print('Error:\n', ValueError(error))
    finally:
        exit(0)


def get_coord(address):
    location = Nominatim(user_agent="atm").geocode(address)
    # checks if the address exists
    if location is None or not (29 < location.latitude < 36) or not (29 < location.longitude < 36):
        print('bad address')
        return None, None
    # fix the bad government table
    return min(location.latitude, location.longitude), max(location.latitude, location.longitude)


def get_atm(meters, address_coord):
    offset = 0
    branch_list, all_results = [], []
    while True:
        url = f'https://data.gov.il/api/3/action/datastore_search_sql?' \
              f'sql=SELECT * from "b9d690de-0a9c-45ef-9ced-3e5957776b26" LIMIT 999 OFFSET {offset}'
        results = json.loads(requests.get(url).text)['result']['records']
        if len(results) == 0:
            break
        for result in results:
            try:
                # fix the bad government table
                x_coord = min(float(result['X_Coordinate']), float(result['Y_Coordinate']))
                y_coord = max(float(result['X_Coordinate']), float(result['Y_Coordinate']))
                # checks which ATMs in range
                if distance.distance((x_coord, y_coord), address_coord).meters <= meters and result['ATM_Type'] == 'משיכת מזומן':
                    # remove duplicated rows (more than one atm machine in the branch).
                    if (result['Bank_Code'], result['Branch_Code']) in branch_list:
                        continue
                    branch_list.append((result['Bank_Code'], result['Branch_Code']))
                    all_results.append(
                        [result['Bank_Name'], str(result['Branch_Code']), result['ATM_Address'], result['City'],
                         result['ATM_Location'].replace('\n', ''), result['ATM_Address_Extra']])
            except:
                pass
        offset += 999
    return all_results


@error_check
def main():
    address_input = input('הכנס כתובת:\n')
    address = get_coord(address_input)
    atm_range = int(input('הכנס טווח במטרים (רדיוס אווירי):\n'))
    if address == (None, None):
        return
    results = get_atm(atm_range, address)
    table = PrettyTable()
    table.field_names = ['שם בנק', 'מספר סניף', 'כתובת', 'עיר', 'מיקום', 'מידע נוסף']
    table.add_rows(results)
    print(table)


if __name__ == '__main__':
    main()
