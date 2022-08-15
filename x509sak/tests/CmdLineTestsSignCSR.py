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

import tempfile
from x509sak.tests import BaseTest
from x509sak.WorkDir import WorkDir
from x509sak.SubprocessExecutor import SubprocessExecutor

class CmdLineTestsSignCSR(BaseTest):
	def test_sign_pubkey(self):
		with tempfile.TemporaryDirectory() as tempdir, WorkDir(tempdir):
			# Creata a CA
			SubprocessExecutor(self._x509sak + [ "createca", "myCA" ]).run()

			# Create a default CSR
			SubprocessExecutor(self._x509sak + [ "createcsr", "client.key", "client.csr" ]).run()

			# Sign the CSR
			SubprocessExecutor(self._x509sak + [ "signcsr", "myCA", "client.csr", "client.crt" ]).run()

			# Extract public key from private key
			pubkey_in = SubprocessExecutor([ "openssl", "ec", "-pubout", "-in", "client.key" ]).run().stdout

			# Extract public key from certificate
			pubkey_out = SubprocessExecutor([ "openssl", "x509", "-noout", "-pubkey", "-in", "client.crt" ]).run().stdout

			self.assertEqual(pubkey_in, pubkey_out)

	def test_take_override_subject(self):
		with tempfile.TemporaryDirectory() as tempdir, WorkDir(tempdir):
			# Creata a CA
			SubprocessExecutor(self._x509sak + [ "createca", "myCA" ]).run()

			# Create a CSR with a specific CN/OU
			SubprocessExecutor(self._x509sak + [ "createcsr", "-s", "/CN=CSR_CN_Subject/OU=CSR_OU_Subject", "client.key", "client.csr" ]).run()

			# Sign the CSR and take original subject
			SubprocessExecutor(self._x509sak + [ "signcsr", "myCA", "client.csr", "client_original.crt" ]).run()

			# Sign the CSR and override subject
			SubprocessExecutor(self._x509sak + [ "signcsr", "-s", "/CN=Foobar", "myCA", "client.csr", "client_override.crt" ]).run()

			# Get text representation of CSR and CRT
			csr_text = SubprocessExecutor([ "openssl", "req", "-noout", "-text", "-in", "client.csr" ]).run().stdout
			crt_orig_text = SubprocessExecutor([ "openssl", "x509", "-noout", "-text", "-in", "client_original.crt" ]).run().stdout
			crt_override_text = SubprocessExecutor([ "openssl", "x509", "-noout", "-text", "-in", "client_override.crt" ]).run().stdout

			# The subject is in the CSR and the CRT without any specification,
			# but not in the CRT where it was overriden
			self.assertIn(b"CSR_CN_Subject", csr_text)
			self.assertIn(b"CSR_OU_Subject", csr_text)
			self.assertIn(b"CSR_CN_Subject", crt_orig_text)
			self.assertIn(b"CSR_OU_Subject", crt_orig_text)
			self.assertNotIn(b"CSR_CN_Subject", crt_override_text)
			self.assertNotIn(b"CSR_OU_Subject", crt_override_text)

	def test_san_included(self):
		with tempfile.TemporaryDirectory() as tempdir, WorkDir(tempdir):
			# Creata a CA
			SubprocessExecutor(self._x509sak + [ "createca", "myCA" ]).run()

			# Create a CSR
			SubprocessExecutor(self._x509sak + [ "createcsr", "client.key", "client.csr" ]).run()

			# Sign the CSR with a SAN
			SubprocessExecutor(self._x509sak + [ "signcsr", "--san-dns", "foobar.com", "--san-dns", "barfoo.com", "--san-ip", "11.22.33.44", "myCA", "client.csr", "client.crt" ]).run()

			# Check that SAN ended up in the CRT
			crt_text = SubprocessExecutor([ "openssl", "x509", "-noout", "-text", "-in", "client.crt" ]).run().stdout
			self.assertIn(b"X509v3 extensions", crt_text)
			self.assertIn(b"foobar.com", crt_text)
			self.assertIn(b"barfoo.com", crt_text)

	def test_override_extensions(self):
		with tempfile.TemporaryDirectory() as tempdir, WorkDir(tempdir):
			# Creata a CA
			SubprocessExecutor(self._x509sak + [ "createca", "myCA" ]).run()

			# Create a CSR and pack it full of extensions
			SubprocessExecutor(self._x509sak + [ "createcsr", "-t", "tls-client", "--san-dns", "fooname.com", "--san-ip", "11.22.33.44", "client.key", "client.csr" ]).run()

			# Sign the CSR but don't put any extensions in the CRT
			SubprocessExecutor(self._x509sak + [ "signcsr", "myCA", "client.csr", "client_none.crt" ]).run()

			# Sign the CSR a second time and override extensions
			SubprocessExecutor(self._x509sak + [ "signcsr", "-s", "/CN=Server", "-t", "tls-server", "myCA", "client.csr", "client_server.crt" ]).run()

			# Sign the CSR a third time and override extensions and add a SAN
			SubprocessExecutor(self._x509sak + [ "signcsr", "-s", "/CN=Server with SAN DNS", "-t", "tls-server", "--san-dns", "newdns.com", "myCA", "client.csr", "client_server_dns.crt" ]).run()

			# Get text representation of CSR and CRT
			csr_text = SubprocessExecutor([ "openssl", "req", "-noout", "-text", "-in", "client.csr" ]).run().stdout
			crt_none_text = SubprocessExecutor([ "openssl", "x509", "-noout", "-text", "-in", "client_none.crt" ]).run().stdout
			crt_server_text = SubprocessExecutor([ "openssl", "x509", "-noout", "-text", "-in", "client_server.crt" ]).run().stdout
			crt_server_dns_text = SubprocessExecutor([ "openssl", "x509", "-noout", "-text", "-in", "client_server_dns.crt" ]).run().stdout

			# CSR contains a bunch of extensions
			self.assertIn(b"Requested Extensions", csr_text)
			self.assertIn(b"fooname.com", csr_text)
			self.assertIn(b"11.22.33.44", csr_text)
			self.assertIn(b"Netscape Cert Type", csr_text)
			self.assertIn(b"Basic Constraints", csr_text)
			self.assertIn(b"SSL Client", csr_text)

			# But the CRT does not contain any
			self.assertNotIn(b"X509v3 extensions", crt_none_text)
			self.assertNotIn(b"fooname.com", crt_none_text)
			self.assertNotIn(b"11.22.33.44", crt_none_text)
			self.assertNotIn(b"Netscape Cert Type", crt_none_text)
			self.assertNotIn(b"Basic Constraints", crt_none_text)

			# The cert with template contains some, though.
			self.assertIn(b"X509v3 extensions", crt_server_text)
			self.assertNotIn(b"fooname.com", crt_server_text)
			self.assertNotIn(b"11.22.33.44", crt_server_text)
			self.assertIn(b"Netscape Cert Type", crt_server_text)
			self.assertIn(b"Basic Constraints", crt_server_text)
			self.assertIn(b"SSL Server", crt_server_text)

			# And one more, the last one also contains the specified SAN
			self.assertIn(b"X509v3 extensions", crt_server_dns_text)
			self.assertNotIn(b"fooname.com", crt_server_dns_text)
			self.assertNotIn(b"11.22.33.44", crt_server_dns_text)
			self.assertIn(b"Netscape Cert Type", crt_server_dns_text)
			self.assertIn(b"Basic Constraints", crt_server_dns_text)
			self.assertIn(b"SSL Server", crt_server_dns_text)
			self.assertIn(b"newdns.com", crt_server_dns_text)
