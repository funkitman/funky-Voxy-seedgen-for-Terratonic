# Public release checklist

- [x] Original Seedgen author and exact upstream commit identified.
- [x] MIT notice and upstream copyright retained; Funky changes identified.
- [x] Separate third-party redistribution policies documented.
- [x] Do not bundle Terralith/Terratonic or Minecraft/Voxy assets.
- [x] Build script embeds MIT LICENSE and attribution in the JAR.
- [x] Java 25 / Minecraft 26.3 compilation passed in GitHub Actions; runtime Fabric behavior unverified.
- [x] Inspect v2 JAR: LICENSE, ATTRIBUTION.md, and FunkyTerratonicZone.class found.
- [ ] Run v2 smoke test in a cloned Prism instance on SunDroneSMP; verify original spawn X/Z, both exact server datapacks, and tag registry loading.
- [ ] Verify generated LOD against real server terrain, matching seed and pack versions.
- [x] Produce downloadable *experimental test* JAR + legal notices from successful GitHub Actions build (not a verified stable release).
- [ ] Mark first release EXPERIMENTAL unless compatibility is confirmed.
- [ ] Set GitHub repo visibility to Public manually in Settings → Danger Zone.
