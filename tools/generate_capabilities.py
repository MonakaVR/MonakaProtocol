"""Generate canonical vocabulary in both languages; --check detects drift."""
import argparse,json,pathlib
R=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
tokens=json.loads((R/'schema/capabilities.json').read_text())['tokens']
def name(t):return ''.join(x.title() for x in t.split('_'))
cpp='#pragma once\n#include <array>\n#include <string_view>\nnamespace monaka::input {\nenum class Capability { '+', '.join(map(name,tokens))+' };\ninline constexpr std::array<std::string_view,7> CapabilityTokens{'+','.join('"'+t+'"' for t in tokens)+'};\n}\n'
kt='package dev.monaka.input\n\n/** Generated from schema/capabilities.json. */\nenum class Capability(val token: String) {\n'+',\n'.join('    '+t.upper()+'("'+t+'")' for t in tokens)+';\n    companion object { fun parse(token: String): Capability = entries.firstOrNull { it.token == token } ?: throw ContractError("UnsupportedValue") }\n}\n'
for path,data in [('cpp/include/monaka/input/vocabulary.hpp',cpp),('jvm/src/main/kotlin/dev/monaka/input/Capability.kt',kt)]:
 out=R/path
 if a.check:assert out.read_text(encoding='utf-8')==data,path
 else:out.parent.mkdir(parents=True,exist_ok=True);out.write_text(data,encoding='utf-8',newline='\n')
schema=json.loads((R/'schema/v2/tracker-observation.schema.json').read_text())
assert schema['$defs']['Capability']['enum']==tokens,'Frozen wire vocabulary divergence'
print('PASS canonical vocabulary / frozen schema / native-JVM generated drift')
