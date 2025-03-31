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

from x509sak.Tools import JSONTools
from x509sak.estimate.JudgementStructure import JudgementStructure

def create_judgement_code_class():
	structure_data = { }
	for structure_json_name in [ "number_theoretic.json", "encoding.json", "cryptography.json", "x509cert.json" ]:
		partial_data = JSONTools.load_internal("x509sak.data.judgements", structure_json_name)
		structure_data.update(partial_data)
	structure = JudgementStructure(structure_data)
	return structure.create_enum_class()

ExperimentalJudgementCodes = create_judgement_code_class()
