#	x509sak - The X.509 Swiss Army Knife white-hat certificate toolkit
#	Copyright (C) 2020-2020 Johannes Bauer
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

from x509sak.OID import OIDDB
from x509sak.estimate.BaseEstimator import BaseEstimator
from x509sak.estimate import JudgementCode, Compatibility
from x509sak.estimate.Judgement import SecurityJudgement, SecurityJudgements, Commonness, Verdict, RFCReference

@BaseEstimator.register
class CARelationshipSecurityEstimator(BaseEstimator):
	_ALG_NAME = "ca"

	def _judge_validity_timestamps(self, certificate, ca_certificate):
		judgements = SecurityJudgements()
		if any(ts is None for ts in [ certificate.valid_not_before, certificate.valid_not_after, ca_certificate.valid_not_before, ca_certificate.valid_not_after ]):
			judgements += SecurityJudgement(JudgementCode.CA_Relationship_Validity_TimestampMalformed, "Certificate or CA certificate validity field malformed, cannot perform checking of time intervals.", verdict = Verdict.NO_SECURITY, commonness = Commonness.HIGHLY_UNUSUAL)

		if certificate.valid_not_before > ca_certificate.valid_not_after:
			judgements += SecurityJudgement(JudgementCode.CA_Relationship_Validity_NoOverlap, "Certifiate becomes valid after CA certificate has expired.", verdict = Verdict.NO_SECURITY, commonness = Commonness.HIGHLY_UNUSUAL)
		elif certificate.valid_not_after < ca_certificate.valid_not_before:
			judgements += SecurityJudgement(JudgementCode.CA_Relationship_Validity_NoOverlap, "Certifiate becomes invalid before CA certificate becomes valid.", verdict = Verdict.NO_SECURITY, commonness = Commonness.HIGHLY_UNUSUAL)
		elif ca_certificate.valid_not_before <= certificate.valid_not_before <= certificate.valid_not_after <= ca_certificate.valid_not_after:
			judgements += SecurityJudgement(JudgementCode.CA_Relationship_Validity_FullOverlap, "Certifiate validity interval falls fully into CA certificate validity.", commonness = Commonness.COMMON)
		else:
			judgements += SecurityJudgement(JudgementCode.CA_Relationship_Validity_PartialOverlap, "Certifiate validity interval falls partially into CA certificate validity. The CA certificate therefore is only useful for a portion of lifetime of the certificate under test.", commonness = Commonness.UNUSUAL)

		return judgements

	def _judge_signature(self, certificate, ca_certificate):
		judgements = SecurityJudgements()

		if not ca_certificate.is_ca_certificate:
			judgements += SecurityJudgement(JudgementCode.CA_Relationship_CACertificateInvalidAsCA, "CA certificate is not valid as a CA.", verdict = Verdict.NO_SECURITY, commonness = Commonness.HIGHLY_UNUSUAL)

		if not certificate.signed_by(ca_certificate):
			judgements += SecurityJudgement(JudgementCode.CA_Relationship_SignatureVerificationFailure, "Certificate signature is not verifiable with CA public key.", verdict = Verdict.NO_SECURITY, commonness = Commonness.HIGHLY_UNUSUAL)
		else:
			judgements += SecurityJudgement(JudgementCode.CA_Relationship_SignatureVerificationSuccess, "Certificate signature is valid.", commonness = Commonness.COMMON)

		return judgements

	def analyze(self, certificate, ca_certificate):
		judgements = SecurityJudgements()

		if certificate.issuer != ca_certificate.subject:
			standard = RFCReference(rfcno = 5280, sect = "4.1.2.4", verb = "MUST", text = "The issuer field identifies the entity that has signed and issued the certificate.")
			judgements += SecurityJudgement(JudgementCode.CA_Relationship_SubjectIssuerMismatch, "Certificate issuer does not match CA subject.", commonness = Commonness.HIGHLY_UNUSUAL, compatibility = Compatibility.STANDARDS_DEVIATION, standard = standard)
		else:
			judgements += SecurityJudgement(JudgementCode.CA_Relationship_SubjectIssuerMatch, "Certificate issuer matches CA subject.", commonness = Commonness.COMMON)

		aki = certificate.extensions.get_first(OIDDB.X509Extensions.inverse("AuthorityKeyIdentifier"))
		ski = ca_certificate.extensions.get_first(OIDDB.X509Extensions.inverse("SubjectKeyIdentifier"))

		if aki is not None:
			if aki.keyid is not None:
				if ski is None:
					standard = RFCReference(rfcno = 5280, sect = "4.2.1.2", verb = "MUST", text = "In conforming CA certificates, the value of the subject key identifier MUST be the value placed in the key identifier field of the authority key identifier extension (Section 4.2.1.1) of certificates issued by the subject of this certificate.")
					judgements += SecurityJudgement(JudgementCode.CA_Relationship_AKI_UncheckableNoCASKI, "Key ID specified in the Authority Key Identifier extension of the certificate cannot be validated because CA does not have a Subject Key Identifier extension.", commonness = Commonness.HIGHLY_UNUSUAL)
				else:
					if ski.keyid != aki.keyid:
						standard = RFCReference(rfcno = 5280, sect = "4.2.1.2", verb = "MUST", text = "In conforming CA certificates, the value of the subject key identifier MUST be the value placed in the key identifier field of the authority key identifier extension (Section 4.2.1.1) of certificates issued by the subject of this certificate.")
						judgements += SecurityJudgement(JudgementCode.CA_Relationship_AKI_KeyIDMismatch, "Key ID specified in the Authority Key Identifier extension of the certificate does not match the Key ID of the CA Subject Key Identifier extension.", commonness = Commonness.HIGHLY_UNUSUAL)
					else:
						judgements += SecurityJudgement(JudgementCode.CA_Relationship_AKI_KeyIDMatch, "Key ID specified in the Authority Key Identifier extension matches that of the CA Subject Key Identifier extension.", commonness = Commonness.COMMON)

			if aki.ca_names is not None:
				for ca_name in aki.ca_names:
					if (ca_name.name == "directoryName") and (ca_name.directory_name == ca_certificate.subject):
						break
				else:
					names = "None of the %d CA names" % (len(aki.ca_names)) if (len(aki.ca_names) != 1) else "The CA name"
					judgements += SecurityJudgement(JudgementCode.CA_Relationship_AKI_CANameMismatch, "%s specified in the Authority Key Identifier extension of the certificate does not match the CA subject.", commonness = Commonness.HIGHLY_UNUSUAL, compatibility = Compatibility.STANDARDS_DEVIATION)


			if aki.serial is not None:
				if aki.serial != ca_certificate.serial:
					if ski.keyid != aki.keyid:
						judgements += SecurityJudgement(JudgementCode.CA_Relationship_AKI_SerialMismatch, "Serial number specified in the Authority Key Identifier extension of the certificate does not match the serial number of the CA certificate.", commonness = Commonness.HIGHLY_UNUSUAL)
					else:
						judgements += SecurityJudgement(JudgementCode.CA_Relationship_AKI_SerialMatch, "Serial number specified in the Authority Key Identifier extension matches that of the CA certificate.", commonness = Commonness.COMMON)

		judgements += self._judge_validity_timestamps(certificate, ca_certificate)
		judgements += self._judge_signature(certificate, ca_certificate)

		return {
			"ca_subject":	self.algorithm("dn").analyze(ca_certificate.subject),
			"ca_issuer":	self.algorithm("dn").analyze(ca_certificate.issuer),
			"security":		judgements,
		}
