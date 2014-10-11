#!/usr/bin/env python
import unittest

import config
import ena

class LoginTest(unittest.TestCase):
    def test_login(self):
        _ = ena.login(config.USERNAME, config.PASSWORD)

class Spreadsheet(unittest.TestCase):
    def test_spreadsheet(self):
        gdrive = ena.login(config.USERNAME, config.PASSWORD)
        _ = ena.spreadsheet(gdrive, config.FILENAME)


class TestDataToDict(unittest.TestCase):
    def test_data_to_dict(self):
        data = [
            ['Timestamp', 'What is your name?',
             'What is your Membership Number?',
             'Which PC will you be portraying today?',
             'Clan / Character Type', 'Covenant', 'Cadence',
             'What is your City Status (Locals Only)',
             'This is the PC I want counted for purposes '
             'of Ascendancy/Eminence'],
            ['7/8/14 14:43', 'Nintendo', 'MUSHROOMKINGDOM4', 'Bonzai Bill',
             'Bullet', 'Bowserite', '1', '0 - None or Non Local', 'Yes'],
            ['9/19/14 12:43', 'Nintendo', 'HYRULE9', 'Zelda',
             'Princess', 'Hyrulean', '5', '5', 'Yes']
        ]

        result = [
            {'Timestamp': '7/8/14 14:43',
             'What is your name?': 'Nintendo',
             'What is your Membership Number?': 'MUSHROOMKINGDOM4',
             'Which PC will you be portraying today?': 'Bonzai Bill',
             'Clan / Character Type': 'Bullet',
             'Covenant': 'Bowserite',
             'Cadence': '1',
             'What is your City Status (Locals Only)': '0 - None or Non Local',
             'This is the PC I want counted for purposes '
             'of Ascendancy/Eminence': 'Yes'},
            {'Timestamp': '9/19/14 12:43',
             'What is your name?': 'Nintendo',
             'What is your Membership Number?': 'HYRULE9',
             'Which PC will you be portraying today?': 'Zelda',
             'Clan / Character Type': 'Princess',
             'Covenant': 'Hyrulean',
             'Cadence': '5',
             'What is your City Status (Locals Only)': '5',
             'This is the PC I want counted for purposes '
             'of Ascendancy/Eminence': 'Yes'}
        ]

        self.assertEqual(ena.data_to_dict(data), result)


class TestFilter(unittest.TestCase):
    def test_filter(self):
        data = [
            ['Timestamp', 'What is your name?',
             'What is your Membership Number?',
             'Which PC will you be portraying today?',
             'Clan / Character Type', 'Covenant', 'Cadence',
             'What is your City Status (Locals Only)',
             'This is the PC I want counted for purposes '
             'of Ascendancy/Eminence'],
            ['7/8/13 14:43', 'Nintendo', 'MUSHROOMKINGDOM4', 'Bonzai Bill',
             'Bullet', 'Bowserite', '1', '0 - None or Non Local', 'No'],
            ['9/19/14 12:43', 'Nintendo', 'HYRULE9', 'Zelda',
             'Princess', 'Hyrulean', '5', '5', 'Yes']
        ]

        set1 = {'Timestamp': '7/8/13 14:43',
                  'What is your name?': 'Nintendo',
                  'What is your Membership Number?': 'MUSHROOMKINGDOM4',
                  'Which PC will you be portraying today?': 'Bonzai Bill',
                  'Clan / Character Type': 'Bullet',
                  'Covenant': 'Bowserite',
                  'Cadence': '1',
                  'What is your City Status (Locals Only)':
                        '0 - None or Non Local',
                  'This is the PC I want counted for purposes '
                  'of Ascendancy/Eminence': 'No'}

        set2 = {'Timestamp': '9/19/14 12:43',
                 'What is your name?': 'Nintendo',
                 'What is your Membership Number?': 'HYRULE9',
                 'Which PC will you be portraying today?': 'Zelda',
                 'Clan / Character Type': 'Princess',
                 'Covenant': 'Hyrulean',
                 'Cadence': '5',
                 'What is your City Status (Locals Only)': '5',
                 'This is the PC I want counted for purposes '
                 'of Ascendancy/Eminence': 'Yes'}

        data1 = ena.data_to_dict(data)
        self.assertEqual(ena.filter_list(data1), data1)
        self.assertEqual(ena.filter_list(data1, {'month': 9}), [set2])

        self.assertEqual(ena.filter_list(data1, {'month': 7}),
                         [set1])

        data2 = ena.data_to_dict(data)
        self.assertEqual(ena.filter_list(data2), data2)
        self.assertEqual(ena.filter_list(data2, {'year': 2013}), [set1])
        self.assertEqual(ena.filter_list(data2, {'year': 2014}), [set2])

        self.assertEqual(ena.filter_list(data2, {'year': 13}), [set1])
        self.assertEqual(ena.filter_list(data2, {'year': 14}), [set2])

        data3 = ena.data_to_dict(data)
        self.assertEqual(ena.filter_list(data3), data3)
        self.assertEqual(ena.filter_list(data3, {'clan': 'princess'}), [set2])
        self.assertEqual(ena.filter_list(data3, {'covenant': 'hyrulean'}), [set2])

        self.assertEqual(ena.filter_list(data3, {'clan': 'bullet'}), [set1])
        self.assertEqual(ena.filter_list(data3, {'covenant': 'bowserite'}), [set1])

        data4 = ena.data_to_dict(data)
        self.assertEqual(ena.filter_list(data4), data4)

        self.assertEqual(ena.filter_list(data4, {'count?': 'yes'}), [set2])
        self.assertEqual(ena.filter_list(data4, {'count?': 'no'}), [set1])



class ParseMonthTest(unittest.TestCase):
    def test_parse_date(self):
        values = (("1/12", {'month': 1, 'year': 12}),
                  ("2/12", {'month': 2, 'year': 12}),
                  ("2/14", {'month': 2, 'year': 14}),
                 )
        for date_string, result in values:
            self.assertEqual(ena.parse_date(date_string), result)


class TestStatusCalculation(unittest.TestCase):
    def test_calculate_status(self):
        data = [
            ['Timestamp', 'What is your name?',
             'What is your Membership Number?',
             'Which PC will you be portraying today?',
             'Clan / Character Type', 'Covenant', 'Cadence',
             'What is your City Status (Locals Only)',
             'This is the PC I want counted for purposes '
             'of Ascendancy/Eminence'],
            ['7/8/13 14:43', 'Nintendo2', 'MUSHROOMKINGDOM4', 'Bonzai Bill',
             'Bullet', 'Bowserite', '1', '0 - None or Non Local', 'Yes'],
            ['9/19/14 12:43', 'Nintendo1', 'HYRULE9', 'Zelda',
             'Princess', 'Hyrulean', '5', '5', 'Yes'],
            ['9/29/14 11:43', 'Nintendo1', 'HYRULE9', 'Zelda',
             'Princess', 'Hyrulean', '5', '5', 'Yes']
        ]

        member_results = {'clan': {'bullet': 1, 'princess': 1},
                          'covenant': {'bowserite': 1, 'hyrulean': 1}}

        status_results = {'clan': {'bullet': 0, 'princess': 5},
                          'covenant': {'bowserite': 0, 'hyrulean': 5}}

        dict_data = ena.data_to_dict(data)
        ena.STFU = True
        members, statuses = ena.calculate_status(dict_data)
        self.assertEqual(members, member_results)
        self.assertEqual(statuses, status_results)


if __name__ == '__main__':
    unittest.main()

