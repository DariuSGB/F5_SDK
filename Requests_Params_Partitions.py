#########################################################################
# title: Requests_Params_Partitions.py                                  #
# author: Dario Garrido                                                 #
# date: 20200410                                                        #
# description: Example of using request_params with partitions          #
#########################################################################

from f5.bigip import ManagementRoot

# ----------------------------------------------------------

session = ManagementRoot("F5_mgmt_IP","username","password",token=True)

virtuals = session.tm.ltm.virtuals.get_collection(requests_params={'params': '$filter=partition+eq+Common'})
# https:// <F5_mgmt_IP>/mgmt/tm/ltm/virtual?$filter=partition+eq+Common
for virtual in virtuals:
	print("VS Name: {}".format(virtual.name))
	print("VS Destination: {}".format(virtual.destination))

# ----------------------------------------------------------
