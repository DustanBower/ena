#!/usr/bin/env python
from datetime import datetime

import config
import ena
import gspread


gdrive = gspread.login(config.USERNAME, config.PASSWORD)
#for worksheet in gdrive.open(config.FILENAME).worksheets()
#    worksheet.sheet1.col_values(rows.index('Allegiance') + 1)

#dict = {}
#for worksheet in gdrive.open(config.FILENAME).worksheets()
#    lines = worksheet.get_all_values()
#    headers = lines.pop(0)
#    for line in lines:
#        for num, value in enumerate(line):
#            dict[headers[num]] = value


# maybe make a list of dictionaries
#data = []
#for worksheet in gdrive.open(config.FILENAME).worksheets()
#    lines = worksheet.get_all_values()
#    headers = lines.pop(0)
#    for line in lines:
#        dict = {}
#        for num, value in enumerate(line):
#            dict[headers[num]] = value
#        data.append(dict)

def login(username, password):
    return gspread.login(username, password)


def spreadsheet(login, filename):
    return login.open(filename)


def filter(data, month=None):
    """
    Filter a list of dictionaries so the specified value it matches specified
            terms.  (for now we just filter by months)

    data: the list of dictionaries to consider

    month: Specify a particular month to filter against.

    """

    if month:
        # Only copy the data that matches the specified month to the new list
        data = [_ for _ in data
                if datetime.strptime(_[config.DATE_FIELD],
                                     config.DATE_FORMAT).month == month]

    return data


def data_to_dict(spreadsheet_data):
    """
    Convert list of lists where the first entry is a list of headers into
        a list of dictionaries where the values are matched to their
        appropriate headers.  (i.e., [['lives', 'score'], ['1', '99'],
        ['3', '0']]  becomes [{'lives': '1', 'score': '99'}, {'lives': '1',
            score: '99'}]

    """

    # get our new key values from the first entry in the list of lists
    headers = spreadsheet_data.pop(0)

    data = [] 

    # go line by line and convert everything
    for line in spreadsheet_data:
        dict = {}
        for num, value in enumerate(line):
            dict[headers[num]] = value

        data.append(dict)

    return data
