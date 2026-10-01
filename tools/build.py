"""Compile balance data into a self-contained, dependency-free X4 extension."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def validate_config(c):
    for key in ('consumption_seconds', 'refresh_seconds', 'buffer_hours',
                'budget_credits', 'development_period_seconds', 'development_duration_seconds'):
        if not isinstance(c[key], int) or isinstance(c[key], bool) or c[key] <= 0:
            raise ValueError(f'{key} must be a positive integer')
    if c['development_duration_seconds'] >= c['development_period_seconds']:
        raise ValueError('Development duration must be shorter than period')
    if c['development_multiplier'] < 1:
        raise ValueError('Development multiplier must be at least one')
    ids = [w['id'] for w in c['wares']]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('Ware IDs must be nonempty and unique')
    for w in c['wares']:
        if not w['id'].isascii() or not w['id'].isalnum():
            raise ValueError('Invalid ware identifier')
        if not isinstance(w['per_hour'], int) or isinstance(w['per_hour'], bool) or w['per_hour'] <= 0:
            raise ValueError('Rates must be positive integers')


def node(parent, tag, **attrs):
    return ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})


def value(parent, name, exact):
    return node(parent, 'set_value', name=name, exact=exact)


def include(parent, name):
    return node(parent, 'include_actions', ref=name)


def generate(c):
    validate_config(c)
    root = ET.Element('mdscript', name='ODE_ArgonPrime', attrib={
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:noNamespaceSchemaLocation': 'md.xsd'})
    cues = node(root, 'cues')
    lib = node(cues, 'library', name='Config')
    a = node(lib, 'actions')
    for name, exact in {
        '$Enabled': str(c['enabled']).lower(), '$Budget': f"{c['budget_credits']}Cr",
        '$DevelopmentEnabled': str(c['development_enabled']).lower(),
    }.items():
        value(a, name, exact)
    lib = node(cues, 'library', name='Refresh')
    a = node(lib, 'actions')
    include(a, 'Config')
    guard = node(a, 'do_if', value='$Station.exists and not $Station.iswreck and $Station.owner == faction.argon')
    fund = node(guard, 'do_if', value='$Enabled and $Station.money lt $Budget')
    node(fund, 'transfer_money', **{'from': 'faction.ownerless', 'to': '$Station',
                                  'amount': '$Budget - $Station.money'})
    value(guard, '$Unloading', 'table[]')
    transfers = node(guard, 'do_for_each', name='$Deal', **{'in': '$Transfers.keys.list'})
    dead = node(transfers, 'do_if', value='not $Deal.exists')
    node(dead, 'remove_value', name='$Transfers.{$Deal}')
    live = node(transfers, 'do_else')
    value(live, '$Unloading.{$Transfers.{$Deal}}', 'true')
    each = node(guard, 'do_for_each', name='$W', **{'in': '$Wares'})
    value(each, '$Ware', '$W.$Ware')
    each = node(each, 'do_if', value='not $Unloading.{$Ware}?')
    value(each, '$Stock', '$Station.cargo.{$Ware}.count')
    value(each, '$Desired', '[0, $W.$Target - $Stock].max')
    value(each, '$Price', '($Ware.minprice + ($Ware.maxprice - $Ware.minprice) * (0.2 + 0.6 * (1 - [1.0, $Stock / ($W.$Target * 1.0)].min)))')
    value(each, '$Price', '(($Price / 1Cr)i) * 1Cr')
    existing = node(each, 'do_if', value='$W.$Offer.exists')
    value(existing, '$Reserved', '[0, $W.$Offer.offeramount - $W.$Offer.amount].max')
    node(existing, 'update_trade', trade='$W.$Offer',
         amount='if $Enabled then [0, $Desired - $Reserved].max else 0',
         desiredamount='if $Enabled then $Desired else 0', price='$Price')
    new = node(each, 'do_elseif', value='$Enabled and $Desired gt 0')
    node(new, 'create_trade_offer', name='$W.$Offer', object='$Station', buyer='$Station',
         ware='$Ware', amount='$Desired', desiredamount='$Desired', price='$Price',
         virtual='false', virtualmoney='false', playeronly='false')
    lost = node(a, 'do_elseif', value='$Station.exists and not $Station.iswreck')
    each = node(lost, 'do_for_each', name='$W', **{'in': '$Wares'})
    old = node(each, 'do_if', value='$W.$Offer.exists')
    node(old, 'remove_trade_offer', object='$Station', tradeoffer='$W.$Offer')
    value(old, '$W.$Offer', 'null')
    lib = node(cues, 'library', name='Consume')
    a = node(lib, 'actions')
    include(a, 'Config')
    guard = node(a, 'do_if', value='$Enabled and $Station.exists and not $Station.iswreck and $Station.owner == faction.argon')
    value(guard, '$Elapsed', 'player.age - $Started')
    value(guard, '$Phase', f"$Elapsed % {c['development_period_seconds']}s")
    value(guard, '$Development', f"$DevelopmentEnabled and $Elapsed ge {c['development_period_seconds']}s and $Phase lt {c['development_duration_seconds']}s")
    each = node(guard, 'do_for_each', name='$W', **{'in': '$Wares'})
    value(each, '$Ware', '$W.$Ware')
    value(each, '$Rate', f"$W.$Rate * (if $Development and $W.$Development then {c['development_multiplier']} else 1)")
    value(each, '$Due', f"$W.$Carry + $Rate * {c['consumption_seconds']}.0 / 3600")
    value(each, '$Whole', '($Due)i')
    value(each, '$W.$Carry', '$Due - $Whole')
    value(each, '$Stock', '$Station.cargo.{$Ware}.count')
    value(each, '$Take', '[$Stock, $Whole].min')
    node(each, 'remove_cargo', object='$Station', ware='$Ware', exact='$Take', result='$Removed')
    node(each, 'debug_text', text="'[ODE] tick ware=%s stock=%s removed=%s unmet=%s development=%s'.[$Ware.id,$Stock,$Removed,$Whole - $Removed,$Development]")
    node(a, 'do_if', value='$Station.exists and not $Station.iswreck and $Station.owner != faction.argon')
    node(a[-1], 'debug_text', text="'[ODE] suspended: exchange owner changed; no funding or consumption'")
    include(a, 'Refresh')
    init = node(cues, 'cue', name='Init', namespace='this')
    node(init, 'delay', exact='10s')
    a = node(init, 'actions')
    include(a, 'Config')
    value(a, '$Station', 'null')
    value(a, '$Wares', '[]')
    value(a, '$Transfers', 'table[]')
    value(a, '$Started', 'player.age')
    for w in c['wares']:
        value(a, '$W', 'table[]')
        value(a, '$W.$Ware', 'ware.' + w['id'])
        value(a, '$W.$Rate', w['per_hour'])
        value(a, '$W.$Target', w['per_hour'] * c['buffer_hours'])
        value(a, '$W.$Development', str(w['development']).lower())
        value(a, '$W.$Carry', '0.0')
        value(a, '$W.$Offer', 'null')
        node(a, 'append_to_list', name='$Wares', exact='$W')
    enabled = node(a, 'do_if', value='$Enabled')
    node(enabled, 'find_sector', name='$Sector', macro='macro.' + c['sector_macro'])
    found = node(enabled, 'do_if', value='$Sector')
    node(found, 'create_station', name='$Station', macro='macro.station_gen_factory_base_01_macro',
         owner='faction.argon', sector='$Sector', state='componentstate.operational',
         constructionplan="'ode_argon_exchange'", rawname=repr(c['station_name']))
    node(found[-1], 'safepos', x='30km', y='10km', z='30km', radius='15km', includeplotbox='true')
    created = node(found, 'do_if', value='$Station.exists')
    node(created, 'set_object_account', object='$Station')
    node(created, 'create_control_entity', object='$Station', post='controlpost.manager')
    node(created, 'add_units', object='$Station', category='unitcategory.transport', mk='1', exact='10')
    include(created, 'Refresh')
    node(created, 'debug_text', text="'[ODE] created Argon Prime Orbital Exchange: %s'.[$Station]")
    node(found, 'do_else')
    node(found[-1], 'debug_text', text="'[ODE] BLOCKED: exchange creation failed'")
    node(enabled, 'do_else')
    node(enabled[-1], 'debug_text', text="'[ODE] BLOCKED: configured sector not found; no fallback station created'")
    children = node(init, 'cues')
    ready = node(children, 'cue', name='Ready')
    conditions = node(ready, 'conditions')
    node(conditions, 'event_cue_completed', cue='parent')
    node(conditions, 'check_value', value='$Station.exists')
    children = node(ready, 'cues')
    start = node(children, 'cue', name='DeliveryStarted', instantiate='true')
    conditions = node(start, 'conditions')
    node(conditions, 'event_trade_started', buyer='$Station')
    a = node(start, 'actions')
    value(a, '$Transfers.{event.param}', 'event.param.ware')
    done = node(children, 'cue', name='DeliveryCompleted', instantiate='true')
    conditions = node(done, 'conditions')
    node(conditions, 'event_trade_completed', buyer='$Station')
    a = node(done, 'actions')
    tracked = node(a, 'do_if', value='$Transfers.{event.param}?')
    node(tracked, 'remove_value', name='$Transfers.{event.param}')
    node(a, 'debug_text', text="'[ODE] delivered ware=%s amount=%s'.[event.param.ware.id,event.param.transferredamount]")
    include(a, 'Refresh')
    for name, seconds, library in [('RefreshTimer', c['refresh_seconds'], 'Refresh'),
                                   ('ConsumptionTimer', c['consumption_seconds'], 'Consume')]:
        timer = node(children, 'cue', name=name)
        node(timer, 'delay', exact=f'{seconds}s')
        a = node(timer, 'actions')
        include(a, library)
        node(a, 'reset_cue', cue='this')
    ET.indent(root, space='  ')
    return ET.tostring(root, encoding='unicode', xml_declaration=True) + '\n'


def build(package=False):
    c = json.loads((ROOT / 'config/argon-prime.json').read_text())
    (ROOT / 'extension/md/ODE_ArgonPrime.xml').write_text(generate(c))
    content = ET.Element('content', id=c['extension_id'], name='Domestic Economy — Argon Prime Prototype',
                         description='Experimental physical civilian demand sink for vanilla X4.',
                         author='Oveews', version=str(c['version']), date='2026-10-01', save='true', enabled='true')
    node(content, 'dependency', version='900')
    ET.indent(content, space='  ')
    (ROOT / 'extension/content.xml').write_text(ET.tostring(content, encoding='unicode', xml_declaration=True) + '\n')
    if package:
        dest = ROOT / 'dist/x4-domestic-economy-prototype.zip'
        dest.parent.mkdir(exist_ok=True)
        with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
            for p in sorted((ROOT / 'extension').rglob('*')):
                if p.is_file():
                    z.write(p, Path(c['extension_id']) / p.relative_to(ROOT / 'extension'))
        print(dest)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--package', action='store_true')
    build(p.parse_args().package)
