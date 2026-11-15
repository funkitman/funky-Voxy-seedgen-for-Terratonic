# Funky Voxy Seedgen for Terratonic (Minecraft 26.3)

**EXPERIMENTAL SOURCE PATCH — not a compiled or tested Fabric mod.**

An unofficial modification of **Seedgen 1.2.10** by [lyuwenhan](https://github.com/lyuwenhan/minecraft-java-edition-mods/tree/main/seedgen), originally licensed under **MIT**. This project is distinct from MobiusMeansBusiness's Voxy SeedGen and Voxygen 3.

## Purpose

Create distant Voxy LOD from known world seed and the *same* Terralith + Terratonic worldgen datapacks used by a server. The experimental modification aims to load an isolated local datapack stack in vanilla → Terralith → Terratonic priority and preserve Terratonic noise settings instead of substituting vanilla terrain.

**Not verified**: Minecraft 26.3, Fabric Loader >=0.19.5, Java 25. Compatibility and generated terrain correctness remain untested. Do not install in your only Prism instance.

## Build

On a Linux system with JDK 25, Git, Python 3, Gradle/Maven network access:

```bash
chmod +x build_on_linux.sh
./build_on_linux.sh
```

The script retrieves **upstream commit `764038d59d09f892e3d09d62a37a512aa09f2bdf`**, tests and applies the Funky patch and attempts a Gradle build. The output directory should contain the experimental JAR and attribution/license files. The current patch has **not** been compiled or run in Minecraft.

## Local packs (NOT included)

Users must independently download compatible official datapacks and place them in:

```text
<Prism instance>/minecraft/config/funky-seedgen/packs/
  01-terralith.zip
  02-terratonic.zip
```

These must match the **server's exact versions, worldgen and seed**. When using Terralith + Tectonic **mods** instead of datapacks, matching these ZIPs is not sufficient to prove equivalence.

Use `python3 validate_packs.py "/path/to/packs"` to check ZIP basics. After compiling on a **copy** of the Prism instance, remove the original `seedgen` mod JAR, enable `"funkyTerratonic": true` in `config/seedgen.json`, and start with radius 16 and threads 4. Use `/seedgen status` to diagnose. Do not delete Voxy cache until correct terrain has been verified.

## Legal and attribution

- [LICENSE](LICENSE) — upstream MIT license and Funky modification copyright; applies to original Seedgen-derived code and this repository's own modifications.
- [ATTRIBUTION.md](ATTRIBUTION.md) — upstream authorship, exact pinned version, and differences.
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) — **Terralith uses a separate Stardust Labs license**. NO Terralith, Tectonic/Terratonic or other third-party assets may be committed here or bundled into our release.
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) — what is complete, and what still requires testing.

This is an unofficial community derivative, **not endorsed or maintained by the original Seedgen developer**. This repository provides a patch against a pinned MIT source; it is not the full upstream source mirror.
