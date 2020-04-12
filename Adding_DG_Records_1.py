#########################################################################
# title: Adding_DG_Records_1.py                                         #
# author: Dario Garrido                                                 #
# date: 20200410                                                        #
# description: Adding DG Records (single values) into an existing DG    #
#########################################################################

from f5.bigip import ManagementRoot

# ----------------------------------------------------------

session = ManagementRoot("F5_mgmt_IP","username","password",token=True)

# >> iControlREST - ADDING NEW RECORDS INTO AN EXISTING DATAGROUP
# PUT https:// localhost/mgmt/tm/ltm/data-group/internal/<datagroup>
# Content-type: application/json
# PAYLOAD = {"records": [{"name": "1.1.1.1/32","data": ""}, {"name": "2.2.2.2/32","data": ""}]}

datagroup = session.tm.ltm.data_group.internals.internal.load(name='testDG', partition='Common')
# CREATE NEW RECORDS
newitems = ["1.1.1.1/32", "2.2.2.2/32"]
# APPEND RECORDS INTO THE EXISTING DATAGROUP
if hasattr(datagroup,'records'):
	datagroup.records = datagroup.records + newitems
else:
	datagroup.records = newitems
	print(datagroup.records)
datagroup.update()

# ----------------------------------------------------------
