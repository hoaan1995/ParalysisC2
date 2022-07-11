'''
Paralysis C2 source
written by Null
'''

import pyfiglet
from random import randint, choice, shuffle

class Captcha():
    def __init__(self):
        self.riddles = [
            # format: (riddle, answer)
            # answer will be checked if its IN the response, not if the response is EQUAL to the answer
            # answer is not case sensitive, so go crazy
            ('How many hours are there in a day?', '24'),
            ('What has to be broken before you can use it?', 'egg'),
            ('I have keys, but no locks. I have space, but no room. You can enter, but you can\'t go outside. What am I?', 'keyboard'),
            ('I am not alive, but I grow; I don\'t have lungs, but I need air; I don\'t have a mouth, but water kills me. What am I?', 'fire'),
            ('What can you catch but never throw?', 'cold'),
            ('What is Obama\'s last name?', 'obama') # yes
        ]

        self.fonts = ['5lineoblique','alligator2','banner','banner3','banner4','banner3-D','bell','big','block','computer','contessa','cosmic','cosmike'] # clear to read figlet fonts go here

    def create(self, cptType:int=0) -> tuple or None:
        '''
        Creates a captcha
        '''

        if cptType == 0: # math based captcha, can be easily solved
            calculation = f'{randint(0,100)} + {randint(0,100)}'
            result = eval(calculation) # using eval is a bad habit, but since there is no direct input we're safe to do so

            return (calculation, str(result)) # returns the calculation and the result
        elif cptType == 1: # generates a simple riddle
            shuffle(self.riddles)
            return choice(self.riddles)
        
        elif cptType == 2: # simple "type what it says" captcha
            result = randint(1,99999)

            return (pyfiglet.figlet_format(str(result), font=choice(self.fonts)), str(result))
        
        elif cptType == 3: # generates another math based captcha, but this time a bit harder and with figlet :P
            calculation = f'{randint(0,100)} {choice(["+","-","/","*","^"])} {randint(0,100)}'
            result = eval(calculation)

            return (pyfiglet.figlet_format(calculation, font=choice(self.fonts)), str(result))
        
        else: # invalid choice
            return None