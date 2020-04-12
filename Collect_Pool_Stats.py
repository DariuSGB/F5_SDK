#########################################################################
# title: Collect_Pool_Stats.py                                          #
# author: Dario Garrido                                                 #
# date: 20200409                                                        #
# description: Collect Pool Stats from an already kwown Pool name       #
#########################################################################

from f5.bigip import ManagementRoot
from f5.utils.responses.handlers import Stats

# ----------------------------------------------------------

session = ManagementRoot("F5_mgmt_IP","username","password",token=True)

pool = session.tm.ltm.pools.pool.load(name='testPool')
# https:// <F5_mgmt_IP>/mgmt/tm/ltm/pool/testPool
poolstats = Stats(pool.stats.load())
# https:// <F5_mgmt_IP>/mgmt/tm/ltm/pool/testPool/stats
for key, value in poolstats.stat.items():
    if value.get('description') != None:
        print("{}: {}".format(key, value.get('description')))
    elif value.get('value') != None:
        print("{}: {}".format(key, value.get('value')))

# ----------------------------------------------------------
