'''
Paralysis C2 source
written by Null
'''

class Colors():
    def __init__(self):
        pass

    def toANSI(self, color:str or tuple) -> str:
        '''
        Parses any color type to ANSI
        '''

        if '#' in color: return self.HEXtoANSI(color) # rgb doesn't use hashtags
        elif type(color) == tuple: return self.RGBtoANSI(color) # and hex doesn't use commas and ()'s
        else: return color

    def HEXtoRGB(self, hex:str) -> tuple:
        '''
        Turns an HEX color code into an RGB one
        '''

        return tuple(int(hex.replace('#','')[i:i+2], 16) for i in (0, 2, 4))
    
    def RGBtoHEX(self, rgb:tuple) -> str:
        '''
        Turns an RGB color code tuple into a HEX color code
        '''

        return f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'
    
    def RGBtoANSI(self, rgb:tuple) -> str:
        '''
        Turns an RGB color code into an ANSI one
        '''

        r,g,b = int(rgb[0]), int(rgb[1]), int(rgb[2])
        return f'\033[38;2;{r};{g};{b}m'
    
    def HEXtoANSI(self, hex:str) -> str:
        '''
        Turns an HEX color code into an ANSI one
        '''

        r,g,b = tuple(int(hex.replace('#','')[i:i+2], 16) for i in (0, 2, 4))
        return f'\033[38;2;{r};{g};{b}m'