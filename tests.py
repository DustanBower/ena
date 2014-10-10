#!/usr/bin/env python
import unittest

import config
import ena

class LoginTest(unittest.TestCase):
    def test_login(self):
        gdrive = ena.login(config.USERNAME, config.PASSWORD)


class Spreadsheet(unittest.TestCase):
    def test_spreadsheet(self):
        gdrive = ena.login(config.USERNAME, config.PASSWORD)
        sheet = ena.spreadsheet(gdrive, config.FILENAME)


class TestDataToDict(unittest.TestCase):
    def test_data_to_dict(self):
        data = [
            ['Timestamp', 'What is your name?',
             'What is your Membership Number?',
             'Which PC will you be portraying today?',
             'Clan / Character Type', 'Covenant', 'Cadence',
             'What is your City Status (Locals Only)',
             'This is the PC I want counted for purposes'
             'of Ascendancy/Eminence'],
            ['7/8/14 14:43', 'Nintendo', 'MUSHROOMKINGDOM4', 'Bonzai Bill',
             'Bullet', 'Bowserite', '1', '0 - None or Non Local', 'Yes'],
            ['9/19/14 12:43', 'Nintendo', 'Hyrule9', 'Zelda',
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
             'This is the PC I want counted for purposes'
             'of Ascendancy/Eminence': 'Yes'},
            {'Timestamp': '9/19/14 12:43',
             'What is your name?': 'Nintendo',
             'What is your Membership Number?': 'Hyrule9',
             'Which PC will you be portraying today?': 'Zelda',
             'Clan / Character Type': 'Princess',
             'Covenant': 'Hyrulean',
             'Cadence': '5',
             'What is your City Status (Locals Only)': '5',
             'This is the PC I want counted for purposes'
             'of Ascendancy/Eminence': 'Yes'}
        ]

        self.assertEqual(ena.data_to_dict(data), result)


class TestDateFilter(unittest.TestCase):
    def test_date_filter(self):
        data = [
            ['Timestamp', 'What is your name?',
             'What is your Membership Number?',
             'Which PC will you be portraying today?',
             'Clan / Character Type', 'Covenant', 'Cadence',
             'What is your City Status (Locals Only)',
             'This is the PC I want counted for purposes'
             'of Ascendancy/Eminence'],
            ['7/8/14 14:43', 'Nintendo', 'MUSHROOMKINGDOM4', 'Bonzai Bill',
             'Bullet', 'Bowserite', '1', '0 - None or Non Local', 'Yes'],
            ['9/19/14 12:43', 'Nintendo', 'Hyrule9', 'Zelda',
             'Princess', 'Hyrulean', '5', '5', 'Yes']
        ]

        month7 = {'Timestamp': '7/8/14 14:43',
                  'What is your name?': 'Nintendo',
                  'What is your Membership Number?': 'MUSHROOMKINGDOM4',
                  'Which PC will you be portraying today?': 'Bonzai Bill',
                  'Clan / Character Type': 'Bullet',
                  'Covenant': 'Bowserite',
                  'Cadence': '1',
                  'What is your City Status (Locals Only)':
                        '0 - None or Non Local',
                  'This is the PC I want counted for purposes'
                  'of Ascendancy/Eminence': 'Yes'}

        month9 = {'Timestamp': '9/19/14 12:43',
                 'What is your name?': 'Nintendo',
                 'What is your Membership Number?': 'Hyrule9',
                 'Which PC will you be portraying today?': 'Zelda',
                 'Clan / Character Type': 'Princess',
                 'Covenant': 'Hyrulean',
                 'Cadence': '5',
                 'What is your City Status (Locals Only)': '5',
                 'This is the PC I want counted for purposes'
                 'of Ascendancy/Eminence': 'Yes'}

        data = ena.data_to_dict(data)
        self.assertEqual(ena.filter(data), data)
        self.assertEqual(ena.filter(data, month=9), [month9])

        self.assertEqual(ena.filter(data, month=7),
                         [month7])


if __name__ == '__main__':
    unittest.main()

