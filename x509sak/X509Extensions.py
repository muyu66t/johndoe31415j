#	x509sak - The X.509 Swiss Army Knife white-hat certificate toolkit
#	Copyright (C) 2018-2019 Johannes Bauer
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

import pyasn1.codec.der.decoder
import pyasn1.error
import pyasn1.type.univ
from pyasn1.type import tag
from pyasn1_modules import rfc2459, rfc5280
from x509sak.OID import OID, OIDDB
from x509sak import ASN1Models
from x509sak.ASN1Wrapper import ASN1NameWrapper

class X509Extensions():
	def __init__(self, extensions):
		self._exts = extensions

	def get_all(self, oid):
		assert(isinstance(oid, OID))
		return [ extension for extension in self._exts if extension.oid == oid ]

	def get_first(self, oid):
		assert(isinstance(oid, OID))
		exts = self.get_all(oid)
		if len(exts) == 0:
			return None
		else:
			return exts[0]

	def remove_all(self, oid):
		assert(isinstance(oid, OID))
		self._exts = [ extension for extension in self._exts if extension.oid != oid ]
		return self

	def filter(self, oid, replacement_extension):
		assert(isinstance(oid, OID))
		self._exts = [ extension if (extension.oid != oid) else replacement_extension for extension in self._exts ]
		return self

	def has(self, oid):
		assert(isinstance(oid, OID))
		return any(extension.oid == oid for extension in self._exts)

	def dump(self, indent = ""):
		print("%sTotal of %d X.509 extensions present:" % (indent, len(self)))
		for (eid, ext) in enumerate(self, 1):
			print("%sExtension %d: %s%s" % (indent + "    ", eid, ext.__class__.__name__, " [critical]" if ext.critical else ""))
			ext.dump(indent = indent + "        ")

	def to_asn1(self):
		extension_list = [ extension.to_asn1() for extension in self ]
		# TODO: OMG this is fugly. We cannot use Extensions(), because it's
		# tag-incompatible with the instance used inside TBSCertificate. So, I
		# guess we're doing this? No way, Jose.
		extensions_asn1 = rfc2459.Extensions().subtype(explicitTag = tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 3))
		extensions_asn1.setComponents(*extension_list)
		return extensions_asn1

	def __getitem__(self, index):
		return self._exts[index]

	def __iter__(self):
		return iter(self._exts)

	def __len__(self):
		return len(self._exts)

	def __str__(self):
		return "X509Extensions<%d>" % (len(self))

class X509ExtensionRegistry():
	_KNOWN_EXTENSIONS = { }
	_DEFAULT_CLASS = None

	@classmethod
	def set_default_class(cls, handler):
		cls._DEFAULT_HANDLER = handler

	@classmethod
	def set_handler_class(cls, handler):
		oid = handler.get_handler_oid()
		cls._KNOWN_EXTENSIONS[oid] = handler

	@classmethod
	def create(cls, oid, critical, data):
		if oid in cls._KNOWN_EXTENSIONS:
			return cls._KNOWN_EXTENSIONS[oid](oid, critical, data)
		else:
			return cls._DEFAULT_HANDLER(oid, critical, data)

class X509Extension():
	_HANDLER_OID = None
	_ASN1_MODEL = None

	def __init__(self, oid, critical, data):
		assert(isinstance(oid, OID))
		assert(isinstance(critical, bool))
		assert(isinstance(data, bytes))
		self._oid = oid
		self._critical = critical
		self._data = data
		self._asn1 = None
		self._not_decoded = data
		if self._ASN1_MODEL is not None:
			try:
				(self._asn1, self._not_decoded) = pyasn1.codec.der.decoder.decode(self.data, asn1Spec = self._ASN1_MODEL())
			except pyasn1.error.PyAsn1Error as e:
#				print("Couldn't parse ASN.1 extension: %s" % (str(e)))
				pass
		self._decode_hook()

	def to_asn1(self):
		extension = rfc2459.Extension()
		extension["extnID"] = self.oid.to_asn1()
		extension["critical"] = self.critical
		extension["extnValue"] = self.data
		return extension

	@property
	def successfully_parsed(self):
		return (self._ASN1_MODEL is not None) and (self._asn1 is not None)

	@classmethod
	def construct_from_asn1(cls, asn1, critical = False):
		data = pyasn1.codec.der.encoder.encode(asn1)
		return cls(oid = cls._HANDLER_OID, data = data, critical = critical)

	@classmethod
	def get_handler_oid(cls):
		return cls._HANDLER_OID

	@property
	def asn1_model(self):
		return self._ASN1_MODEL

	@property
	def oid(self):
		return self._oid

	@property
	def critical(self):
		return self._critical

	@property
	def data(self):
		return self._data

	@property
	def not_decoded(self):
		return self._not_decoded

	@property
	def asn1(self):
		return self._asn1

	def raw_decode(self):
		(asn1, tail) = pyasn1.codec.der.decoder.decode(self.data)
		return asn1

	def _decode_hook(self):
		pass

	@property
	def format_value(self):
		return self.data.hex()

	@property
	def known(self):
		return self.oid in OIDDB.X509Extensions

	@property
	def name(self):
		if self.known:
			name = OIDDB.X509Extensions[self.oid]
		else:
			name = str(self.oid)
		return name

	def dump(self, indent = ""):
		print("%s%s" % (indent, str(self)))

	def __repr__(self):
		return "%s<%s = %s>" % (self.__class__.__name__, self.name, self.format_value)
X509ExtensionRegistry.set_default_class(X509Extension)

class X509SubjectKeyIdentifierExtension(X509Extension):
	_HANDLER_OID = OIDDB.X509Extensions.inverse("SubjectKeyIdentifier")
	_ASN1_MODEL = rfc2459.SubjectKeyIdentifier

	@classmethod
	def construct(cls, keyid):
		assert(isinstance(keyid, bytes))
		assert(len(keyid) == 20)
		return cls.construct_from_asn1(cls._ASN1_MODEL(keyid), critical = False)

	@property
	def keyid(self):
		return self._keyid

	@property
	def format_value(self):
		return "KeyID %s" % (self.keyid.hex())

	def __eq__(self, other):
		return self.keyid == other.keyid

	def _decode_hook(self):
		self._keyid = bytes(self.asn1)
X509ExtensionRegistry.set_handler_class(X509SubjectKeyIdentifierExtension)

class X509AuthorityKeyIdentifierExtension(X509Extension):
	_HANDLER_OID = OIDDB.X509Extensions.inverse("AuthorityKeyIdentifier")
	_ASN1_MODEL = rfc2459.AuthorityKeyIdentifier

	@classmethod
	def construct(cls, keyid):
		assert(isinstance(keyid, bytes))
		assert(len(keyid) > 0)
		asn1 = cls._ASN1_MODEL()
		asn1["keyIdentifier"] = keyid
		return cls.construct_from_asn1(asn1, critical = False)

	@property
	def keyid(self):
		return self._keyid

	@property
	def ca_names(self):
		return self._ca_names

	@property
	def serial(self):
		return self._serial

	@property
	def format_value(self):
		values = [ ]
		if self.keyid is not None:
			values.append("KeyID %s" % (self.keyid.hex()))
		if self.ca_names is not None:
			values.append("CAName {%s}" % (", ".join(str(name) for name in self.ca_names)))
		if self.serial is not None:
			values.append("Serial %x" % (self.serial))
		return ", ".join(values)

	def _decode_hook(self):
		if self.asn1.getComponentByName("keyIdentifier", None, instantiate = False) is not None:
			self._keyid = bytes(self.asn1["keyIdentifier"])
		else:
			self._keyid = None
		if self.asn1.getComponentByName("authorityCertIssuer", None, instantiate = False) is not None:
			self._ca_names = [ ASN1NameWrapper.from_asn1_general_name(generalname) for generalname in self.asn1["authorityCertIssuer"] ]
		else:
			self._ca_names = None
		if self.asn1.getComponentByName("authorityCertSerialNumber", None, instantiate = False) is not None:
			self._serial = int(self.asn1["authorityCertSerialNumber"])
		else:
			self._serial = None
X509ExtensionRegistry.set_handler_class(X509AuthorityKeyIdentifierExtension)


class X509BasicConstraintsExtension(X509Extension):
	_HANDLER_OID = OIDDB.X509Extensions.inverse("BasicConstraints")
	_ASN1_MODEL = rfc2459.BasicConstraints

	@property
	def is_ca(self):
		if self.asn1 is not None:
			return bool(self.asn1["cA"])
		else:
			return False

	def __repr__(self):
		return "%s<CA = %s>" % (self.__class__.__name__, self.is_ca)
X509ExtensionRegistry.set_handler_class(X509BasicConstraintsExtension)


class X509ExtendedKeyUsageExtension(X509Extension):
	_HANDLER_OID = OIDDB.X509Extensions.inverse("ExtendedKeyUsage")
	_ASN1_MODEL = rfc2459.ExtKeyUsageSyntax

	def _decode_hook(self):
		if self.asn1 is not None:
			self._oids = set(OID.from_str(str(oid)) for oid in self.asn1)
		else:
			self._oids = set()

	@property
	def key_usage_oids(self):
		return iter(self._oids)

	@property
	def any_key_usage(self):
		return OIDDB.X509ExtendedKeyUsage.inverse("anyExtendedKeyUsage") in self._oids

	@property
	def client_auth(self):
		return OIDDB.X509ExtendedKeyUsage.inverse("id_kp_clientAuth") in self._oids

	@property
	def server_auth(self):
		return OIDDB.X509ExtendedKeyUsage.inverse("id_kp_serverAuth") in self._oids

	def __repr__(self):
		return "%s<%s>" % (self.__class__.__name__, ", ".join(OIDDB.X509ExtendedKeyUsage.get(oid, str(oid)) for oid in sorted(self._oids)))
X509ExtensionRegistry.set_handler_class(X509ExtendedKeyUsageExtension)


class X509SubjectAlternativeNameExtension(X509Extension):
	_HANDLER_OID = OIDDB.X509Extensions.inverse("SubjectAlternativeName")
	_ASN1_MODEL = rfc5280.SubjectAltName

	def _decode_hook(self):
		self._known_names = [ ]
		if self.asn1 is None:
			return
		for altname in self.asn1:
			self._known_names.append(ASN1NameWrapper.from_asn1_general_name(altname))

	@property
	def name_count(self):
		return len(self._known_names)

	def get_all(self, name_type):
		return [ asn1name for asn1name in self._known_names if asn1name.name == name_type ]

	def __iter__(self):
		return iter(self._known_names)

	def __repr__(self):
		return "%s<%s>" % (self.__class__.__name__, ", ".join(str(asn1name) for asn1name in self._known_names))
X509ExtensionRegistry.set_handler_class(X509SubjectAlternativeNameExtension)


class X509IssuerAlternativeNameExtension(X509SubjectAlternativeNameExtension):
	_HANDLER_OID = OIDDB.X509Extensions.inverse("IssuerAlternativeName")
	_ASN1_MODEL = rfc5280.IssuerAltName
X509ExtensionRegistry.set_handler_class(X509IssuerAlternativeNameExtension)


class X509KeyUsageExtension(X509Extension):
	_HANDLER_OID = OIDDB.X509Extensions.inverse("KeyUsage")
	_ASN1_MODEL = rfc5280.KeyUsage

	@property
	def flags(self):
		return self._flags

	def _decode_hook(self):
		self._flags = set()
		for (name, bit) in self._ASN1_MODEL.namedValues.items():
			if (len(self._asn1) > bit) and self._asn1[bit]:
				self._flags.add(name)

	def __repr__(self):
		return "%s<%s>" % (self.__class__.__name__, ", ".join(sorted(self._flags)))
X509ExtensionRegistry.set_handler_class(X509KeyUsageExtension)


class X509NetscapeCertificateTypeExtension(X509Extension):
	_HANDLER_OID = OIDDB.X509Extensions.inverse("NetscapeCertificateType")
	_ASN1_MODEL = ASN1Models.NetscapeCertificateType

	@property
	def ssl_server(self):
		return "server" in self.flags

	@property
	def ssl_client(self):
		return "client" in self.flags

	@property
	def flags(self):
		return self._flags

	def _decode_hook(self):
		self._flags = set()
		for (name, bit) in self._ASN1_MODEL.namedValues.items():
			if (len(self._asn1) > bit) and self._asn1[bit]:
				self._flags.add(name)

	def __repr__(self):
		return "%s<%s>" % (self.__class__.__name__, ", ".join(sorted(self._flags)))
X509ExtensionRegistry.set_handler_class(X509NetscapeCertificateTypeExtension)


class X509AuthorityInformationAccessExtension(X509Extension):
	_HANDLER_OID = OIDDB.X509Extensions.inverse("id-pe-authorityInfoAccess")
	_ASN1_MODEL = rfc5280.AuthorityInfoAccessSyntax

	@property
	def method_count(self):
		return len(self._methods)

	def _decode_hook(self):
		self._methods = [ ]
		for item in self._asn1:
			oid = OID.from_asn1(item["accessMethod"])
			location = item["accessLocation"]
			self._methods.append((oid, location))

	def __repr__(self):
		return "%s<%s>" % (self.__class__.__name__, ", ".join(str(oid) for (oid, location) in self._methods))
X509ExtensionRegistry.set_handler_class(X509AuthorityInformationAccessExtension)

class X509CertificatePoliciesExtension(X509Extension):
	_HANDLER_OID = OIDDB.X509Extensions.inverse("CertificatePolicies")
	_ASN1_MODEL = rfc5280.CertificatePolicies

	@property
	def policy_count(self):
		return len(self._policies)

	@property
	def policy_oids(self):
		return [ oid for (oid, qualifiers) in self._policies ]

	def get_qualifier_asn1(self, policy_oid):
		for (oid, qualifiers) in self._policies:
			if oid == policy_oid:
				return qualifiers

	def _decode_hook(self):
		self._policies = [ ]
		for item in self._asn1:
			oid = OID.from_asn1(item["policyIdentifier"])
			qualifiers = item["policyQualifiers"]
			self._policies.append((oid, qualifiers))

	def __repr__(self):
		return "%s<%s>" % (self.__class__.__name__, ", ".join(str(oid) for (oid, qualifiers) in self._policies))
X509ExtensionRegistry.set_handler_class(X509CertificatePoliciesExtension)
