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

import math
import pyasn1
from x509sak.ModulusDB import ModulusDB
from x509sak.NumberTheory import NumberTheory
from x509sak.estimate.BaseEstimator import BaseEstimator
from x509sak.estimate import JudgementCode, AnalysisOptions, Verdict, Commonness, Compatibility
from x509sak.estimate.Judgement import SecurityJudgement, SecurityJudgements, RFCReference
from x509sak.Exceptions import LazyDeveloperException

@BaseEstimator.register
class DSASecurityEstimator(BaseEstimator):
	_ALG_NAME = "dsa"

	"""DSA Parameters:
	p: Prime modulus of bitlength L
	q: Prime divisor of (p - 1) of bitlength N
	g: Generator of order q in GF(p); 1 < g < p
	y: pubkey, y = g^x mod p; x is the private key
	"""

	_TYPICAL_L_N_VALUES = {
		1024:	(160, ),
		2048:	(224, 256),
		3072:	(256, )
	}

	def analyze(self, pubkey):
		judgements = SecurityJudgements()

		L = pubkey.p.bit_length()
		N = pubkey.q.bit_length()

		if not NumberTheory.is_probable_prime(pubkey.p):
			standard = LiteratureReference(quote = "p: a prime modulus", sect = "4.1", author = "National Institute of Standards and Technology", title = "FIPS PUB 186-4: Digital Signature Standard (DSS)", year = 2013, month = 7, doi = "10.6028/NIST.FIPS.186-4")
			judgements += SecurityJudgement(JudgementCode.DSA_Parameter_P_Not_Prime, "DSA parameter p is not prime.", commonness = Commonness.HIGHLY_UNUSUAL, compatibility = Compatibility.STANDARDS_DEVIATION, bits = 0, standard = standard)

		if not NumberTheory.is_probable_prime(pubkey.q):
			standard = LiteratureReference(quote = "q: a prime divisor of (p - 1)", sect = "4.1", author = "National Institute of Standards and Technology", title = "FIPS PUB 186-4: Digital Signature Standard (DSS)", year = 2013, month = 7, doi = "10.6028/NIST.FIPS.186-4")
			judgements += SecurityJudgement(JudgementCode.DSA_Parameter_Q_Not_Prime, "DSA parameter q is not prime.", commonness = Commonness.HIGHLY_UNUSUAL, compatibility = Compatibility.STANDARDS_DEVIATION, bits = 0, standard = standard)

		if ((pubkey.p - 1) % pubkey.q) != 0:
			standard = LiteratureReference(quote = "q: a prime divisor of (p - 1)", sect = "4.1", author = "National Institute of Standards and Technology", title = "FIPS PUB 186-4: Digital Signature Standard (DSS)", year = 2013, month = 7, doi = "10.6028/NIST.FIPS.186-4")
			judgements += SecurityJudgement(JudgementCode.DSA_Parameter_Q_No_Divisor_Of_P1, "DSA parameter q is not a divisor of (p - 1).", commonness = Commonness.HIGHLY_UNUSUAL, compatibility = Compatibility.STANDARDS_DEVIATION, bits = 0, standard = standard)

		if pow(pubkey.g, pubkey.q, pubkey.p) != 1:
			judgements += SecurityJudgement(JudgementCode.DSA_Parameter_G_Unverifiable, "DSA parameter g is not verifyable. That means g^q mod p != 1.", commonness = Commonness.HIGHLY_UNUSUAL)

		if (pubkey.g <= 1) or (pubkey.g >= pubkey.p):
			standard = LiteratureReference(quote = "g: a generator of a subgroup of order q in the multiplicative group of GF(p), such that 1 < g < p", sect = "4.1", author = "National Institute of Standards and Technology", title = "FIPS PUB 186-4: Digital Signature Standard (DSS)", year = 2013, month = 7, doi = "10.6028/NIST.FIPS.186-4")
			judgements += SecurityJudgement(JudgementCode.DSA_Parameter_G_Invalid_Range, "DSA parameter g is not inside the valid range (1 < g < p).", commonness = Commonness.HIGHLY_UNUSUAL, compatibility = Compatibility.STANDARDS_DEVIATION, bits = 0, standard = standard)

		L_strength_bits = NumberTheory.asymtotic_complexity_gnfs_bits(pubkey.p)
		N_strength_bits = math.floor(N / 2)
		bits_security = min(L_strength_bits, N_strength_bits)
		judgements += self.algorithm("bits").analyze(JudgementCode.DSA_Security_Level, bits_security)

		result = {
			"cryptosystem":	"dsa",
			"specific": {
				"L":	L,
				"N":	N,
			},
			"security": judgements,
		}

		if self._analysis_options.include_raw_data:
			result["specific"]["p"]["value"] = pubkey.p
			result["specific"]["q"]["value"] = pubkey.q
			result["specific"]["g"]["value"] = pubkey.g
			result["specific"]["pubkey"]["value"] = pubkey.pubkey
		return result
