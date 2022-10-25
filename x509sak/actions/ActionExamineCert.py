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

from x509sak.BaseAction import BaseAction
from x509sak import X509Certificate
from x509sak.Tools import JSONTools
from x509sak.SecurityEstimator import AnalysisOptions

class ActionExamineCert(BaseAction):
	def __init__(self, cmdname, args):
		BaseAction.__init__(self, cmdname, args)

		analyses = [ ]
		for crt_filename in self._args.crt_filenames:
			self._log.debug("Reading %s", crt_filename)
			crts = X509Certificate.read_pemfile(crt_filename)
			for (crtno, crt) in enumerate(crts, 1):
				if len(crts) > 1:
					print("%s #%d:" % (crt_filename, crtno))
				else:
					print("%s:" % (crt_filename))
				analysis_options = AnalysisOptions(rsa_testing = AnalysisOptions.RSATesting.Fast if self._args.fast_rsa else AnalysisOptions.RSATesting.Full, include_raw_data = self._args.include_raw_data)
				analysis = self._analyze_crt(crt, analysis_options = analysis_options)
				analysis["source"] = {
					"filename":		crt_filename,
					"index":		crtno - 1,
				}
				analyses.append(analysis)

		if self._args.write_json:
			JSONTools.write_to_file(analyses, self._args.write_json)

	def _analyze_crt(self, crt, analysis_options = None):
		analysis = crt.analyze(analysis_options = analysis_options)
		if self._args.print_raw:
			print(JSONTools.serialize(analysis))
		else:
			print("Subject   : %s" % (analysis["subject"]["pretty"]))
			print("Issuer    : %s" % (analysis["issuer"]["pretty"]))
			print("Public key: %s" % (analysis["pubkey"]["pretty"]))
#			print("Validity  : %s to %s" % (a
			#print("Signature : %s" % (analysis["signature"]["pretty"]))
			print("   Hash function: %s" % (analysis["signature"]["hash_fnc"]["name"]))
			print("   Signature algorithm: %s" % (analysis["signature"]["sig_fnc"]["name"]))
		return analysis
#		print(crt.signature_algorithm)
#		print(crt.extensions)
#		print(crt)
