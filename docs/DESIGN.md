# Design boundaries

The abstract economy decides demand; the native physical economy transports and
stores goods. Scripted trade offers use `virtual="false"` and `virtualmoney="false"`.
No trader AI, ship stats, weapons, jobs or universe definitions are replaced.
Only an additive construction-plan diff and a namespaced MD controller are added.

The first pass uses deterministic demand. Random variation would obscure baseline
measurements. Prices span 20–80% of the interval between each ware's native minimum
and maximum: empty shelves bid higher; full shelves bid lower. There are no sell
offers. The station's name represents a planetary interface, not a landable planet.

## First acceptance gate

A normal NPC freighter buys goods elsewhere, sells them into physical exchange
storage, receives payment, and later another buy offer appears after stock is
consumed. The same station survives save/reload without duplicate creation. Both
M and L deliveries must work without cancelled-order churn or storage overfill.

## Subsequent increments

1. Tune demand against baseline production and scarcity; polish the station layout.
2. Use existing faction trading stations as the regional logistics hubs and
   measure freight behaviour between them and planetary exchanges. Add a new
   regional station only where sustained demand, long routes and poor market
   coverage demonstrate a distribution gap. Distinguish missing production from
   missing distribution: another warehouse cannot cure absent suppliers. A hub
   needs suppliers, onward customers and traders. Explicit faction expansion
   logic may be required; do not assume vanilla AI recognises scripted civilian
   demand and builds infrastructure accordingly. A hierarchy of stations alone
   does not force native traders to route via hubs. Frontier FOB demand can
   contribute to the case for a new hub.
3. Add a small fleet FOB, first proving native repair/rearm support. Maintenance,
   replacement fighters and fleet return behaviour need separate implementation;
   consuming generic wares does not itself sustain fleets.
4. Generalise market records beyond Argon Prime, with faction-specific baskets.
5. Add terraforming integration. Getsu Fune and relevant Pioneer planetary markets
   must follow verified vanilla plot/project state. Do not infer civilisation from
   background planet artwork or unlock every target after one generic milestone.
6. Add station residents and then prosperity/migration, keeping worker production
   usable during civilian shortages. Avoid double-counting native food/medical use.
7. Add Reemergence as a separate universe dataset/integration extension. Keep IDs,
   ownership, trade regions and plot gates out of the general economic controller.
8. Evaluate civilian wares, passengers and tourism after the existing economy loop
   is stable. New ship models and UI are independent workstreams.

## Known uncertainties

- No X4 runtime or local game XSDs are present in the build environment.
- Sector macro, creation completeness, manager initialisation, physical offers,
  reservation semantics and ownership handling require live-game confirmation.
- The module IDs and L storage capacity were cross-checked against extracted game
  data; snap geometry was not. Initial modules intentionally have no snap links.
- Native traders may ignore a new destination due to range, prices, trade knowledge,
  faction relations, competing demand or storage/offer behaviour. Diagnose these
  before spawning special traders or promising automatic freight corridors.
- NPC supply, save safety, compatibility with other economy mods and uninstall are
  not claimed. No RE or VRO compatibility testing has occurred.
- Funding models off-map spending; planetary exports and monetary conservation are
  beyond this proof of concept.
