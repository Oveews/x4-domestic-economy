# In-game acceptance checklist

Build target: vanilla X4 9.x, no economy overhaul, disposable save. Record exact
game version, extension revision and other active extensions alongside the log.

## Load and station

- [ ] Game imports the MD without unknown actions, invalid expressions or macro errors.
- [ ] Exactly one exchange appears in Argon Prime, owned by ARG.
- [ ] All three modules are operational, separated and usable; M/S docking works.
- [ ] L freighter docking and cargo drones work.
- [ ] Seven buy offers appear; there are no sell offers or production modules.
- [ ] Account is funded; offers stay within native ware price bounds.

## Physical trade

- [ ] Manually sell a measured amount of Food Rations with an M ship.
- [ ] Seller receives the advertised credits; exchange physical cargo rises accordingly.
- [ ] After fifteen game minutes, stock drops by at most 150 Food Rations.
- [ ] No negative stock, deferred shortage debt or magically created wares.
- [ ] Observe an independent NPC freighter supply the exchange. Record its origin,
      ware, quantity and price. Player delivery alone does not pass the milestone.
- [ ] Repeat with an L freighter and two concurrent reservations of the same ware.
- [ ] During unloading, refreshing offers does not cancel or duplicate deliveries.
- [ ] The four-hour target limits demand; storage cannot overfill from repeated orders.
- [ ] Empty shelves pay more than stocked shelves; high-value shipbuilding wares do
      not cause disproportionate regional scarcity over several game hours.

## Persistence and suspension

- [ ] Save with stock and an incoming delivery; reload and complete the delivery.
- [ ] No duplicate station; stock and fractional consumption remain intact.
- [ ] Destroy the exchange in a separate test copy: no respawn, funding or error spam.
- [ ] Transfer ownership in a test environment: mod offers disappear and funding/
      consumption stop. Return to ARG and verify offer recreation.
- [ ] Set `enabled` false, rebuild and reload: unreserved mod demand becomes zero
      and consumption/funding stop. Already accepted deliveries may finish.

## Optional development pressure

Use a fresh save with development enabled. After eight game hours, verify the two
construction wares consume three times their baseline for two hours. Other rates
and stock targets must remain unchanged; then the baseline resumes.

## Log interpretation

Search `domestic-economy.log` for `[ODE]`. Each consumption record includes ware,
stock before consumption, actual removal, unmet consumption and development state.
The absence of script errors is necessary but does not prove NPC economic behaviour.

If no NPC arrives, first capture offers, price, station account, storage, manager,
trade visibility and nearby suppliers. Do not mark the prototype working merely
because the station was created.
