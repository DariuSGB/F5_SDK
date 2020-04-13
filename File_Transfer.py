#########################################################################
# title: File_Transfer.py                                               #
# author: Dario Garrido                                                 #
# date: 20200412                                                        #
# description: Upload files to Big-IP                                   #
# usage: File_Transfer.py [-h] [-i | -u | -g] host username filepath    #
# https://devcentral.f5.com/s/articles/BIG-IP-File-Transfers            #
#########################################################################

import os, requests, argparse, getpass

# ----------------------------------------------------------

# >> iControlREST - DOWNLOADING FILE
# GET https:// localhost/mgmt/cm/autodeploy/software-image-downloads/<filename>
# Content-type: application/octet-stream
# Content-Range: <start>-<end>/<file_size>
# -----------------------------------------
# GET https:// localhost/mgmt/shared/file-transfer/ucs-downloads/<filename>
# Content-type: application/octet-stream
# Content-Range: <start>-<end>/<file_size>

# >> iControlREST - UPLOADING FILE
# POST https:// localhost/mgmt/cm/autodeploy/software-image-downloads/<filename>
# Content-type: application/octet-stream
# Content-Range: <start>-<end>/<file_size>
# PAYLOAD = <RAW_FILE_DATA>
# -----------------------------------------
# POST https:// localhost/mgmt/shared/file-transfer/ucs-downloads/<filename>
# Content-type: application/octet-stream
# Content-Range: <start>-<end>/<file_size>
# PAYLOAD = <RAW_FILE_DATA>
# -----------------------------------------
# POST https:// localhost/mgmt/shared/file-transfer/uploads/<filename>
# Content-type: application/octet-stream
# Content-Range: <start>-<end>/<file_size>
# PAYLOAD = <RAW_FILE_DATA>

# ----------------------------------------------------------

def _download(location, host, creds, filepath):
	# Initialize variables
	chunk_size = 512 * 1024
	start = 0
	end = chunk_size - 1
	size = -1
	current_bytes = 0
	headers = {
		'Content-Type': 'application/octet-stream'
	}
	filename = os.path.basename(filepath)
	# Select downloading location
	select_uri = {
		0: '/mgmt/cm/autodeploy/software-image-downloads/',
		1: '/mgmt/shared/file-transfer/ucs-downloads/'
	}
	uri = 'https://{}'.format(host) + select_uri[location] + filename
	# Create file buffer
	with open(filepath, 'wb') as fileobj:
		while True:
			# Set new content range header
			content_range = "%s-%s/%s" % (start, end, size)
			headers['Content-Range'] = content_range
			# Lauch REST request
			try:
				response = requests.get(uri, auth=creds, headers=headers, verify=False, stream=True, timeout=10)
			except requests.exceptions.ConnectTimeout:
				print("Connection Timeout.")
				break
			# Check response status
			if response.status_code == 200:
				# If the size is zero, then this is the first time through the
				# loop and we don't want to write data because we haven't yet
				# figured out the total size of the file.
				if size > 0:
					current_bytes += chunk_size
					for chunk in response.iter_content(chunk_size):
						fileobj.write(chunk)
					# Once we've downloaded the entire file, we can break out of
					# the loop
					if end == size - 1:
						print("Successful Transfer.")
						break
			else:
				# Response status 400 (Bad Request)
				print("Bad Request(400). Check filepath, credentials, ...")
				break
			crange = response.headers['Content-Range']
			# Determine the total number of bytes to read
			if size == -1:
				size = int(crange.split('/')[-1])
				# Stops if the file is empty
				if size == 0:
					print("Successful Transfer.")
					break
				# If the file is smaller than the chunk size, BIG-IP will
				# return an HTTP 400. So adjust the chunk_size down to the
				# total file size...
				if chunk_size > size:
					end = size - 1
				# ...and pass on the rest of the code
				continue
			start += chunk_size
			# Check if you are in your last chunk
			if (current_bytes + chunk_size) > size - 1:
				end = size - 1
			else:
				end = start + chunk_size - 1

# ----------------------------------------------------------

def _upload(location, host, creds, filepath):
	# Initialize variables
	chunk_size = 512 * 1024
	start = 0
	end = 0
	size = os.path.getsize(filepath)
	current_bytes = 0
	headers = {
		'Content-Type': 'application/octet-stream'
	}
	filename = os.path.basename(filepath)
	# Select uploading location
	select_uri = {
		0: '/mgmt/cm/autodeploy/software-image-uploads/',
		1: '/mgmt/shared/file-transfer/ucs-uploads/',
		2: '/mgmt/shared/file-transfer/uploads/'
	}
	uri = 'https://{}'.format(host) + select_uri[location] + filename
	# Create file buffer
	fileobj = open(filepath, 'rb')
	while True:
		# Slice source file
		file_slice = fileobj.read(chunk_size)
		if not file_slice:
			print("Successful Transfer.")
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
		try:
			response = requests.post(uri, auth=creds, data=file_slice, headers=headers, verify=False, timeout=10)
			if response.status_code != 200:
				# Response status 400 (Bad Request)
				print("Bad Request(400). Check filepath, credentials, ...")
				break
		except requests.exceptions.ConnectTimeout:
			print("Connection Timeout.")
			break
		# Shift to next slice
		start += current_bytes

# ----------------------------------------------------------

if __name__ == "__main__":
	# Disable SSL Warnings
	requests.packages.urllib3.disable_warnings()
	# Configure parsers
	parser = argparse.ArgumentParser(description='Transfer File from/to BIG-IP')
	parser.add_argument("mode", help='Select mode \'download\' or \'upload\'')
	parser.add_argument("host", help='BIG-IP IP or Hostname')
	parser.add_argument("username", help='BIG-IP Username')
	#parser.add_argument("password", help='BIG-IP Password')
	parser.add_argument("filepath", help='filename & path')
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-i', '--image', action='store_true',
					   help='Select location as SW Image/MD5 file -- /shared/images/')
	group.add_argument('-u', '--ucs', action='store_true', help='Select location as UCS file -- /var/local/ucs/')
	group.add_argument('-g', '--general', action='store_true',
					   help='Select location as general stuff -- /var/config/rest/downloads/')
	args = vars(parser.parse_args())
	# Set variables
	mode = args['mode']
	hostname = args['host']
	username = args['username']
	print('Enter \'{}\' password: '.format(args['username']))
	password = getpass.getpass()
	#password = args['password']
	filepath = args['filepath']
	# set location parameter
	ext = os.path.splitext(filepath)[-1]
	if mode == 'download':
		if args['ucs']:
			location = 1
		elif args['image']:
			location = 0
		elif ext == '.ucs':
			location = 1
		elif ext == '.iso':
			location = 0
		elif ext == '.md5':
			location = 0
		else:
			location = 1
		if args['general']:
			print('Selector \'-g|--general\' is not valid with download mode.')
		else:
			_download(location, hostname, (username, password), filepath)
	elif mode == 'upload':
		if args['general']:
			location = 2
		elif args['ucs']:
			location = 1
		elif args['image']:
			location = 0
		elif ext == '.ucs':
			location = 1
		elif ext == '.iso':
			location = 0
		elif ext == '.md5':
			location = 0
		else:
			location = 2
		_upload(location, hostname, (username, password), filepath)
	else:
		print('Transfer mode not supported.')

# ----------------------------------------------------------
