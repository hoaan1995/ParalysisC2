'''
Paralysis C2 source
written by Null
'''

import re, os
from colored import fg, attr

from src.utils import Utils
from src.core import Core
from src.config import Config
from src.database import Database
from src.themes import Theme

class Reader():

    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.anchors = { "start": "<<", "end": ">>" } 

        # registers the fade function
        self.register_function("color", self._colored)
        self.register_function("fade", self._tfx_fade)

    def _tfx_fade(self, start:str, end:str, text:str, ignore:bool=False, text_color:str="\033[0m") -> str:
        '''
        Helper function for the _fade function
        '''
        start = self._str_to_tuple(start)
        end = self._str_to_tuple(end)
        
        return self._fade(start, end, text, ignore, text_color)

    def _colored(self, hex: str):
        try: return fg(hex)
        except Exception: return attr(hex)

    def _fade(self, start:tuple, end:tuple, text:str, ignore_alpha:bool=False, text_color:str="\033[0m") -> str:
        '''
        Gives a line of text a cool ANSI fade
        '''
        result = ""

        changer = int((int(end[0]) - int(start[0])) / len(text))
        changeg = int((int(end[1]) - int(start[1])) / len(text))
        changeb = int((int(end[2]) - int(start[2])) / len(text))
        r, g, b = int(start[0]), int(start[1]), int(start[2])

        for letter in text:
            if letter == "\n": # don't bother fading newlines
                pass

            if ignore_alpha:
                if letter.isalpha() or letter.isnumeric():
                    result += text_color + letter

                    r += changer; g += changeg; b += changeb 
                    continue

            result += "\x1b[40;38;2;%s;%s;%sm%s\033[0m" % (r, g, b, letter) # ANSI escape sequence
            r += changer; g += changeg; b += changeb 
        
        return result

    def _str_to_tuple(self, string:str) -> tuple:
        '''
        Turns a string into an Tuple
        '''
        x = string.split(',' if ',' in string else '/')
        return (x[0], x[1], x[2])

    def register_variable(self, name:str, value:str) -> None:
        '''
        Registers a variable
        '''
        if name in self.variables.keys():
            raise Exception(f"A variable with the name {name} already exists.")

        self.variables[name] = value

    def register_function(self, name:str, func:any):
        '''
        Registers a function
        '''
        if name in self.functions.keys():
            raise Exception(f"A function with the name {name} already exists.")

        self.functions[name] = func
    
    def register_dict(self, data:dict) -> None:
        '''
        Registers a dictionary full of variables
        '''
        for name, value in data.items():
            self.register_variable(name, value)

    def stripper(self, string:str) -> str:
        '''
        Strips string characters from the specified string
        '''
        for x in ['"', "'", '''"""''', """'''"""]:
            string=string.replace(x, "")
        return string

    def execute_file(self, username:str, file:str) -> str:
        '''
        Executes a file at once
        '''
        path = (f'assets/themes/{Theme.getTheme(username)}/{file}' + ('.tfx' if not file.endswith('.tfx') else '')) if not 'assets/commands' in file else file
        if not os.path.isfile(path): return ''
        with open(path, buffering=(2048*2048), encoding="utf-8") as f:
            output = self.execute(f.read())
        return output

    def execute_realtime(self, username:str, file:str, func:any) -> None:
        '''
        Executes a file line by line
        '''
        path = (f'assets/themes/{Theme.getTheme(username)}/{file}' + ('.tfx' if not file.endswith('.tfx') else '')) if not 'assets/commands' in file else file
        if not os.path.isfile(path): return 
        with open(path, buffering=(2048*2048), encoding="utf-8") as f:
            for line in f.read().split("\n"):
                try: func(self.execute(line))
                except: pass

    def execute(self, string:str) -> str:
        '''
        This is where the magic happens, basically runs over a string and replaces the tfx variables and functions with the registered output
        '''
        output = string

        for line in re.findall(fr"(\<\<(.*?)\>\>)", string):
            value = line[1]

            if value.startswith("$"): # variable
                name = self.variables.get(value.replace("$",""))
                if name is None: # not found? we ignore it
                    continue

                output = output.replace(f"<<{value}>>", str(name))

            elif "(" in line[1] and ")" in line[1]: # function

                arguments = value.split("(")[1].split(")")[0]
                arglist = arguments.split(",") if len(arguments.split(",")) > 1 else [arguments]
                arguments = [int(x) if x.isdigit() else float(x) if re.match(r"^-?\d+(?:\.\d+)$", x) else self.stripper(x) for x in arglist]

                getfunc = self.functions.get(value.split("(")[0])
                if getfunc is None: # didn't find anything? if so, we skip
                    continue

                # run with or without arguments
                if arglist[0] == "": func_output = getfunc()
                else: func_output = getfunc(*arguments)
                
                output = output.replace(line[0], "" if func_output is None else str(func_output))
        return output # return the output