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

import sys

class FileWriter(object):
	def __init__(self, filename, mode = "w"):
		assert(isinstance(filename, str))
		assert(mode in [ "w", "wb" ])
		self._filename = filename
		self._mode = mode
		self._f = None

	def __enter__(self):
		assert(self._f is None)
		if self._filename != "-":
			self._f = open(self._filename, self._mode)
		else:
			if self._mode == "w":
				self._f = sys.stdout
			else:
				self._f = sys.stdout.buffer
		return self._f

	def __exit__(self, *args):
		if self._filename != "-":
			self._f.close()
		else:
			self._f.flush()
