#########################################################################
# title: Collect_VS_Stats.py                                            #
# author: Dario Garrido                                                 #
# date: 20200409                                                        #
# description: Collect VS Stats from an already kwown VS name           #
#########################################################################

from f5.bigip import ManagementRoot
from f5.utils.responses.handlers import Stats

# ----------------------------------------------------------

session = ManagementRoot("F5_mgmt_IP","username","password",token=True)

virtual = session.tm.ltm.virtuals.virtual.load(name='testVS')
#https:// <F5_mgmt_IP>/mgmt/tm/ltm/virtual/testVS
virtualstats = Stats(virtual.stats.load())
#https:// <F5_mgmt_IP>/mgmt/tm/ltm/virtual/testVS/stats
for key, value in virtualstats.stat.items():
    if value.get('description') != None:
        print("{}: {}".format(key, value.get('description')))
    elif value.get('value') != None:
        print("{}: {}".format(key, value.get('value')))

# ----------------------------------------------------------
