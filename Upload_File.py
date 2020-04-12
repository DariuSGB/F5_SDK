#############################################################################################
# title: Upload_File.py                                                                     #
# author: Dario Garrido                                                                     #
# date: 20200412                                                                            #
# description: Upload files to Big-IP                                                       #
# usage: Upload_File.py [-h] [-i | -u | -g] host username password filename                 #
# https://devcentral.f5.com/s/articles/demystifying-icontrol-rest-part-5-transferring-files #
#############################################################################################

import os, requests, argparse

# ----------------------------------------------------------

# >> iControlREST - UPLOADING FILE
# POST https:// localhost/mgmt/cm/autodeploy/sotfware-image-downloads/<filename>
# Content-type: application/octet-stream
# Content-Range: <start>-<end>/<file_size>
# -----------------------------------------
# POST https:// localhost/mgmt/shared/file-transfer/ucs-downloads/<filename>
# Content-type: application/octet-stream
# Content-Range: <start>-<end>/<file_size>
# -----------------------------------------
# POST https:// localhost/mgmt/shared/file-transfer/uploads/<filename>
# Content-type: application/octet-stream
# Content-Range: <start>-<end>/<file_size>

def upload(mode, host, creds, filepath):
	# Initialize variables
	chunk_size = 512 * 1024
	start = 0
	end = 0
	size = os.path.getsize(filepath)
	current_bytes = 0
	headers = {
		'Content-Type': 'application/octet-stream'
	}
	print(filepath)
	filename = os.path.basename(filepath)
	requests.packages.urllib3.disable_warnings()
	# Select uploading mode
	extension = os.path.splitext(filename)[-1]
	select_uri = {
		0: '/mgmt/cm/autodeploy/sotfware-image-uploads/',
		1: '/mgmt/shared/file-transfer/ucs-uploads/',
		2: '/mgmt/shared/file-transfer/uploads/'
	}
	if extension == '.iso':
		uri = 'https://%s/mgmt/cm/autodeploy/software-image-uploads/%s' % (host, filename)
	elif extension == '.ucs':
		uri = 'https://%s/mgmt/shared/file-transfer/uploads/%s' % (host, filename)
	elif extension == '.md5':
		uri = 'https://%s/mgmt/shared/file-transfer/uploads/%s' % (host, filename)
	else:
		uri = 'https://{}'.format(host) + select_uri[mode] + filename
	# Create file buffer
	fileobj = open(filepath, 'rb')
	while True:
		# Slice source file
		file_slice = fileobj.read(chunk_size)
		if not file_slice:
			break
		# Check file boundaries
		current_bytes = len(file_slice)
		if current_bytes < chunk_size:
			end = size
		else:
			end = start + current_bytes
		# Set new content range header
		content_range = "%s-%s/%s" % (start, end - 1, size)
		headers['Content-Range'] = content_range
		# Lauch REST request
		requests.post(uri, auth=creds, data=file_slice, headers=headers, verify=False, timeout=10)
		# Shift to next slice
		start += current_bytes

# ----------------------------------------------------------

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Upload File from BIG-IP')
	parser.add_argument("host", help='BIG-IP IP or Hostname')
	parser.add_argument("username", help='BIG-IP Username')
	parser.add_argument("password", help='BIG-IP Password')
	parser.add_argument("filename", help='Source filename to upload')
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-i', '--image', action='store_true', help='Select to upload a SW Image/MD5 file -- /shared/images/')
	group.add_argument('-u', '--ucs', action='store_true', help='Select to upload a UCS file -- /var/local/ucs/')
	group.add_argument('-g', '--general', action='store_true', help='Select to upload other type of file -- /var/config/rest/downloads/ (default)' )
	args = vars(parser.parse_args())
	if args['image']: mode = 0
	elif args['ucs']: mode = 1
	else: mode = 2
	hostname = args['host']
	username = args['username']
	password = args['password']
	file = args['filename']
	upload(mode, hostname, (username, password), file)

# ----------------------------------------------------------
