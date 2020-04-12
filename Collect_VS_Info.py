#########################################################################
# title: Collect_VS_Info.py                                             #
# author: Dario Garrido                                                 #
# date: 20200409                                                        #
# description: Collect VS info from an already kwown VS name            #
#########################################################################

import re
from f5.bigip import ManagementRoot

# ----------------------------------------------------------

session = ManagementRoot("F5_mgmt_IP","username","password",token=True)

# CAPTURE CLIENT SSL PROFILE LIST
client_ssls = session.tm.ltm.profile.client_ssls.get_collection()
# https:// <F5_mgmt_IP>/mgmt/tm/ltm/profile/client-ssl
listClientSsl = []
for client_ssl in client_ssls:
	listClientSsl.append(client_ssl.name)

# CAPTURE SERVER SSL PROFILE LIST
server_ssls = session.tm.ltm.profile.server_ssls.get_collection()
# https:// <F5_mgmt_IP>/mgmt/tm/ltm/profile/server-ssl
listServerSsl = []
for server_ssl in server_ssls:
	listServerSsl.append(server_ssl.name)

# CAPTURE VIRTUAL SERVER INFORMATION
virtual = session.tm.ltm.virtuals.virtual.load(name='testVS', partition='Common')
# https:// <F5_mgmt_IP>/mgmt/tm/ltm/virtual/~Common~testVS

print("------------")
print("Partition: {}".format(virtual.partition))
if hasattr(virtual, 'subPath'):
	print("SubPath: {}".format(virtual.subPath))
else:
	print("SubPath: None")
print("Virtual: {}".format(virtual.name))
if hasattr(virtual, 'description'):
	print("Description: {}".format(virtual.description))
else:
	print("Description: None")
print("Destination: {}".format(re.search('[^\/]+$', virtual.destination).group(0)))
listClientSsl_inUse = []
listServerSsl_inUse = []
for profile in virtual.profiles_s.get_collection():
	# https:// <F5_mgmt_IP>/mgmt/tm/ltm/virtual/<virtual_name>/profiles
	if profile.name in listClientSsl:
		listClientSsl_inUse.append(profile.name)
	if profile.name in listServerSsl:
		listServerSsl_inUse.append(profile.name)
if listClientSsl_inUse:
	for prof in listClientSsl_inUse:
		print("Client SSL: {}".format(prof))
else:
	print("Client SSL: None")
if listServerSsl_inUse:
	for prof in listServerSsl_inUse:
		print("Server SSL: {}".format(prof))
else:
	print("Server SSL: None")
if hasattr(virtual, 'rules'):
	for rule in virtual.rules:
		print("Rule: {}".format(re.search('[^\/]+$', rule).group(0)))
else:
	print("Rule: None")
if hasattr(virtual, 'persist'):
	for persist in virtual.persist:
		print("Persistence: {}".format(persist['name']))
else:
	print("Persistence: None")
if hasattr(virtual, 'pool'):
	print("Pool: {}".format(re.search('[^\/]+$', virtual.pool).group(0)))
	if hasattr(virtual, 'subPath'):
		poolName = virtual.pool.split("/")[3]
		poolSubpath = virtual.pool.split("/")[2]
		poolPartition = virtual.pool.split("/")[1]
		pool = session.tm.ltm.pools.pool.load(name=poolName, subPath=poolSubpath, partition=poolPartition)
		# https:// <F5_mgmt_IP>/mgmt/tm/ltm/pool/<pool_name>
	else:
		poolName = virtual.pool.split("/")[2]
		poolPartition = virtual.pool.split("/")[1]
		pool = session.tm.ltm.pools.pool.load(name=poolName, partition=poolPartition)
		# https:// <F5_mgmt_IP>/mgmt/tm/ltm/pool/<pool_name>
	poolMembers = pool.members_s.get_collection()
	# https:// <F5_mgmt_IP>/mgmt/tm/ltm/pool/<pool_name>/members
	if poolMembers:
		for member in poolMembers:
			print("Member: {}".format(member.name))
	else:
		print("Member: None")
else:
	print("Pool: None")
	print("Member: None")
print("------------")

# ----------------------------------------------------------
