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

import pprint
from x509sak.BaseAction import BaseAction
from x509sak import X509Certificate
from x509sak.Exceptions import InvalidInputException
from x509sak.Tools import JSONTools
from x509sak.SecurityEstimator import AnalysisOptions

class ActionExamineCert(BaseAction):
	def __init__(self, cmdname, args):
		BaseAction.__init__(self, cmdname, args)

		crts = X509Certificate.read_pemfile(args.crt_filename)
		if len(crts) == 0:
			raise InvalidInputException("No certificates found inside %s." % (args.crt_filename))

		analyses = [ ]
		for (crtno, crt) in enumerate(crts, 1):
			if len(crts) > 1:
				print("Certificate #%d:" % (crtno))
			analysis_options = AnalysisOptions(rsa_testing = AnalysisOptions.RSATesting.Fast if self._args.fast_rsa else AnalysisOptions.RSATesting.Full, include_raw_data = self._args.include_raw_data)
			analysis = self._analyze_crt(crt, analysis_options = analysis_options)
			analyses.append(analysis)

		if self._args.write_json:
			JSONTools.write_to_file(analyses, self._args.write_json)

	def _analyze_crt(self, crt, analysis_options = None):
		analysis = crt.analyze(analysis_options = analysis_options)
		print("Subject   : %s" % (analysis["subject"]["pretty"]))
		print("Issuer    : %s" % (analysis["issuer"]["pretty"]))
		print("Public key: %s" % (analysis["pubkey"]["pretty"]))
		return analysis
#		print(crt.signature_algorithm)
#		print(crt.extensions)
#		print(crt)
