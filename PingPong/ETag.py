import os, binascii
from stat import *

class ETag:
	def hasModified(self, filepath, etagToCompare):
		etag = binascii.unhexlify(etagToCompare[3:-1]).decode('unicode_escape').split('/')
		sizeOld = etag[0]
		mdateOld = etag[1]

		statinfo = os.stat(filepath)
		mdate = str(statinfo[ST_MTIME])
		size = str(statinfo[ST_SIZE])
		# Compare mdate
		if mdate == mdateOld and size == sizeOld:
			return False
		return True


	# Weak Validator since we are not generating an ETag based on content,
	# but attributes
	def generateETag(self, filepath):
		statinfo = os.stat(filepath)
		size = statinfo[ST_SIZE]
		mtime = statinfo[ST_MTIME]
		val = str(size) + '/' + str(mtime)
		val = val.encode('utf-8')

		# Indicate to browser weak ETag using W/"
		return 'W/"' + binascii.hexlify(val).decode('unicode_escape') + '"'
