#	x509sak - The X.509 Swiss Army Knife white-hat certificate toolkit
#	Copyright (C) 2018-2020 Johannes Bauer
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

import urllib.parse
from x509sak.estimate.Judgement import Commonness
from x509sak.ASN1Wrapper import ASN1GeneralNameWrapper
from x509sak.Tools import ValidationTools
from x509sak.estimate.Validator import BaseValidator, BaseValidationResult

#		"empty_value":					GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_SAN_EmptyValue),
#		"email":						GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_SAN_Name_Email_Malformed, standard = RFCReference(rfcno = 822, sect = "6.1", verb = "MUST", text = "addr-spec = local-part \"@\" domain")),
#		"ip":							GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_SAN_Name_IPAddress_Malformed, standard = RFCReference(rfcno = 5280, sect = "4.2.1.6", verb = "MUST", text = "For IP version 4, as specified in [RFC791], the octet string MUST contain exactly four octets. For IP version 6, as specified in [RFC2460], the octet string MUST contain exactly sixteen octets.")),
#		"ip_private":					GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_SAN_Name_IPAddress_PrivateAddressSpace),
#		"uri":							GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_SAN_Name_URI_Malformed, standard = RFCReference(rfcno = 5280, sect = "4.2.1.6", verb = "MUST", text = "The name MUST NOT be a relative URI, and it MUST follow the URI syntax and encoding rules specified in [RFC3986]. The name MUST include both a scheme (e.g., \"http\" or \"ftp\") and a scheme-specific-part. URIs that include an authority ([RFC3986], Section 3.2) MUST include a fully qualified domain name or IP address as the host.")),
#		"uri_invalid_scheme":			GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_SAN_Name_URI_UncommonURIScheme),
#		"dnsname":						GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_SAN_Name_DNS_Malformed, standard = RFCReference(rfcno = 1034, sect = "3.5", verb = "MUST", text = "The following syntax will result in fewer problems with many applications that use domain names (e.g., mail, TELNET).")),
#		"dnsname_space":				GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_SAN_Name_DNS_OnlyWhitespace, standard = RFCReference(rfcno = 5280, sect = "4.2.1.6", verb = "MUST", text = "In addition, while the string \" \" is a legal domain name, subjectAltName extensions with a dNSName of \" \" MUST NOT be used.")),
#		"dnsname_single_label":			GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_SAN_Name_DNS_SingleLabel),
#		"dnsname_wc_notleftmost":		GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_SAN_Name_DNS_Wildcard_NotLeftmost, standard = RFCReference(rfcno = 6125, sect = "6.4.3", verb = "SHOULD", text = "The client SHOULD NOT attempt to match a presented identifier in which the wildcard character comprises a label other than the left-most label")),
#		"dnsname_wc_morethanone":		GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_SAN_Name_DNS_Wildcard_MulitpleWildcards, standard = RFCReference(rfcno = 6125, sect = "6.4.3", verb = "SHOULD", text = "If the wildcard character is the only character of the left-most label in the presented identifier, the client SHOULD NOT compare against anything but the left-most label of the reference identifier")),
#		"dnsname_wc_international":		GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_SAN_Name_DNS_Wildcard_InternationalLabel, standard = RFCReference(rfcno = 6125, sect = "6.4.3", verb = "SHOULD", text = "However, the client SHOULD NOT attempt to match a presented identifier where the wildcard character is embedded within an A-label or U-label [IDNA-DEFS] of an internationalized domain name [IDNA-PROTO].")),
#		"dnsname_wc_broad":				GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_SAN_Name_DNS_Wildcard_BroadMatch),
#		"invalid_type":					GeneralNameValidator.Error(code = JudgementCode.Cert_X509Ext_SubjectAltName_UncommonIdentifier),
#		"empty_value":					GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_IAN_EmptyValue),
#		"email":						GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_IAN_Name_Email_Malformed, standard = RFCReference(rfcno = 822, sect = "6.1", verb = "MUST", text = "addr-spec = local-part \"@\" domain")),
#		"ip":							GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_IAN_Name_IPAddress_Malformed, standard = RFCReference(rfcno = 5280, sect = "4.2.1.6", verb = "MUST", text = "For IP version 4, as specified in [RFC791], the octet string MUST contain exactly four octets. For IP version 6, as specified in [RFC2460], the octet string MUST contain exactly sixteen octets.")),
#		"ip_private":					GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_IAN_Name_IPAddress_PrivateAddressSpace),
#		"uri":							GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_IAN_Name_URI_Malformed, standard = RFCReference(rfcno = 5280, sect = "4.2.1.6", verb = "MUST", text = "The name MUST NOT be a relative URI, and it MUST follow the URI syntax and encoding rules specified in [RFC3986]. The name MUST include both a scheme (e.g., \"http\" or \"ftp\") and a scheme-specific-part. URIs that include an authority ([RFC3986], Section 3.2) MUST include a fully qualified domain name or IP address as the host.")),
#		"uri_invalid_scheme":			GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_IAN_Name_URI_UncommonURIScheme),
#		"dnsname":						GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_IAN_Name_DNS_Malformed, standard = RFCReference(rfcno = 1034, sect = "3.5", verb = "MUST", text = "The following syntax will result in fewer problems with many applications that use domain names (e.g., mail, TELNET).")),
#		"dnsname_space":				GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_IAN_Name_DNS_OnlyWhitespace, standard = RFCReference(rfcno = 5280, sect = "4.2.1.6", verb = "MUST", text = "In addition, while the string \" \" is a legal domain name, subjectAltName extensions with a dNSName of \" \" MUST NOT be used.")),
#		"dnsname_single_label":			GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_IAN_Name_DNS_SingleLabel),
#		"invalid_type":					GeneralNameValidator.Error(code = JudgementCode.Cert_X509Ext_IssuerAltName_UncommonIdentifier),
#		"empty_value":					GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_AKI_CAName_EmptyValue),
#		"email":						GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_AKI_CAName_Email_Malformed, standard = RFCReference(rfcno = 822, sect = "6.1", verb = "MUST", text = "addr-spec = local-part \"@\" domain")),
#		"ip":							GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_AKI_CAName_IPAddress_Malformed, standard = RFCReference(rfcno = 5280, sect = "4.2.1.6", verb = "MUST", text = "For IP version 4, as specified in [RFC791], the octet string MUST contain exactly four octets. For IP version 6, as specified in [RFC2460], the octet string MUST contain exactly sixteen octets.")),
#		"ip_private":					GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_AKI_CAName_IPAddress_PrivateAddressSpace),
#		"uri":							GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_AKI_CAName_URI_Malformed, standard = RFCReference(rfcno = 5280, sect = "4.2.1.6", verb = "MUST", text = "The name MUST NOT be a relative URI, and it MUST follow the URI syntax and encoding rules specified in [RFC3986]. The name MUST include both a scheme (e.g., \"http\" or \"ftp\") and a scheme-specific-part. URIs that include an authority ([RFC3986], Section 3.2) MUST include a fully qualified domain name or IP address as the host.")),
#		"uri_invalid_scheme":			GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_AKI_CAName_URI_UncommonURIScheme),
#		"dnsname":						GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_AKI_CAName_DNS_Malformed, standard = RFCReference(rfcno = 1034, sect = "3.5", verb = "MUST", text = "The following syntax will result in fewer problems with many applications that use domain names (e.g., mail, TELNET).")),
#		"dnsname_space":				GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_AKI_CAName_DNS_OnlyWhitespace, standard = RFCReference(rfcno = 5280, sect = "4.2.1.6", verb = "MUST", text = "In addition, while the string \" \" is a legal domain name, subjectAltName extensions with a dNSName of \" \" MUST NOT be used.")),
#		"dnsname_single_label":			GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_AKI_CAName_DNS_SingleLabel),
#		"invalid_type":					GeneralNameValidator.Error(code = JudgementCode.Cert_X509Ext_AuthorityKeyIdentifier_CAName_UncommonIdentifier),
#		"empty_value":					GeneralNameValidator.Error(code = JudgementCode.Cert_X509Ext_CRLDistributionPoints_PointName_EmptyValue),
#		"email":						GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_CRLDP_PointName_Email_Malformed, standard = RFCReference(rfcno = 822, sect = "6.1", verb = "MUST", text = "addr-spec = local-part \"@\" domain")),
#		"ip":							GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_CRLDP_PointName_IPAddress_Malformed, standard = RFCReference(rfcno = 5280, sect = "4.2.1.6", verb = "MUST", text = "For IP version 4, as specified in [RFC791], the octet string MUST contain exactly four octets. For IP version 6, as specified in [RFC2460], the octet string MUST contain exactly sixteen octets.")),
#		"ip_private":					GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_CRLDP_PointName_IPAddress_PrivateAddressSpace),
#		"uri":							GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_CRLDP_PointName_URI_Malformed, standard = RFCReference(rfcno = 5280, sect = "4.2.1.6", verb = "MUST", text = "The name MUST NOT be a relative URI, and it MUST follow the URI syntax and encoding rules specified in [RFC3986]. The name MUST include both a scheme (e.g., \"http\" or \"ftp\") and a scheme-specific-part. URIs that include an authority ([RFC3986], Section 3.2) MUST include a fully qualified domain name or IP address as the host.")),
#		"uri_invalid_scheme":			GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_CRLDP_PointName_URI_UncommonURIScheme),
#		"dnsname":						GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_CRLDP_PointName_DNS_Malformed, standard = RFCReference(rfcno = 1034, sect = "3.5", verb = "MUST", text = "The following syntax will result in fewer problems with many applications that use domain names (e.g., mail, TELNET).")),
#		"dnsname_space":				GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_CRLDP_PointName_DNS_OnlyWhitespace, standard = RFCReference(rfcno = 5280, sect = "4.2.1.6", verb = "MUST", text = "In addition, while the string \" \" is a legal domain name, subjectAltName extensions with a dNSName of \" \" MUST NOT be used.")),
#		"dnsname_single_label":			GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_CRLDP_PointName_DNS_SingleLabel),
#		"invalid_type":					GeneralNameValidator.Error(code = JudgementCode.Cert_X509Ext_CRLDistributionPoints_PointName_UncommonIdentifier),
#		"empty_value":					GeneralNameValidator.Error(code = JudgementCode.Cert_X509Ext_CRLDistributionPoints_CRLIssuer_Name_EmptyValue),
#		"email":						GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_CRLDP_CRLIssuer_Email_Malformed, standard = RFCReference(rfcno = 822, sect = "6.1", verb = "MUST", text = "addr-spec = local-part \"@\" domain")),
#		"uri":							GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_CRLDP_CRLIssuer_URI_Malformed, standard = RFCReference(rfcno = 5280, sect = "4.2.1.6", verb = "MUST", text = "The name MUST NOT be a relative URI, and it MUST follow the URI syntax and encoding rules specified in [RFC3986]. The name MUST include both a scheme (e.g., \"http\" or \"ftp\") and a scheme-specific-part. URIs that include an authority ([RFC3986], Section 3.2) MUST include a fully qualified domain name or IP address as the host.")),
#		"uri_invalid_scheme":			GeneralNameValidator.Error(code = JudgementCode.X509Cert_Body_X509Exts_Ext_CRLDP_CRLIssuer_URI_UncommonURIScheme),
#		"invalid_type":					GeneralNameValidator.Error(code = JudgementCode.Cert_X509Ext_CRLDistributionPoints_CRLIssuer_Name_UncommonIdentifier),


class GeneralNameValidationResult(BaseValidationResult):
	def _get_message(self, issue, message):
		return "%s of type %s %s" % (self._validator.validation_subject, self._subject.name, message)

	def _validate_dNSName(self):
		self._report("Enc_DER_Struct_GenName_DNS_Unexpected", "contains unexpected domain name \"%s\"." % (self._subject.str_value))
		if self._subject.str_value == " ":
			return self._report("Enc_DER_Struct_GenName_DNS_OnlyWhitespace", "got invalid DNS name \" \" (space character).")

		if self._validator.allow_dnsname_wildcard_matches:
			(result, label) = ValidationTools.validate_domainname_template(self._subject.str_value)
			if result != ValidationTools.DomainnameTemplateValidationResult.Valid:
				if result == ValidationTools.DomainnameTemplateValidationResult.InvalidCharacter:
					return self._report("Enc_DER_Struct_GenName_DNS_Malformed", "has invalid domain name \"%s\", error at label \"%s\"." % (self._subject.str_value, label))
				elif result == ValidationTools.DomainnameTemplateValidationResult.FullWildcardNotLeftmost:
					return self._report("Enc_DER_Struct_GenName_DNS_Wildcard_NotLeftmost", "has invalid domain name \"%s\". Full-label wildcard appears not as leftmost element." % (self._subject.str_value))
				elif result == ValidationTools.DomainnameTemplateValidationResult.MoreThanOneWildcard:
					return self._report("Enc_DER_Struct_GenName_DNS_Wildcard_MulitpleWildcards", "has invalid domain name \"%s\". More than one wildcard label present." % (self._subject.str_value))
				elif result == ValidationTools.DomainnameTemplateValidationResult.WildcardInInternationalDomain:
					return self._report("Enc_DER_Struct_GenName_DNS_Wildcard_InternationalLabel", "has invalid domain name \"%s\". Wildcard in international domain label \"%s\"." % (self._subject.str_value, label))
				else:
					raise NotImplementedError(result)

			if "*" in self._subject.str_value:
				# Wildcard match
				labels = self._subject.str_value.split(".")
				if len(labels) <= 2:
					self._report("Enc_DER_Struct_GenName_DNS_Wildcard_BroadMatch", "has wildcard value \"%s\", which is an extremely broad domain match." % (self._subject.str_value), commonness = Commonness.HIGHLY_UNUSUAL)

		if not "." in self._subject.str_value:
			self._report("Enc_DER_Struct_GenName_DNS_SingleLabel", "contains only single label \"%s\", which is highly unusual." % (self._subject.str_value), commonness = Commonness.HIGHLY_UNUSUAL)

		validation_name = self._subject.str_value
		if self._validator.allow_dnsname_wildcard_matches:
			validation_name = validation_name.replace("*", "a")
		result = ValidationTools.validate_domainname(validation_name)
		if not result:
			self._report("Enc_DER_Struct_GenName_DNS_Malformed", "has invalid domain name \"%s\" (wildcard matches %s)." % (self._subject.str_value, "permitted" if self._validator.allow_dnsname_wildcard_matches else "forbidden"))

	def _validate_iPAddress(self):
		self._report("Enc_DER_Struct_GenName_IPAddress_Unexpected", "contains unexpected IP address \"%s\"." % (self._subject.str_value))
		if len(self._subject.asn1_value) not in [ 4, 16 ]:
			self._report("Enc_DER_Struct_GenName_IPAddress_Malformed", "expects either 4 or 16 bytes of data for IPv4/IPv6, but saw %d bytes." % (len(self._subject.str_value)))
		else:
			if len(self._subject.asn1_value) == 4:
				# IPv4
				ip_value = int.from_bytes(self._subject.asn1_value, byteorder = "big")
				private_networks = (
					(0x0a000000, 0xff000000, "private class A"),
					(0xac100000, 0xfff00000, "private class B"),
					(0xc0a80000, 0xffff0000, "private class C"),
					(0x64400000, 0xffc00000, "carrier-grade NAT"),
					(0xe0000000, 0xf0000000, "IP multicast"),
					(0xf0000000, 0xf0000000, "reserved"),
					(0x7f000000, 0xff000000, "loopback"),
					(0xffffffff, 0xffffffff, "limited broadcast"),
				)
				for (network, netmask, network_class) in private_networks:
					if (ip_value & netmask) == network:
						self._report("Enc_DER_Struct_GenName_IPAddress_PrivateAddressSpace", "has network address %s in a %s subnet." % (self._subject.str_value, network_class))
						break

	def _validate_rfc822Name(self):
		self._report("Enc_DER_Struct_GenName_Email_Unexpected", "contains unexpected email address \"%s\"." % (self._subject.str_value))
		if not ValidationTools.validate_email_address(self._subject.str_value):
			self._report("Enc_DER_Struct_GenName_Email_Malformed", "contains invalid email address \"%s\"." % (self._subject.str_value))

	def _validate_directoryName(self):
		self._report("Enc_DER_Struct_GenName_DirectoryAddress_Unexpected", "contains unexpected directory name \"%s\"." % (self._subject.str_value))

	def _validate_uniformResourceIdentifier(self):
		self._report("Enc_DER_Struct_GenName_URI_Unexpected", "contains unexpected URI \"%s\"." % (self._subject.str_value))
		if not ValidationTools.validate_uri(str(self._subject.str_value)):
			self._report("Enc_DER_Struct_GenName_URI_Malformed", "contains invalid URI \"%s\"." % (str(self._subject.str_value)))
		if self._validator.permissible_uri_schemes is not None:
			split_url = urllib.parse.urlsplit(self._subject.str_value)
			if split_url.scheme not in self._validator.permissible_uri_schemes:
				self._report("Enc_DER_Struct_GenName_URI_UncommonURIScheme", "contains invalid URI scheme \"%s\" (permitted schemes are only %s)." % (str(self._subject.str_value), ", ".join(sorted(self._validator.permissible_uri_schemes))))

	def _validate_registeredID(self):
		self._report("Enc_DER_Struct_GenName_RegisteredID_Unexpected", "contains unexpected registered ID \"%s\"." % (self._subject.str_value))

	def _validate(self):
		gn_subtype_handler = getattr(self, "_validate_%s" % (str(self._subject.name)), None)
		if gn_subtype_handler is not None:
			gn_subtype_handler()


class GeneralNameValidator(BaseValidator):
	_ValidationResultClass = GeneralNameValidationResult

	def __init__(self, validation_subject, recognized_issues, permissible_uri_schemes = None, allow_dnsname_wildcard_matches = None):
		BaseValidator.__init__(self, validation_subject, recognized_issues)
		self._permissible_uri_schemes = permissible_uri_schemes
		self._allow_dnsname_wildcard_matches = allow_dnsname_wildcard_matches

	@property
	def permissible_uri_schemes(self):
		return self._permissible_uri_schemes

	@property
	def allow_dnsname_wildcard_matches(self):
		return self._allow_dnsname_wildcard_matches

	def validate_asn1(self, general_name_asn1):
		general_name = ASN1GeneralNameWrapper.from_asn1(general_name_asn1)
		return self.validate(general_name)
