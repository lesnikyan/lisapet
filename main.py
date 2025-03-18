'''

'''

import argparse
from argparse import ArgumentParser

def main():
    ''' Run script using args from command line '''
    arp = ArgumentParser()
    arp.add_argument('filename')
    arp.add_argument('-c') # in line code
    

if __name__ == '__main__':
    main()
