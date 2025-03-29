

def norm(code):
    ''' Normalize input code: 
    - cut extra indent'''
    ind = 0
    for s in code:
        if s == ' ':
            ind += 1
        else:
            break
    return '\n'.join([s[ind:] for s in code.splitlines()])