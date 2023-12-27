#!/usr/bin/python3
#	x509sak - The X.509 Swiss Army Knife white-hat certificate toolkit
#	Copyright (C) 2018-2018 Johannes Bauer
#
#	This file is part of x509sak.
#
#	x509sak is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	x509sak is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with x509sak; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import subprocess
import os
import threading
import hashlib
import tempfile

def get_processor_count():
	with open("/proc/cpuinfo") as f:
		return len(list(line for line in f.read().split("\n") if line.startswith("processor")))

corpus_directory = "../../x509-cert-testcorpus/certs/"
output_directory = "examine"
thread_cnt = get_processor_count()
threads = threading.Semaphore(thread_cnt)

def execute(certno, domain, infile, outfile):
	try:
		os.makedirs(os.path.dirname(outfile))
	except FileExistsError:
		pass

	cmd = [ "../x509sak.py", "examine", "-p", "tls-server", "--server-name=%s" % (domain), "-f", "json", "-o", outfile, "-i", "dercrt", infile ]
	print("%6d %s" % (certno, " ".join(cmd)))
	try:
		subprocess.check_call(cmd)
	except subprocess.CalledProcessError:
		with open("failed_certificate.txt", "a") as f:
			print(infile, file = f)
	threads.release()

certno = 0
for (dirname, subdirs, files) in os.walk(corpus_directory):
	for filename in files:
		fullfilename = dirname + "/" + filename
		domain = filename[:-4]
		key = hashlib.md5(domain.encode()).hexdigest()[:3]
		outfile = "%s/%s/%s.json" % (output_directory, key, domain)
		if os.path.isfile(outfile):
			continue

		certno += 1
		threads.acquire()
		thread = threading.Thread(target = execute, args = (certno, domain, fullfilename, outfile))
		thread.start()

for i in range(thread_cnt):
	threads.acquire()
