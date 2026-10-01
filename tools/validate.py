"""Structural checks by default; optional validation against locally extracted X4 schemas."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from build import ROOT, generate, validate_config


def validate(schema_root=None):
    c = json.loads((ROOT / 'config/argon-prime.json').read_text())
    validate_config(c)
    xml = ROOT / 'extension/md/ODE_ArgonPrime.xml'
    if xml.read_text() != generate(c):
        raise ValueError('Generated MD is stale; run python tools/build.py')
    for p in (ROOT / 'extension').rglob('*.xml'):
        ET.parse(p)
    md = ET.parse(xml).getroot()
    names = [n.get('name') for n in md.findall('.//cue') + md.findall('.//library')]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate cue/library names')
    for n in md.findall('.//include_actions'):
        if n.get('ref') not in names:
            raise ValueError('Unresolved action library')
    for offer in md.findall('.//create_trade_offer'):
        if any(offer.get(k) != 'false' for k in ('virtual', 'virtualmoney', 'playeronly')):
            raise ValueError('Offers must use real cargo, real payments and allow NPC trading')
    if schema_root:
        from lxml import etree
        schema_path = Path(schema_root) / 'md/md.xsd'
        schema = etree.XMLSchema(etree.parse(str(schema_path)))
        schema.assertValid(etree.parse(str(xml)))
        print('MD XSD validation passed. Runtime expression and game behaviour checks remain required.')
    else:
        print('Structural validation passed. XSD and in-game validation have NOT been run.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--schema-root', help='Extracted X4 root containing md/md.xsd and libraries/*.xsd')
    validate(parser.parse_args().schema_root)
