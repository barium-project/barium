class TrapControl_config(object):
    '''
    trap control client configuration file

    Attributes
    ----------
    info: dict
    {Parameter: (Rod1, Rod2, Rod3, Rod4))}
    {endCaps: (endCap 1, endCap 2)
    {einzel lens: (lens 1, lens 2)
    {Ablation loading delay:(time(usec))
    '''
    params = {'Frequency' :(1.099e6, 1.099e6, 1.099e6, 1.099e6),
            'Phase' :(15,170,0,38),
            'Voltage':(186, 1233, 200, 1233),
            'DC':(0,0,0,0),
            'HV':(0,0,1400,1400),
            'endCap':(5,5),
            'eLens':(0,0),
            'Loading Time':(50)
            }
    '''
    IP address of the computer running the server
    '''
    ip = '10.97.111.2'

    ''' Mapping of rods to channels

    rods: dict
    {rod:channel}

    '''

    rods = {'1':3, '2':1, '3':2, '4':0}

    ''' Mapping of end caps to channels

    endCaps: dict
    {end cap : channel}

    '''
    endCaps = {'1':4, '2':5}

    ''' Mapping of einzel lens to channels

    einzel lens: dict
    {Elens : channel}

    '''
    eLens = {'1':4, '2':5}

