import argparse
import requests
import json
import time
import datetime
import telepot
import numpy as np 
import pandas as pd
from bs4 import BeautifulSoup
from telepot.loop import MessageLoop


TOKEN = None

class ZenitBot:
    '''
    this bot finds the opening hours of the zenit gym and posts them into a chat if asked to
    if added to a chat, print /info to get functions

    __init__() - 
    get_week_changes() - 
    get_todays_time() - 
    get_week_time() - 
    get_info() - 
    handle() - 
    '''

    def __init__(self):
        '''
        initialize telegram bot
        '''

        self.bot = telepot.Bot(TOKEN)
        self.dt = pd.read_json('/home/hanzule/zenit/default_times.json') # load default opening hours
        MessageLoop(self.bot, self.handle).run_as_thread()


    def get_week_changes(self):
        '''
        parse zenit home page for updates in opening times for the current week
        create pandas dataframe and compare it with the default times
        if there are differences, print them 
        if not, print just the no differences message
        '''

        # parse zenit web page
        info = requests.get('https://www.zenit-klettern.de/')
        soup = BeautifulSoup(info.text, 'html.parser')

        block = soup.find('div', {'id': 'c23'})
        hours = block.find_all('td')
        element = []
        for s in hours:
            element.append(s.text)

        # create dataframe and compare
        self.ct = pd.DataFrame([element[7:14], element[14:]], columns=element[:7])
        rows, cols = np.where((self.dt.values == self.ct.values) == False)

        if len(cols) > 0:
            # find changed times if there are differences
            response = ''
            for i in range(len(cols)):
                col = int(cols[i])
                row = int(rows[i])
                day = self.ct.keys()[col]
                new_time = self.ct.values[row,col]
                old_time = self.dt.values[row,col]

                if row == 0:
                    string = 'öffnet'
                else:
                    string = 'schließt'

                response = response + 'Die Halle {} diese Woche am {} um {} Uhr.\n'.format(string,day,new_time)

        else:
            # write default text if there are no differences
            response = 'Die Öffnungszeiten in dieser Woche sind bisher unverändert.'

        return response


    def get_todays_time(self):
        ''' 
        returns the opening hours for today
        '''

        today = datetime.datetime.today().weekday()

        # parse zenit web page
        info = requests.get('https://www.zenit-klettern.de/')
        soup = BeautifulSoup(info.text, 'html.parser')

        block = soup.find('div', {'id': 'c23'})
        hours = block.find_all('td')
        element = []
        for s in hours:
            element.append(s.text)

        # create dataframe 
        self.ct = pd.DataFrame([element[7:14], element[14:]], columns=element[:7])

        times = self.ct[self.ct.columns[today]].values
        response = 'Die Halle öffnet heute um {} Uhr und schließt um {} Uhr.'.format(times[0], times[1])

        # check if opening hours are regular toady
        if (self.ct[self.ct.columns[today]].values == self.dt[self.dt.columns[today]].values).all():
            response = response + ' Die Öffnungszeiten sind heute regulär.'
        else:
            response = response + ' Die Öffnungszeiten für heute sind verändert.'

        return response


    def get_week_time(self):
        ''' 
        returns the opening hours for this week
        '''

        # parse zenit web page
        info = requests.get('https://www.zenit-klettern.de/')
        soup = BeautifulSoup(info.text, 'html.parser')

        block = soup.find('div', {'id': 'c23'})
        hours = block.find_all('td')
        element = []
        for s in hours:
            element.append(s.text)

        # create dataframe 
        self.ct = pd.DataFrame([element[7:14], element[14:]], columns=element[:7])

        response = 'Die Öffnungszeiten für diese Woche sind: \n'
        for column in self.ct:
            response = response + column + ': ' + str(self.ct[column].values[0]) + ' - ' + str(self.ct[column].values[1]) + '\n'

        return response


    def get_info(self):
        '''
        sends info text to chat
        should contain all or the most important functions
        '''

        response = 'Ich bin ein Bot und kann euch über die Öffnungszeiten der Kletterhalle informieren. Wenn Ihr was wissen wollt, fragt einfach:\n\
                    /heute - gibt euch die heutigen Öffnungszeiten\n\
                    /woche - gibt euch die Öffnungszeiten für diese Woche\n\
                    /anders - gibt euch alle Veränderunge für diese Woche\n\
                    mehr kommt noch...'

        return response



    def handle(self, msg):
        ''' 
        handle commands given to bot
        '''
        
        chat_id = msg['chat']['id']
        command = msg['text']

        if command == '/anders':
            # send changes in opening times to chat
            message = self.get_week_changes()
            print(message)
            self.bot.sendMessage(chat_id, message)

        elif command == '/heute':
            # send todays opening times to chat
            message = self.get_todays_time()
            print(message)
            self.bot.sendMessage(chat_id, message)

        elif command == '/woche':
            # send todays opening times to chat
            message = self.get_week_time()
            print(message)
            self.bot.sendMessage(chat_id, message)

        elif command == '/info':
            # implement helper command
            message = self.get_info()
            print(message)
            self.bot.sendMessage(chat_id, message)

        elif command == '/echo':
            # print chat_id so that bot can post into group chats
            print(chat_id)
            



if __name__ == '__main__':
    #ArgumentParser
    parser = argparse.ArgumentParser(description='Telegram Bot TOKEN:')
    parser.add_argument('-tk','--Token', help='gimme the token', type=str)
    args = vars(parser.parse_args())

    TOKEN = args['Token']

    zb = ZenitBot()
    print ("Let's go...")
    while 1:
        time.sleep(10)



