#!/usr/bin/env python

"""
Module/Script for parsing sign-in data from google drive and determining
Ascendancy and Eminence.

"""

from collections import defaultdict
from datetime import datetime
import operator

import argparse
import config
import gspread


VERBOSE = False
STFU = False

# lookup fields for rows by name
DATA_FIELDS = {
    "clan": config.CLAN_FIELD,
    "covenant": config.COVENANT_FIELD,
    "count?": config.COUNT_FIELD,
    "player_name": config.PLAYER_NAME,
    "mship_number": config.MEMBERSHIP_NUMBER,
    "status": config.STATUS_FIELD,
}


def login(username, password):
    """
    Log-in to Google Spreadsheets and return a client object.

    username: The username to sign into google docs.
    password: The password for google docs.

    """

    client = gspread.client.Client(auth=(username, password))
    client.login()
    return client


def spreadsheet(client, filename):
    """
    Open and return the spreadsheet of the specified name.

    client: Google drive client
    filename: name of file to open

    """
    return client.open(filename)


def filter_list(data, arguments=None):
    """
    Filter a list of dictionaries so the specified value it matches specified
            terms.  (for now we just filter by months)

    data: the list of dictionaries to consider

    arguments: Specify fields to filter against:
        month: month (int 1 to 12)
        year: year (after 2000.  13 is considered abbreviation for 2013)

        clan: Name of clan
        covenant: Name of covenant
        count?: Whether this entry should be counted for E&A

    """

    if arguments == None:
        arguments = {}

    filter_by = defaultdict(lambda: None)

    for k, v in arguments.iteritems():
        filter_by[k] = v

    special_keys = ['month', 'year']
    special_fields = {}

    # special keys need to be treated differently than regular filters and
    # removed before we handle default filtering
    for field in special_keys:
        special_fields[field] = filter_by[field]
        del filter_by[field]

        if field == 'year':
            year = special_fields['year']
            # strptime gives us the full year, so we need to correct
            # 13 to 2013, etc.
            special_fields['year'] = (year + 2000
                                      if year is not None and year < 2000
                                      else year)

    for date_field in ('month', 'year'):
        # Only copy the data that matches the specified field to the new list

        if special_fields[date_field]:
            data = [_ for _ in data
                    if getattr(datetime.strptime(_[config.DATE_FIELD],
                                   config.DATE_FORMAT),
                               date_field) == special_fields[date_field]]

    for filter_key, filter_value in filter_by.iteritems():
        # update the specified key to match the lookup table used by the
        # data from the spreadsheet
        filter_key = DATA_FIELDS[filter_key]

        data = [_ for _ in data
                if _[filter_key].lower() == filter_value.lower()]

    return data


def data_to_dict(spreadsheet_data):
    """
    Convert list of lists where the first entry is a list of headers into
        a list of dictionaries where the values are matched to their
        appropriate headers.  (i.e., [['lives', 'score'], ['1', '99'],
        ['3', '0']]  becomes [{'lives': '1', 'score': '99'}, {'lives': '1',
            score: '99'}]

    spreadsheet_data: list of lists, where the first item is a list of headers
                    to consider fields of.
    """

    spreadsheet_data = spreadsheet_data[:] # copy data so we don't alter it

    # get our new key values from the first entry in the list of lists
    headers = spreadsheet_data.pop(0)

    data = []

    # go line by line and convert everything
    for line in spreadsheet_data:
        dict_ = {}
        for num, value in enumerate(line):
            dict_[headers[num]] = value

        data.append(dict_)

    return data


def parse_date(date_string):
    """ Parse a date in the form 1/12 into a dict specifying month/year. """

    month, year = date_string.split('/')
    return {'month': int(month), 'year': int(year)}


def calculate_status(data):
    """
    Calculate total status of each Covenant and Clan and return a dictionary.

    data: spreadsheet data in dictionary form

    """
    members = {}
    statuses = {}

    TYPES = ['clan', 'covenant']
    for type_ in TYPES:
        members[type_] = defaultdict(int)
        statuses[type_] = defaultdict(int)

    seen = {}
    seen['mship_numbers'] = []
    seen['players'] = []
    seen['data'] = []

    for entry in data:
        mship_number = entry[DATA_FIELDS['mship_number']].upper()
        player_name = entry[DATA_FIELDS['player_name']].lower()

        if (mship_number in seen['mship_numbers'] or
                player_name in seen['players']):

            for seen_mship, seen_name in seen['data']:
                mship_match = name_match = False

                if seen_mship == mship_number:
                    if VERBOSE:
                        print('match membership')
                    mship_match = True

                if seen_name == player_name:
                    if VERBOSE:
                        print('match name')
                    name_match = True

                if not STFU and (mship_match or name_match):
                    print('{} ({}) collides with {} ({}), excluding'.format(
                        player_name.title(), mship_number, seen_name.title(),
                        seen_mship))

                    break

            if not STFU and not (seen_mship or seen_name):
                print('{} ({}) was excluded for unknown reasons'.format(
                    mship_number, player_name.title()))

            continue

        player = entry[DATA_FIELDS['player_name']].lower()

        # Let's not treat empty mship numbers as matches, or names for that
        # matter.  Empty mship numbers aren't tracked, empty names are forced
        # to be spaces so we can see them on the counted player output and
        # in any collisions that occur.
        if mship_number:
            seen['mship_numbers'].append(mship_number)

        player = ' ' if not player else player
        if player:
            seen['players'].append(player)
        seen['data'].append((mship_number, player))

        for type_ in TYPES:
            type_name = entry[DATA_FIELDS[type_]].lower().strip()
            members[type_][type_name] += 1

            pc_status = entry[DATA_FIELDS["status"]]
            pc_status = (0 if pc_status in config.UNKNOWN_STATUSES
                         else pc_status)
            statuses[type_][type_name] += int(pc_status)


    if not STFU:
        print('Counted status for the following UNIQUE players:')
        if len(seen['players']) == 0:
            print('    None')

        for player in sorted(seen['players']):
            print('    ' + player.title())


    # convert default dicts to regular dicts and return a list
    return [dict(_) for _ in members, statuses]


def show_results(results):
    """
    Sort and display E&A results.

    results: list containing dictionaries, [members, statuses], where members
            is a dictionary of member numbers with clan/covenant as the key,
            and statuses is the same, but with status totals.

            I.e., if the only person who signed in was a status 2 Mekhet,
            results would look like: [{'mekhet': 1}, {'mekhet': 2}]
    """

    members, statuses = results
    for type_ in ['clan', 'covenant']:
        print('')
        print('{0: <19}  total status  # of members'.format(type_.title()))
        for entry, status in sorted(statuses[type_].items(),
                            key=operator.itemgetter(1), reverse=True):
            print('    {0: <19}: {1: <14} {2}'.format(entry.title(), status,
                                             members[type_][entry]))

        print('')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("date", help="month/year in the format 12/14, etc.")
    parser.add_argument("--verbose", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("--stfu", help="only print totals, overrides verbose",
                        action="store_true")
    args = parser.parse_args()

    STFU = args.stfu
    VERBOSE = args.verbose if STFU == False else False

    gdrive = login(config.USERNAME, config.PASSWORD)
    sheet = spreadsheet(gdrive, config.FILENAME)
    sheet_data = data_to_dict(sheet.sheet1.get_all_values())

    args = parse_date(args.date)
    # We only care about PCs who are supposed to be counted
    args['count?'] = 'yes'
    ena_data = filter_list(sheet_data, args)

    show_results(calculate_status(ena_data))
    # FIXME: Write unit tests for number tally
