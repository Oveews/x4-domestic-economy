# X4 Domestic Economy

An experimental civilian demand layer for **vanilla X4: Foundations 9.x**.

**Status: first implementation; structural checks and offline balance tests only.
Not yet validated against an installed game's XSDs or tested in X4.**

The first milestone is deliberately small: an ARG-owned **Argon Prime Orbital
Exchange** that buys seven existing wares, stores physical deliveries, and consumes
stock every fifteen game minutes to represent planetary demand. Ordinary ships must
deliver the goods. No cargo is spawned or teleported to satisfy consumption.

| Ware | Consumption/hour | Target stock |
| --- | ---: | ---: |
| Food Rations | 600 | 2,400 |
| Medical Supplies | 150 | 600 |
| Energy Cells | 1,500 | 6,000 |
| Hull Parts | 150 | 600 |
| Claytronics | 50 | 200 |
| Microchips | 50 | 200 |
| Advanced Electronics | 20 | 80 |

These are initial test values, not established balance. Buy prices fall with stock
and remain inside vanilla min/max prices. Offers refresh every game minute and
subtract outstanding reservations. Fractional consumption carries between ticks;
unmet consumption expires instead of becoming unlimited demand debt.

## Install the prototype

1. Build an archive with `python tools/build.py --package`, or download the
   artifact from a successful GitHub Actions run.
2. Extract the `oveews_domestic_economy` folder into the X4 installation's
   `extensions` directory. The result must be
   `extensions/oveews_domestic_economy/content.xml`.
3. Enable the extension and use a disposable vanilla test save. Start X4 with
   `-debug scripts -logfile domestic-economy.log`.
4. After about ten game seconds, locate the new exchange in Argon Prime. Expected
   placement is near (30 km, 10 km, 30 km), adjusted by the safe-position search.
5. Follow [the playtest checklist](docs/PLAYTEST.md).

The first station is seeded operationally to isolate trading from construction.
It contains a vanilla M/S dock, L/XL pier, L container storage and ten cargo drones.
The prototype uses spaced, unconnected modules; geometry and docking need checking
in game before a polished connected design is introduced. It has no habitation or
production modules, keeping native workforce demand out of the first experiment.

## Funding and lifecycle

The exchange represents spending by an off-map planet. Its account is topped up
from the engine's ownerless faction to a configurable 20 million credit budget.
**This introduces credits into the space economy deliberately.** Finite buy targets
and consumption rates cap the market; this is not a simulated planetary treasury.

Init is a saved, one-time cue. Loading the same save should preserve its station
reference, stock, timers and fractional counters. Destruction suspends trading and
consumption; this build does not respawn it. Changing ownership removes this mod's
offers and suspends funding/consumption. There is no automated uninstall or saved
state migration yet: restore the pre-mod test save to roll back the experiment.

## Development

Requires Python 3.10+ for build, structural validation and offline tests.

```sh
python tools/build.py
python tools/validate.py
python -m unittest discover -s tests -v
python tools/build.py --package
```

Edit `config/argon-prime.json`, then regenerate. `extension/md/ODE_ArgonPrime.xml`
is committed so that the repository contains an installable extension. CI detects
stale generated XML before rebuilding. Changing rates or targets requires a fresh
test save; existing saved ware records are not migrated in this prototype.

For real schema validation, extract your own game's schema files, preserving
`md/md.xsd` and `libraries/` paths. Install `lxml`, then run:

```sh
python tools/validate.py --schema-root /path/to/extracted-game
```

XSD validation cannot establish runtime expression correctness or NPC trading
behaviour. The repository does not ship Egosoft's schemas or game assets.

An optional development cycle is implemented but disabled for the baseline test.
Enable `development_enabled` to triple Hull Parts and Claytronics consumption for
two game hours every eight hours after the first eight hours. Stock targets remain
fixed, so the surge tests replenishment under pressure rather than unlimited buying.

## Direction

See [the design boundaries and roadmap](docs/DESIGN.md). Vanilla comes first.
Existing faction trading stations form the regional hub network; new hubs should
fill evidenced distribution gaps rather than duplicate the existing stations.
Reemergence integration, fleet FOBs, terraforming, civilian habitats, hub expansion,
prosperity and passengers follow only once physical NPC supply has been observed.

Independent project; not affiliated with Egosoft or the separate Civilian Economy
mod. No scripts, layouts or assets from that mod are included.

## References

- [Egosoft Mission Director guide](https://wiki.egosoft.com/X%20Rebirth%20Wiki/Modding%20support/Mission%20Director%20Guide/)
- [Egosoft Argon Prime sector information](https://wiki.egosoft.com/X4%20Foundations%20Wiki/Manual%20and%20Guides/Objects%20in%20the%20Game%20Universe/Systems%2C%20Sectors%20and%20Zones/Systems%20Database/Argon%20Prime/)
- [Schema-derived script command reference](https://chemodun.github.io/x4/modding-support/scripting-md-libraries-map/script-commands/)
- [Extracted game module identifiers and capacities](https://github.com/Mistralys/x4-core/tree/master/data)

X4: Foundations and its assets belong to Egosoft. Original project code is MIT licensed.
