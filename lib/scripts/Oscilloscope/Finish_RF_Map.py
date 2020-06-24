# Read in traces

import numpy as np

rf_50_100 = np.loadtxt('C:/Users/barium133/Code/barium/lib/scripts/Oscilloscope/rf_settings_50_100.txt')
rf_101_400 = np.loadtxt('C:/Users/barium133/Code/barium/lib/scripts/Oscilloscope/rf_settings_101_400.txt')
rf_401_770 = np.loadtxt('C:/Users/barium133/Code/barium/lib/scripts/Oscilloscope/rf_settings_401_770.txt')
#rf_701_1000 = np.loadtxt('C:/Users/barium133/Code/barium/lib/scripts/Oscilloscope/rf_settings_701_1000.txt')
#rf_1001_1233 = np.loadtxt('C:/Users/barium133/Code/barium/lib/scripts/Oscilloscope/rf_settings_1001_1233.txt')


rf_map = np.append(rf_50_100, rf_101_400,  axis = 0)
rf_map = np.append(rf_map, rf_401_770 , axis = 0)
#rf_map = np.append(rf_map, rf_701_1000 , axis = 0)
#rf_map = np.append(rf_map,rf_1001_1233 , axis = 0)

np.savetxt('C:/Users/barium133/Code/barium/lib/clients/TrapControl_client/rf_map.txt',rf_map,fmt="%0.2f")

print rf_map
