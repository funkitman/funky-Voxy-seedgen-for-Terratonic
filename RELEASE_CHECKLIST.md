# Public release checklist

- [x] Original Seedgen author and exact upstream commit identified.
- [x] MIT notice and upstream copyright retained; Funky changes identified.
- [x] Separate third-party redistribution policies documented.
- [x] Do not bundle Terralith/Terratonic or Minecraft/Voxy assets.
- [x] Build script embeds MIT LICENSE and attribution in the JAR.
- [ ] Compile with JDK 25 and confirm on Minecraft 26.3 / Fabric 0.19.5+.
- [ ] Inspect JAR (`jar tf ... | grep -E 'LICENSE|ATTRIBUTION'`).
- [ ] Run singleplayer and SunDroneSMP multiplayer smoke tests.
- [ ] Verify generated LOD against real server terrain, matching seed and pack versions.
- [ ] Produce downloadable compiled JAR + legal notices **only after build**.
- [ ] Mark first release EXPERIMENTAL unless compatibility is confirmed.
- [ ] Set GitHub repo visibility to Public manually in Settings → Danger Zone.
