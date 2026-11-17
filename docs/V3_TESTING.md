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

**SunDroneSMP GitHub inventory (may not equal deployed server):** `datapacks/Terralith_v2.6.5+26.3.zip` and `datapacks/terratonic-datapack-3.0.31.zip`. Copy the **deployed** files exactly before renaming for the local loader. Check the server's actual active `/datapack list` and files; archive names alone do not prove they are enabled.

**CAUTION about mod vs datapack:** If the server uses the **Terralith 2.6+ Fabric mod + Tectonic Fabric mod**, the standalone datapacks are **not guaranteed identical** to its active worldgen. Both versions need explicit comparison; same Minecraft version and seed are not enough. v3's safeguard only confirms Terralith biomes are *present in the local generator*, not that all worldgen/trees match the server.

## What's new in v3

- **Version/name:** `funkyGenSunDroneSmp-v3-MC26.3-Fabric.jar`. Keeps `fabric.mod.json` ID `seedgen` to preserve config/command compatibility.
- **Biome safety:** Abort local Overworld worldgen if the datapack-based biome source contains zero `terralith:` biomes. The log says `SAFE STOP` instead of writing vanilla LOD with wrong biome types.
- **Pack auditing:** Log SHA-256 and byte length for both local worldgen ZIPs. Compare with the **exact server worldgen resources**, where applicable.
- **LOD transport diagnostic:** `/seedgen status` and the log detect **VoxyServer or Voxy Server Side/LSS client mods**, but **cannot prove that the server completed a handshake or streamed any sections**.
- **v2 behavior retained:** protected vanilla 10,000-block circle, block tag preload and client-only integration.

## Why Voxy Server / Voxy Server Side may not stream

**Critical two-project distinction:** The SunDroneSMP GitHub repo includes `mods/voxy-server-side-fabric.jar` (Voxy Server Side / VSS), while an earlier Prism log had `VoxyServer-1.2.5-36.3.jar` marked **disabled**. These are **different projects with different client/server network protocols**. The repository file list is not proof of what is currently deployed.

If the live server uses **Voxy Server Side** (XANTHA / VSS):
1. Install the same 26.3 **Voxy Server Side** Fabric mod on the client, alongside Voxy. Disable the unrelated **VoxyServer** jar in the test profile to avoid confusion.
2. Verify `minecraft/config/vss-client-config.json` (client) and `config/vss-server-config.json` (server). LOD streaming must be enabled on both.
3. Try `/vss diag` on the client and `/vsslod stats` or `/vsslod diag` on the server **where supported by that exact build**, to check handshake and transfer activity. The official [VSS documentation](https://modrinth.com/mod/voxy-server-side) also documents `/vss clearcache`, but **back up data first and do not clear the cache as the first test**.

If the live server instead uses **VoxyServer** (PooSmacker):
1. Install the matching `VoxyServer-1.2.5-36.3.jar` on **both sides** and ensure it is enabled; previous client log showed it was disabled.
2. Check `minecraft/config/voxyserver-client.json` on the client and `config/voxyserver.json` on the server (per-server host:port profile matters).
3. Verify `/voxyserver stats` and `/voxyserver import existing status`. Where the server database has no pregenerated chunks, `/voxyserver import existing current` can populate it, but **schedule for low TPS load, monitor resources, and do not delete the DB**.

Use **one matching transport system** on both sides. Simply matching a numeric version between different projects cannot make their protocols communicate.

V3 looks for Fabric mod IDs `voxyserver`, `vss`, and `lss`; this only detects installed clients, **not active networking, handshake, server storage or data arrival**.

If Voxy already has stale/incorrect v1/v2 chunks, v3 will skip existing LOD. Use an isolated test profile/cache and compare before making any destructive cache changes.

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
