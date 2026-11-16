# Funky Seedgen Terratonic v2 — test guide (Minecraft 26.3)

**Status:** GitHub Actions Java 25 build passed. Tested only for compilation, NOT for multiplayer generation or Terratonic fidelity.

## Scope: SunDroneSMP hybrid Voxy

SunDroneSMP has already-generated **vanilla chunks within a circular radius of 10,000 blocks around its original spawn center**. Voxy Server shares that LOD with clients. Funky Seedgen must **only write local generated Voxy chunks outside the circle**, using the same seed and Terralith + Terratonic worldgen datapacks as the server.

This client-only mod does NOT modify server chunks or install server datapacks.

## Safe Prism install (Windows 11, MC26.3)

1. Copy Prism instance `26.3 funky Ultimate 8.98 alpha` (never overwrite your only stable profile).
2. Remove/disable the old `seedgen` or `voxygen-1.2.10.jar`, and install **one v2 JAR** from the successful [GitHub Actions v2 build](https://github.com/funkitman/funky-Voxy-seedgen-for-Terratonic/actions).
3. Launch once so `minecraft/config/seedgen.json` is created (if it does not already exist), then exit.
4. Edit only the properties below — preserve your `seeds` map and other JSON properties:

```json
{
  "funkyTerratonic": true,
  "funkyServerHost": "sundrone.tplinkdns.com",
  "funkySpawnX": 0,
  "funkySpawnZ": 0,
  "funkyVanillaRadiusBlocks": 10000,
  "funkyBoundaryBufferBlocks": 0,
  "radius": 16,
  "threads": 4
}
```

**The snippet is not a replacement config file:** merge these fields into the existing JSON. **Set `funkySpawnX` and `funkySpawnZ` to the exact center of the original pregeneration!** 0,0 is just a placeholder assumption. Verify this before generating LODs.

5. Put **server-matching** 26.3 `01-terralith.zip` and `02-terratonic.zip` in `minecraft/config/funky-seedgen/packs/`. No datapack binaries are bundled, by design and licensing.
6. Reopen Prism instance, connect to `sundrone.tplinkdns.com`, run `/seedgen seed`, then `/seedgen status`.

If the world is still inside the protected radius, the status can say **inside protected vanilla spawn zone**, and that is intended. Go *near the known boundary* only after validating the spawn center and datapacks, preferably with `radius=16`.

## v2 implementation details

- Loads static block-tags before worldgen registry decoding using `TagLoader.loadTagsForExistingRegistries` and `TagLoader.buildUpdatedLookups`. This targets the v1 `minecraft:cannot_place_basalt_pillar_on` failure.
- V1's vanilla-only simplification is bypassed for an active Funky Terratonic generator, preserving datapack noise settings.
- Chunk XY rectangle vs spawn-centered circle check: ANY intersection with the 10,000-block vanilla disk excludes that chunk from **Seedgen Voxy output** (inside chunks may still be generated internally as dependency data near the edge).
- `receiver.hasData()` from original Seedgen still skips existing LODs; this does NOT guarantee a server/local race is impossible for all external chunks.
- Only `sundrone.tplinkdns.com` (including default port 25565) activates the custom packs; a non-target multiplayer host is blocked when Funky mode is on. Singleplayer keeps vanilla behavior.
- Initial `radius=16`, `threads=4` is recommended; `radius=1000` causes millions of generation targets and is not an appropriate first test.

## Current limitations

- Game runtime behavior and accuracy of Terratonic terrain remain **unverified**.
- The original seed and all worldgen datapacks must match the server **exactly**.
- 26.2/1.21.x datapacks are not automatically compatible with 26.3.
- Unmodified Minecraft static registry tags may differ from server-specific datapack tag state during actual placement. Compare generated hills/coasts to real server terrain before expanding radius.
- The shape is configured as a **circle**, not a square. If server pregen used a square, a different safe-zone geometry is needed.
- Old client Voxy cache may contain erroneous prior LOD; do not delete the entire cache as the first action.

## Diagnostics

The log must show:
```text
Funky Terratonic zone: server=..., spawn=(X,Z), vanillaRadius=10000 blocks
Funky Terratonic worldgen selected: true
Funky Terratonic local pack order (low -> high): ...
Funky Terratonic worldgen registries loaded successfully
```
If you see `Paused: local world-generation data is unavailable`, supply the first `Cannot create local generator` stack trace from `minecraft/logs/latest.log`.

**Test environment:** MC26.3, Fabric Loader 0.20.1, Java 25, Voxy 0.2.20-beta; compatible versions not otherwise guaranteed.

**License:** Seedgen-derived code MIT by lyuwenhan; no Terralith/Terratonic assets redistributed.
