#############################################################################################
# title: Download_File.py                                                                   #
# author: Dario Garrido                                                                     #
# date: 20200412                                                                            #
# description: Download files from Big-IP                                                   #
# usage: Download_File.py [-h] [-i | -u] host username password filename                    #
# https://devcentral.f5.com/s/articles/demystifying-icontrol-rest-part-5-transferring-files #
#############################################################################################

import os, requests, argparse

# ----------------------------------------------------------

# >> iControlREST - DOWNLOADING FILE
# GET https:// localhost/mgmt/cm/autodeploy/sotfware-image-downloads/<filename>
# Content-type: application/octet-stream
# Content-Range: <start>-<end>/<file_size>
# -----------------------------------------
# GET https:// localhost/mgmt/shared/file-transfer/ucs-downloads/<filename>
# Content-type: application/octet-stream
# Content-Range: <start>-<end>/<file_size>

def download(mode, host, creds, filepath):
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
	requests.packages.urllib3.disable_warnings()
	# Select downloading mode
	select_uri = {
		0: '/mgmt/cm/autodeploy/sotfware-image-downloads/',
		1: '/mgmt/shared/file-transfer/ucs-downloads/'
	}
	uri = 'https://{}'.format(host) + select_uri[mode] + filename
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
				print("Connection Timeout")
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
						break
			else:
				# Response status 400 (Bad Request)
				print("Bad Request. Maybe the file doesn't exist.")
				break
			crange = response.headers['Content-Range']
			# Determine the total number of bytes to read
			if size == -1:
				size = int(crange.split('/')[-1])
				# Stops if the file is empty
				if size == 0:
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

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Download File from BIG-IP')
	parser.add_argument("host", help='BIG-IP IP or Hostname')
	parser.add_argument("username", help='BIG-IP Username')
	parser.add_argument("password", help='BIG-IP Password')
	parser.add_argument("filename", help='Source filename to download')
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-i', '--image', action='store_true', help='Select to download a SW Image file -- /shared/images/ (default)')
	group.add_argument('-u', '--ucs', action='store_true', help='Select to download a UCS file -- /var/local/ucs/')
	args = vars(parser.parse_args())
	if args['ucs']: mode = 1
	else: mode = 0
	hostname = args['host']
	username = args['username']
	password = args['password']
	filename = args['filename']
	download(mode, hostname, (username, password), filename)

# ----------------------------------------------------------
