# Attribution and provenance

**Original project:** Seedgen (Minecraft Fabric client mod) by **lyuwenhan (Wenhan)**.

- Source: https://github.com/lyuwenhan/minecraft-java-edition-mods/tree/main/seedgen
- Upstream version used as base: **Seedgen 1.2.10** (Minecraft 26.3)
- Pinned commit: `764038d59d09f892e3d09d62a37a512aa09f2bdf` (2026-11-15)
- Upstream license: **MIT**; original copyright **Copyright (c) 2026 lyuwenhan**. Full MIT text is in [LICENSE](LICENSE).

**Funky alterations:** `funkitman`, 2026. Experimental patches add a local Terralith/Terratonic datapack loading pathway for client-generated Voxy LODs, prefer modded worldgen settings over vanilla noise-router replacement, and validate dependencies before generating. The patch/build scripts and Funky-specific modifications are also MIT-licensed.

## AI-assisted development disclosure

**Every change made to the original Seedgen project in this Funky fork has been produced using artificial intelligence (AI) tools under the direction of `funkitman`.** This includes the Funky-specific Java changes, patch scripts, repository documentation, configuration additions, and build automation. Original upstream Seedgen code remains credited to lyuwenhan; this statement does **not** imply that upstream code was written with AI.

Project decisions and test requirements are provided by `funkitman`. AI-generated contributions are experimental until tested and verified in Minecraft; compilation alone is not proof of correct world generation.

**Not an official edition.** Independent, not endorsed by, affiliated with, or supported by lyuwenhan, Stardust Labs, Apollo, Mojang, or Voxy developers.

These repository files are patch scripts, not a redistributed copy of the complete upstream project. The build script fetches the upstream MIT-licensed source at the pinned commit, then applies Funky modifications. The build script embeds `LICENSE` and `ATTRIBUTION.md` in the compiled JAR resources.