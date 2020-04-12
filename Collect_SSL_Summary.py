#########################################################################
# title: Collect_SSL_Summary.py                                         #
# author: Dario Garrido                                                 #
# date: 20200410                                                        #
# description: Collect info from all SSL Profiles and their usage       #
#########################################################################

from f5.bigip import ManagementRoot

# ----------------------------------------------------------

session = ManagementRoot("F5_mgmt_IP","username","password",token=True)

# CAPTURE CERTIFICATE LIST
print("******************************************")
print("************ CERTIFICATE LIST ************")
print("******************************************")
certs = session.tm.sys.file.ssl_certs.get_collection()
# https:// <F5_mgmt_IP>/mgmt/tm/ltm/virtual
for cert in certs:
	print("------------------------------------------")
	print("Cert: {}".format(cert.fullPath))
	if hasattr(cert, 'expirationString'):
		print("Expiration: {}".format(cert.expirationString))
	else:
		print("Server SSL: {}".format("None"))
print("------------------------------------------")

# CAPTURE CLIENT SSL PROFILE LIST
print("******************************************")
print("********* CLIENT SSL PROFILE LIST ********")
print("******************************************")
client_ssls = session.tm.ltm.profile.client_ssls.get_collection()
# https:// <F5_mgmt_IP>/mgmt/tm/ltm/profile/client-ssl
listClientSsl = []
for client_ssl in client_ssls:
	listClientSsl.append(client_ssl.name)
	#-----------------------------------------
	print("------------------------------------------")
	print("Client SSL: {}".format(client_ssl.fullPath))
	if hasattr(client_ssl, 'cert'):
		print("Cert: {}".format(client_ssl.cert))
	else:
		print("Cert: {}".format("None"))
	if hasattr(client_ssl, 'chain'):
		print("Chain: {}".format(client_ssl.chain))
	else:
		print("Chain: {}".format("None"))
	if hasattr(client_ssl, 'key'):
		print("Key: {}".format(client_ssl.key))
	else:
		print("Key: {}".format("None"))
	if hasattr(client_ssl, 'ciphers'):
		print("Cipher: {}".format(client_ssl.ciphers))
	else:
		print("Cipher: {}".format("None"))
	if hasattr(client_ssl, 'defaultsFrom'):
		print("Parent Profile: {}".format(client_ssl.defaultsFrom))
	else:
		print("Parent Profile: {}".format("None"))
print("------------------------------------------")

# CAPTURE SERVER SSL PROFILE LIST
print("******************************************")
print("********* SERVER SSL PROFILE LIST ********")
print("******************************************")
server_ssls = session.tm.ltm.profile.server_ssls.get_collection()
# https:// <F5_mgmt_IP>/mgmt/tm/ltm/profile/server-ssl
listServerSsl = []
for server_ssl in server_ssls:
	listServerSsl.append(server_ssl.name)
	#-----------------------------------------
	print("------------------------------------------")
	print("Server SSL: {}".format(server_ssl.fullPath))
	if hasattr(server_ssl, 'cert'):
		print("Cert: {}".format(server_ssl.cert))
	else:
		print("Cert: {}".format("None"))
	if hasattr(server_ssl, 'chain'):
		print("Chain: {}".format(server_ssl.chain))
	else:
		print("Chain: {}".format("None"))
	if hasattr(server_ssl, 'key'):
		print("Key: {}".format(server_ssl.key))
	else:
		print("Key: {}".format("None"))
	if hasattr(server_ssl, 'ciphers'):
		print("Cipher: {}".format(server_ssl.ciphers))
	else:
		print("Cipher: {}".format("None"))
	if hasattr(server_ssl, 'defaultsFrom'):
		print("Parent Profile: {}".format(server_ssl.defaultsFrom))
	else:
		print("Parent Profile: {}".format("None"))
print("------------------------------------------")

# CAPTURE VIRTUAL SERVER SSL PROFILE INFO
print("******************************************")
print("*********** VIRTUAL SERVER LIST **********")
print("******************************************")
virtuals = session.tm.ltm.virtuals.get_collection()
# https:// <F5_mgmt_IP>/mgmt/tm/ltm/virtual
for virtual in virtuals:
	print("------------------------------------------")
	print("Virtual: {}".format(virtual.fullPath))
	listClientSsl_byVS = []
	listServerSsl_byVS = []
	for profile in virtual.profiles_s.get_collection():
		# https:// <F5_mgmt_IP>/mgmt/tm/ltm/virtual/<virtual_name>/profiles
		if profile.name in listClientSsl:
			listClientSsl_byVS.append(profile.fullPath)
		if profile.name in listServerSsl:
			listServerSsl_byVS.append(profile.fullPath)
	if listClientSsl_byVS:
		for prof in listClientSsl_byVS:
			print("Client SSL: {}".format(prof))
	else:
		print("Client SSL: {}".format("None"))
	if listServerSsl_byVS:
		for prof in listServerSsl_byVS:
			print("Server SSL: {}".format(prof))
	else:
		print("Server SSL: {}".format("None"))
print("------------------------------------------")

# ----------------------------------------------------------
