# funkyGenSunDroneSmp v3 — Minecraft 26.3 / Fabric test

**Experimental.** Compilation passed with Java 25 and the JAR contains all expected classes. **No claim of full multiplayer, worldgen fidelity, or VoxyServer handshake validation is made.**

## Architecture

- Within 10,000 blocks of the original spawn: server has pregenerated **vanilla** terrain. Funky Seedgen **does not inject** chunks whose footprint intersects the protected circle; **VoxyServer** is expected to supply these LODs after successful networking and initial import.
- Beyond 10,000 blocks: Funky Seedgen can inject local Terralith + Terratonic LODs **only when the actual runtime Overworld biome source has Terralith biomes**.
- Original project from lyuwenhan licensed MIT; all Funky code, documentation, and build modifications were made with AI tools under funkitman's direction; upstream credits preserved.

## Install test JAR

1. Duplicate the Prism Launcher instance `26.3 funky Ultimate 8.98 alpha`.
2. Disable v1/v2 Seedgen/Voxygen and ensure just **one** `seedgen` mod is enabled.
3. Download **funkyGenSunDroneSmp-v3-MC26.3-Fabric.jar** from the successful v3 workflow artifact and put it under `minecraft/mods/`.
4. Open `minecraft/config/seedgen.json` and merge these keys (do not erase the `seeds` map or unrelated configuration):

```json
{
  "funkyTerratonic": true,
  "funkyServerHost": "sundronesmp.com",
  "funkySpawnX": 0,
  "funkySpawnZ": 0,
  "funkyVanillaRadiusBlocks": 10000,
  "funkyBoundaryBufferBlocks": 0,
  "radius": 16,
  "threads": 4
}
```

**Important:** The **server address must exactly match** the Prism address actually used. v2 used a default of `sundrone.tplinkdns.com`; existing configs retain that value when upgraded, so change it if necessary. The 0,0 spawn center is only an assumption: verify the actual original pregeneration center.

5. Put the **exact server-version** datapacks in `minecraft/config/funky-seedgen/packs/` as `01-terralith.zip` and `02-terratonic.zip`. Both are user-supplied, **never bundled** for licensing reasons.
6. Connect to SunDroneSMP, enter `/seedgen seed`, `/seedgen on`, and `/seedgen status`. Test first near the outside boundary with radius 16 and threads 4.

**CAUTION about mod vs datapack:** If the server uses the **Terralith 2.6+ Fabric mod + Tectonic Fabric mod**, the standalone datapacks are **not guaranteed identical** to its active worldgen. Both versions need explicit comparison; same Minecraft version and seed are not enough. v3's safeguard only confirms Terralith biomes are *present in the local generator*, not that all worldgen/trees match the server.

## What's new in v3

- **Version/name:** `funkyGenSunDroneSmp-v3-MC26.3-Fabric.jar`. Keeps `fabric.mod.json` ID `seedgen` to preserve config/command compatibility.
- **Biome safety:** Abort local Overworld worldgen if the datapack-based biome source contains zero `terralith:` biomes. The log says `SAFE STOP` instead of writing vanilla LOD with wrong biome types.
- **Pack auditing:** Log SHA-256 and byte length for both local worldgen ZIPs. Compare with the **exact server worldgen resources**, where applicable.
- **VoxyServer diagnostic:** `/seedgen status` and the log show whether the **VoxyServer client mod is installed**, but **cannot prove that the server completed a handshake or streamed any sections**.
- **v2 behavior retained:** protected vanilla 10,000-block circle, block tag preload and client-only integration.

## Why Voxy Server might not stream

1. An earlier user's Prism log listed `VoxyServer-1.2.5-36.3.jar` as **disabled**. Recheck that it is enabled **now**. Same version in the folder is not sufficient.
2. Check the same correct `VoxyServer` build plus Voxy and Sodium are installed and enabled on the Fabric server. A client must have the `voxyserver` mod in addition to `voxy`.
3. In client `minecraft/config/voxyserver-client.json`, inspect the effective **default and per-server** profile. Enable LOD Streaming in the mod's ModMenu UI; address matching is keyed by host:port.
4. On the **server console**, check `/voxyserver stats` and `/voxyserver import existing status` if supported by the installed build. If previously generated vanilla regions were never imported, run `/voxyserver import existing current` while monitoring TPS and resource use; this reads the region files and can be expensive for a 10,000-block radius world. Do not wipe the existing Voxy DB.
5. Check server config `config/voxyserver.json` for `lodStreamRadius`, `maxSectionsPerTickPerPlayer`, streaming state, and any client-connection warnings.
6. If VoxyClient has stale/incorrect v1/v2 sections already cached, v3 will usually **skip existing LOD**; back up client cache and compare a fresh isolated test profile before deleting anything.

These Voxy Server checks are **separate** from Seedgen code: v3 does **not** implement Voxy Server's networking stack.

## Log lines for analysis

```text
Funky Terratonic zone: server=..., spawn=(...), vanillaRadius=10000
Funky Terratonic worldgen selected: true
funkyGenSunDroneSmp v3: local Terralith sha256=...
funkyGenSunDroneSmp v3: local Terratonic sha256=...
funkyGenSunDroneSmp v3: Overworld biome source has N biome choices, M Terralith
Funky Terratonic worldgen registries loaded successfully
```

**If the guard fires**, send `latest.log` containing `SAFE STOP` and the local ZIP SHA-256 lines, together with the server's exact Terralith/Tectonic versions and whether they are mods or datapacks.

## Known limits

- The generated features, especially trees, may still differ due to Minecraft worldgen behavior and custom mod/datapack versions. The original Seedgen author documents feature parity limitations (MC-55596).
- The server's LOD streaming is independent and must be tested separately.
- SHA-256 is diagnostic, not proof that two differently packaged worldgen implementations are equivalent.
- No in-game end-to-end validation has been performed. Make backups and test in a duplicated Prism profile.

Source acknowledgements: https://github.com/lyuwenhan/minecraft-java-edition-mods/tree/main/seedgen, https://github.com/PooSmacker/VoxyServer, https://modrinth.com/datapack/terralith, https://github.com/Apollounknowndev/tectonic/wiki/Terratonic-FAQ.
