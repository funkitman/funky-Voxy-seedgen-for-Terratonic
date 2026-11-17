#!/usr/bin/env python3
"""Apply funkyGenSunDroneSmp v3 AFTER original v1 and v2 patches on pinned MIT Seedgen source.

v3 adds fail-closed biome-source validation, datapack SHA-256 diagnostics and
VoxyServer client detection. Does NOT pretend to implement server LOD networking.
"""
import argparse
from pathlib import Path

def once(text: str, before: str, after: str, label: str) -> str:
    n=text.count(before)
    if n!=1:
        raise ValueError(f"{label}: expected one occurrence, found {n}")
    return text.replace(before,after,1)

def first_of_two(text: str,before: str,after: str,label: str) -> str:
    n=text.count(before)
    if n!=2:
        raise ValueError(f"{label}: expected two occurrences, found {n}")
    return text.replace(before,after,1)

def patch(root: Path) -> dict[Path,str]:
    files={
        "config":root/"src/main/java/com/example/seedgen/SeedgenConfig.java",
        "service":root/"src/main/java/com/example/seedgen/core/SeedgenGenerationService.java",
        "packs":root/"src/main/java/com/example/seedgen/core/FunkyTerratonicPacks.java",
        "mod":root/"src/main/java/com/example/seedgen/SeedgenMod.java",
        "gradle":root/"gradle.properties",
        "build":root/"build.gradle",
        "meta":root/"src/main/resources/fabric.mod.json"
    }
    contents={k:p.read_text(encoding="utf-8") for k,p in files.items()}

    # Fail closed when the actual biome source contains only vanilla biomes.
    # Upstream Seedgen builds MultiNoiseBiomeSource from a datapack registry,
    # but wrong pack versions can leave the minecraft:overworld preset vanilla.
    k="service"
    contents[k]=once(contents[k],
        'import net.minecraft.resources.ResourceKey;',
        'import net.minecraft.resources.ResourceKey;\n'
        'import net.fabricmc.loader.api.FabricLoader;',
        'FabricLoader import')
    contents[k]=first_of_two(contents[k],
        '\t\t\t\tbiomes = MultiNoiseBiomeSource.createFromPreset(preset);',
        '\t\t\t\tbiomes = MultiNoiseBiomeSource.createFromPreset(preset);\n'
        '\t\t\t\tif (FunkyTerratonicPacks.isActive()) {\n'
        '\t\t\t\t\tlong terralithBiomes = biomes.possibleBiomes().stream()\n'
        '\t\t\t\t\t\t\t.filter(holder -> holder.unwrapKey().map(key ->\n'
        '\t\t\t\t\t\t\t\t\tkey.identifier().getNamespace().equals("terralith")).orElse(false))\n'
        '\t\t\t\t\t\t\t.count();\n'
        '\t\t\t\t\tLOGGER.info("funkyGenSunDroneSmp v3: Overworld biome source has {} biome choices, {} Terralith",\n'
        '\t\t\t\t\t\t\tbiomes.possibleBiomes().size(), terralithBiomes);\n'
        '\t\t\t\t\tif (terralithBiomes == 0) {\n'
        '\t\t\t\t\t\tthrow new IllegalStateException("Funky v3 SAFE STOP: Overworld biome source contains ZERO "\n'
        '\t\t\t\t\t\t\t\t+ "Terralith biomes. Local LOD would have wrong biome/tree types. "\n'
        '\t\t\t\t\t\t\t\t+ "Use identical 26.3 Terralith + Terratonic SERVER datapacks; "\n'
        '\t\t\t\t\t\t\t\t+ "Terralith MOD worldgen is not automatically equivalent to the DATAPACK.");\n'
        '\t\t\t\t\t}\n'
        '\t\t\t\t}',
        'Overworld Terralith biome-source guard')

    contents[k]=once(contents[k],
        '\t\tif (current == null) {\n\t\t\tcurrent =\n\t\t\t\t\tnew Session(',
        '\t\tif (current == null) {\n'
        '\t\t\tif (FunkyTerratonicZone.active()\n'
        '\t\t\t\t&& !FabricLoader.getInstance().isModLoaded("voxyserver")\n'
        '\t\t\t\t&& !FabricLoader.getInstance().isModLoaded("vss")\n'
        '\t\t\t\t&& !FabricLoader.getInstance().isModLoaded("lss")) {\n'
        '\t\t\t\tLOGGER.warn("funkyGenSunDroneSmp v3: no client LOD-streaming mod detected! "\n'
        '\t\t\t\t\t\t+ "Install the SAME LOD project (VoxyServer or Voxy Server Side/LSS) on BOTH "\n'
        '\t\t\t\t\t\t+ "sides and verify its network handshake. These two projects are NOT interchangeable.");\n'
        '\t\t\t}\n'
        '\t\t\tcurrent =\n\t\t\t\t\tnew Session(',
        'VoxyServer diagnostic on new session')

    contents[k]=once(contents[k],
        '\t\t\t\t\t\t+ current.protectedVanilla.get()));',
        '\t\t\t\t\t\t+ current.protectedVanilla.get()))\n'
        '\t\t\t\t.copy().append(Component.literal("\\nFunky v3: LOD streaming client " +\n'
        '\t\t\t\t\t(FabricLoader.getInstance().isModLoaded("voxyserver") ? "VoxyServer loaded (handshake unverified)"\n'
        '\t\t\t\t\t : (FabricLoader.getInstance().isModLoaded("vss") || FabricLoader.getInstance().isModLoaded("lss"))\n'
        '\t\t\t\t\t  ? "Voxy Server Side/LSS loaded (handshake unverified)"\n'
        '\t\t\t\t\t  : "NONE detected; check matching server mod"))));',
        'Funky status VoxyServer diagnostics')

    # Debug actual selected pack content using stable per-file SHA-256.
    k="packs"
    contents[k]=once(contents[k],
        'import java.nio.file.Path;',
        'import java.nio.file.Path;\n'
        'import java.io.InputStream;\n'
        'import java.security.MessageDigest;\n'
        'import java.security.NoSuchAlgorithmException;\n'
        'import java.util.HexFormat;',
        'hash imports')
    contents[k]=once(contents[k],
        '        checkZip(terralith);\n        checkZip(terratonic);',
        '        checkZip(terralith);\n'
        '        checkZip(terratonic);\n'
        '        LOGGER.info("funkyGenSunDroneSmp v3: local Terralith sha256={}, size={} bytes",\n'
        '                sha256(terralith), size(terralith));\n'
        '        LOGGER.info("funkyGenSunDroneSmp v3: local Terratonic sha256={}, size={} bytes",\n'
        '                sha256(terratonic), size(terratonic));\n'
        '        LOGGER.warn("Check local datapack hashes against server worldgen pack hashes; "\n'
        '                + "matching seed and matching MC version alone do not guarantee matching biomes or trees.");',
        'datapack hashes on load')
    contents[k]=once(contents[k],
        '    private static void checkZip(Path file) {',
        '    private static long size(Path file) {\n'
        '        try { return Files.size(file); }\n'
        '        catch (IOException e) { throw new IllegalStateException("Cannot size " + file, e); }\n'
        '    }\n\n'
        '    private static String sha256(Path file) {\n'
        '        try (InputStream in = Files.newInputStream(file)) {\n'
        '            MessageDigest digest = MessageDigest.getInstance("SHA-256");\n'
        '            byte[] bytes = new byte[65536];\n'
        '            int count;\n'
        '            while ((count = in.read(bytes)) != -1) digest.update(bytes, 0, count);\n'
        '            return HexFormat.of().formatHex(digest.digest());\n'
        '        } catch (IOException | NoSuchAlgorithmException e) {\n'
        '            throw new IllegalStateException("Cannot hash local worldgen pack: " + file, e);\n'
        '        }\n'
        '    }\n\n'
        '    private static void checkZip(Path file) {',
        'hash helper methods')

    # Keep user config from v2, but fix clean-install host for the actual game server.
    k="config"
    contents[k]=once(contents[k],
        '\tpublic String funkyServerHost = "sundrone.tplinkdns.com";',
        '\tpublic String funkyServerHost = "sundronesmp.com";',
        'v3 hostname default')

    # Preserve technical mod ID 'seedgen' and version-friendly semver metadata.
    k="gradle"
    contents[k]=once(contents[k],
        'mod_version=1.2.10-funky-terratonic.2',
        'mod_version=3.0.0-funkygensundronesmp.3+mc26.3',
        'v3 mod version')
    k="build"
    contents[k]=once(contents[k],
        'archivesName = "seedgen-funky-terratonic"',
        'archivesName = "funkyGenSunDroneSmp"',
        'archive base name')
    k="meta"
    contents[k]=once(contents[k],
        '"name": "Seedgen - Funky Terratonic"',
        '"name": "funkyGenSunDroneSmp v3"',
        'display name')
    contents[k]=once(contents[k],
        '"description": "Experimental client-only Terralith + Terratonic datapack worldgen for Voxy; based on Wenhan Seedgen."',
        '"description": "AI-developed SunDroneSMP hybrid Voxy Seedgen with protected vanilla spawn LOD and validated Terralith biome source; original Seedgen by lyuwenhan."',
        'v3 description')
    return {files[k]:value for k,value in contents.items()}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seedgen_dir",type=Path)
    parser.add_argument("--dry-run",action="store_true")
    args=parser.parse_args()
    modified=patch(args.seedgen_dir.resolve())
    for path,text in modified.items():
        print(("CHECK" if args.dry_run else "WRITE"),path)
        if not args.dry_run:
            path.write_text(text,encoding="utf-8")
    print("funkyGenSunDroneSmp v3 patch successfully "+("validated" if args.dry_run else "applied"))
