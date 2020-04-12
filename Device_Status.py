#########################################################################
# title: Device_Status.py                                               #
# author: Dario Garrido                                                 #
# date: 20200409                                                        #
# description: Collect Device status                                    #
#########################################################################

from f5.bigip import ManagementRoot

# ----------------------------------------------------------

session = ManagementRoot("F5_mgmt_IP","username","password",token=True)

# https:// <F5_mgmt_IP>/mgmt/tm/cm/device
devices = session.tm.cm.devices.get_collection()
for device in devices:
    print("Device: {}".format(device.name))
    print("State: {}".format(device.failoverState))

# ----------------------------------------------------------
