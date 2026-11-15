#!/usr/bin/env python3
"""Apply Funky Terratonic modifications to the upstream MIT Seedgen 1.2.10 source.

Target: lyuwenhan/minecraft-java-edition-mods, commit 764038d59d09f892e3d09d62a37a512aa09f2bdf
Minecraft 26.3 / Fabric. This script does not compile or download dependencies.
"""

import argparse
from pathlib import Path


PACK_LOADER = r'''package com.example.seedgen.core;

import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.client.Minecraft;
import net.minecraft.server.packs.PackResources;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.repository.FolderRepositorySource;
import net.minecraft.server.packs.repository.PackRepository;
import net.minecraft.server.packs.repository.PackSource;
import net.minecraft.world.level.storage.LevelStorageSource;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.zip.ZipFile;

/**
 * Client-only isolated datapack stack for seed-based Terralith + Terratonic LOD.
 * This does not install datapacks into the connected multiplayer server.
 * Actual generation only starts after both client copies can be loaded.
 */
public final class FunkyTerratonicPacks {
    private static final Logger LOGGER = LoggerFactory.getLogger("seedgen-funky-terratonic");
    private static final String TERRALITH = "01-terralith.zip";
    private static final String TERRATONIC = "02-terratonic.zip";
    private static volatile boolean enabled;
    private static volatile boolean active;

    private FunkyTerratonicPacks() {}

    public static void configure(boolean selected) {
        enabled = selected;
        active = false;
        LOGGER.info("Funky Terratonic worldgen selected: {}", selected);
    }

    public static boolean enabled() {
        return enabled;
    }

    public static boolean isActive() {
        return active;
    }

    public static void markLoaded() {
        if (enabled) {
            active = true;
            LOGGER.info("Funky Terratonic worldgen registries loaded successfully");
        }
    }

    public static List<PackResources> openPacks() {
        if (!enabled) {
            return List.of();
        }

        Path root = FabricLoader.getInstance().getConfigDir().resolve("funky-seedgen/packs");
        Path terralith = root.resolve(TERRALITH);
        Path terratonic = root.resolve(TERRATONIC);
        checkZip(terralith);
        checkZip(terratonic);

        Path gameDir = Minecraft.getInstance().gameDirectory.toPath();
        PackRepository repository = new PackRepository(
                new FolderRepositorySource(
                        root,
                        PackType.SERVER_DATA,
                        PackSource.WORLD,
                        LevelStorageSource.parseValidator(gameDir.resolve("allowed_symlinks.txt"))));
        repository.reload();

        List<String> selected = new ArrayList<>(2);
        selected.add(requiredId(repository, TERRALITH));
        selected.add(requiredId(repository, TERRATONIC));
        repository.setSelected(selected); // Later packs override earlier ones.

        List<PackResources> packs = repository.openAllSelected();
        if (packs.size() != 2) {
            packs.forEach(PackResources::close);
            throw new IllegalStateException(
                    "Funky Terratonic expected exactly two usable 26.3 data packs, got "
                            + packs.size() + ": " + selected);
        }
        LOGGER.info("Funky Terratonic local pack order (low -> high): {}", selected);
        return packs;
    }

    private static String requiredId(PackRepository repo, String fileName) {
        String suffix = "/" + fileName.toLowerCase(Locale.ROOT);
        return repo.getAvailableIds().stream()
                .filter(id -> id.toLowerCase(Locale.ROOT).endsWith(suffix))
                .findFirst()
                .orElseThrow(() -> new IllegalStateException(
                        "Minecraft rejected or could not discover " + fileName
                                + ". Check pack.mcmeta for Minecraft 26.3 compatibility."));
    }

    private static void checkZip(Path file) {
        if (!Files.isRegularFile(file)) {
            throw new IllegalStateException("Required local datapack is missing: " + file);
        }
        try (ZipFile zip = new ZipFile(file.toFile())) {
            if (zip.getEntry("pack.mcmeta") == null) {
                throw new IllegalStateException(file + " has no pack.mcmeta at ZIP root");
            }
            boolean hasData = zip.stream().anyMatch(e -> e.getName().startsWith("data/"));
            if (!hasData) {
                throw new IllegalStateException(file + " has no data/ folder at ZIP root");
            }
        } catch (IOException e) {
            throw new IllegalStateException("Unreadable datapack ZIP: " + file, e);
        }
    }
}
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f'{label}: expected 1 anchor, got {count}; upstream may have changed')
    return text.replace(old, new, 1)


def prepare_changes(root: Path) -> dict[Path, str]:
    p = lambda sub: root / sub
    config = p('src/main/java/com/example/seedgen/SeedgenConfig.java')
    mod = p('src/main/java/com/example/seedgen/SeedgenMod.java')
    rules = p('src/main/java/com/example/seedgen/core/SeedgenWorldgenRules.java')
    service = p('src/main/java/com/example/seedgen/core/SeedgenGenerationService.java')
    gradle = p('gradle.properties')
    build = p('build.gradle')
    metadata = p('src/main/resources/fabric.mod.json')
    helper = p('src/main/java/com/example/seedgen/core/FunkyTerratonicPacks.java')

    files = [config, mod, rules, service, gradle, build, metadata]
    for file in files:
        if not file.is_file():
            raise FileNotFoundError(f'Missing original upstream file: {file}')
    if helper.exists():
        raise FileExistsError(f'{helper} exists; use a clean upstream clone')
    c = {file: file.read_text(encoding='utf-8') for file in files}
    if 'mod_version=1.2.10' not in c[gradle] or 'minecraft_version=26.3' not in c[gradle]:
        raise ValueError('Expected upstream Seedgen 1.2.10 for Minecraft 26.3')

    c[config] = replace_once(
        c[config],
        '\tpublic boolean generateForFreecam = false;',
        '\tpublic boolean generateForFreecam = false;\n'
        '\t// Experimental; requires exact local Terralith and Terratonic datapack copies.\n'
        '\tpublic boolean funkyTerratonic = false;',
        'config field')
    c[mod] = replace_once(
        c[mod],
        'import com.example.seedgen.core.SeedgenGenerationService;',
        'import com.example.seedgen.core.SeedgenGenerationService;\n'
        'import com.example.seedgen.core.FunkyTerratonicPacks;',
        'mod import')
    c[mod] = replace_once(
        c[mod],
        '\t\tconfig = SeedgenConfig.load();\n\t\tSeedgenGenerationService.initialize();',
        '\t\tconfig = SeedgenConfig.load();\n'
        '\t\tFunkyTerratonicPacks.configure(config.funkyTerratonic);\n'
        '\t\tSeedgenGenerationService.initialize();',
        'config initialization')
    c[rules] = replace_once(
        c[rules],
        '\t\tHolder<NoiseGeneratorSettings> settingsHolder = noiseGenerator.generatorSettings();',
        '\t\t// Terratonic changes noise, climate/biomes and surface rules.\n'
        '\t\t// Vanilla cave simplification must NOT replace its noise router.\n'
        '\t\tif (FunkyTerratonicPacks.isActive()) {\n'
        '\t\t\treturn original;\n'
        '\t\t}\n\n'
        '\t\tHolder<NoiseGeneratorSettings> settingsHolder = noiseGenerator.generatorSettings();',
        'preserve custom terrain')
    c[service] = replace_once(
        c[service],
        'import net.minecraft.server.packs.PackType;',
        'import net.minecraft.server.packs.PackType;\n'
        'import net.minecraft.server.packs.PackResources;',
        'service imports')
    c[service] = replace_once(
        c[service],
        '\t\t\t\tMultiPackResourceManager resources =\n'
        '\t\t\t\t\t\tnew MultiPackResourceManager(\n'
        '\t\t\t\t\t\t\t\tPackType.SERVER_DATA,\n'
        '\t\t\t\t\t\t\t\tList.of(client.getVanillaPackResources().fullResources()));',
        '\t\t\t\t// Vanilla first; Terralith second; Terratonic last/highest priority.\n'
        '\t\t\t\tList<PackResources> worldgenPacks = new ArrayList<>();\n'
        '\t\t\t\tworldgenPacks.add(client.getVanillaPackResources().fullResources());\n'
        '\t\t\t\tworldgenPacks.addAll(FunkyTerratonicPacks.openPacks());\n'
        '\t\t\t\tMultiPackResourceManager resources =\n'
        '\t\t\t\t\t\tnew MultiPackResourceManager(PackType.SERVER_DATA, worldgenPacks);',
        'worldgen datapack resource stack')
    c[service] = replace_once(
        c[service],
        '\t\t\t\t\tvanillaWorldgenRegistries = cached;\n\t\t\t\t\treturn cached;',
        '\t\t\t\t\tvanillaWorldgenRegistries = cached;\n'
        '\t\t\t\t\tFunkyTerratonicPacks.markLoaded();\n'
        '\t\t\t\t\treturn cached;',
        'activate only after successful registry load')
    c[gradle] = replace_once(
        c[gradle], 'mod_version=1.2.10', 'mod_version=1.2.10-funky-terratonic.1', 'version')
    c[build] = replace_once(
        c[build], 'archivesName = "seedgen"', 'archivesName = "seedgen-funky-terratonic"', 'archive name')
    c[metadata] = replace_once(
        c[metadata], '"name": "Seedgen"', '"name": "Seedgen - Funky Terratonic"', 'mod name')
    c[metadata] = replace_once(
        c[metadata],
        '"description": "Locally generates vanilla terrain from a known world seed without requiring the server to generate it."',
        '"description": "Experimental client-only Terralith + Terratonic datapack worldgen for Voxy; based on Wenhan Seedgen."',
        'description')
    c[helper] = PACK_LOADER
    return c


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('seedgen_dir', type=Path, help='Upstream repository seedgen/ directory')
    parser.add_argument('--dry-run', action='store_true', help='Verify anchors and print changes only')
    args = parser.parse_args()
    root = args.seedgen_dir.resolve()
    modified = prepare_changes(root)
    for path, contents in modified.items():
        print(f'{"CHECK" if args.dry_run else "WRITE"}: {path.relative_to(root)} ({len(contents)} chars)')
        if not args.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents, encoding='utf-8')
    print('Funky Terratonic source patch applied' if not args.dry_run else 'All upstream anchors matched')


if __name__ == '__main__':
    main()
