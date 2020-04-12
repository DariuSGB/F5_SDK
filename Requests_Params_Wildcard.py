#########################################################################
# title: Requests_Params_Wildcard.py                                    #
# author: Dario Garrido                                                 #
# date: 20200410                                                        #
# description: Example of using request_params with wildcard            #
#########################################################################

from f5.bigip import ManagementRoot

# ----------------------------------------------------------

session = ManagementRoot("F5_mgmt_IP","username","password",token=True)

virtuals = session.tm.ltm.virtuals.get_collection(requests_params={'params': 'options=test*'})
# https:// <F5_mgmt_IP>/mgmt/tm/ltm/virtual?options=test*
for virtual in virtuals:
	print("VS Name: {}".format(virtual.name))
	print("VS Destination: {}".format(virtual.destination))

# ----------------------------------------------------------
