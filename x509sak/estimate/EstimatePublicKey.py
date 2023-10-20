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

from x509sak.AlgorithmDB import Cryptosystems
from x509sak.estimate.BaseEstimator import BaseEstimator
from x509sak.Exceptions import LazyDeveloperException
from x509sak.CurveDB import CurveNotFoundException
from x509sak.estimate.Judgement import SecurityJudgement, SecurityJudgements, JudgementCode, Compatibility, Commonness

@BaseEstimator.register
class PublicKeyEstimator(BaseEstimator):
	_ALG_NAME = "pubkey"

	def _error_curve_not_found(self, certificate, exception):
		judgements = SecurityJudgements()
		judgements += SecurityJudgement(JudgementCode.ECC_Curve_Unknown, "Certificate public key relies on unknown elliptic curve: %s Conservatively estimating broken security." % (str(exception)), bits = 0, compatibility = Compatibility.LIMITED_SUPPORT, commonness = Commonness.HIGHLY_UNUSUAL)
		result = {
			"pubkey_alg":	None,
			"pretty":		"Unrecognized elliptic curve: %s" % (str(exception)),
			"security":		judgements,
		}

		return result

	def analyze(self, certificate):
		try:
			pubkey = certificate.pubkey
		except CurveNotFoundException as e:
			return self._error_curve_not_found(certificate, e)

		result = {
			"pubkey_alg":	pubkey.pk_alg.value.name,
		}
		if pubkey.pk_alg.value.cryptosystem == Cryptosystems.RSA:
			result["pretty"] = "RSA with %d bit modulus" % (pubkey.n.bit_length())
			result.update(self.algorithm("rsa").analyze(pubkey))
		elif pubkey.pk_alg.value.cryptosystem == Cryptosystems.ECC_ECDSA:
			result["pretty"] = "ECC on %s" % (pubkey.curve.name)
			result.update(self.algorithm("ecc").analyze(pubkey))
		elif pubkey.pk_alg.value.cryptosystem == Cryptosystems.ECC_EdDSA:
			result["pretty"] = "EdDSA on %s" % (pubkey.curve.name)
			result.update(self.algorithm("ecc").analyze(pubkey))
		else:
			raise LazyDeveloperException(NotImplemented, pubkey.pk_alg.value.cryptosystem)
		return result
