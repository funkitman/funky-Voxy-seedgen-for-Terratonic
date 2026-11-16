#!/usr/bin/env python3
"""Funky v2 source patch, applied AFTER apply_funky_terratonic.py to pinned upstream."""
import argparse
from pathlib import Path

ZONE = r'''package com.example.seedgen.core;

import com.example.seedgen.SeedgenConfig;
import net.minecraft.world.level.Level;
import net.minecraft.resources.ResourceKey;
import net.minecraft.client.Minecraft;

import java.util.Locale;
import java.util.Objects;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * No Seedgen output in the pre-generated 10,000 block vanilla circle.
 * Only a specifically configured multiplayer server can enable this policy.
 * Proximity is from the actual spawn center, not world 0,0 unless configured.
 */
public final class FunkyTerratonicZone {
    private static final Logger LOGGER = LoggerFactory.getLogger("seedgen-funky-zone");
    private static volatile Settings current;

    private record Settings(String server, int spawnX, int spawnZ, int radius, int buffer) {}

    private FunkyTerratonicZone() {}

    public static boolean isTarget(SeedgenConfig config, String serverAddress) {
        if (serverAddress == null || config.funkyServerHost == null
                || config.funkyServerHost.isBlank()) {
            return false;
        }
        String actual = serverAddress.toLowerCase(Locale.ROOT);
        String expected = config.funkyServerHost.toLowerCase(Locale.ROOT);
        return actual.equals(expected) || actual.equals(expected + ":25565");
    }

    public static void configure(SeedgenConfig config, String serverAddress, boolean singleplayer) {
        Settings next = null;
        if (config.funkyTerratonic && !singleplayer && isTarget(config, serverAddress)
                && config.funkyVanillaRadiusBlocks > 0 && config.funkyVanillaRadiusBlocks <= 30_000_000) {
            next = new Settings(serverAddress, config.funkySpawnX, config.funkySpawnZ,
                    config.funkyVanillaRadiusBlocks, Math.max(0, config.funkyBoundaryBufferBlocks));
        }
        if (!Objects.equals(current, next)) {
            current = next;
            if (next != null) {
                LOGGER.info("Funky Terratonic zone: server={}, spawn=({},{}), vanillaRadius={} blocks, buffer={}",
                        next.server(), next.spawnX(), next.spawnZ(), next.radius(), next.buffer());
            } else {
                LOGGER.info("Funky Terratonic protected zone not active");
            }
        }
    }

    public static boolean active() {
        return current != null;
    }

    public static boolean isProtected(ResourceKey<Level> dimension, int chunkX, int chunkZ) {
        if (!Level.OVERWORLD.equals(dimension)) {
            return false;
        }
        Settings s = current;
        if (s == null) return false;
        // The entire chunk rectangle must be outside the circle before we can emit it.
        // Use long before shifting for negative coordinates and overflow safety.
        long x0 = ((long) chunkX) * 16L;
        long z0 = ((long) chunkZ) * 16L;
        long x1 = x0 + 15L;
        long z1 = z0 + 15L;
        long closestX = Math.max(x0, Math.min((long)s.spawnX(), x1));
        long closestZ = Math.max(z0, Math.min((long)s.spawnZ(), z1));
        long dx = closestX - (long)s.spawnX();
        long dz = closestZ - (long)s.spawnZ();
        long radius = (long)s.radius() + s.buffer();
        return dx * dx + dz * dz <= radius * radius;
    }

    public static boolean windowFullyProtected(ResourceKey<Level> dimension,
            int centerChunkX, int centerChunkZ, int radiusChunks) {
        Settings s = current;
        if (s == null || !Level.OVERWORLD.equals(dimension)) return false;
        long r = (long) s.radius() + s.buffer();
        long maxX = ((long)centerChunkX + radiusChunks) * 16 + 15;
        long minX = ((long)centerChunkX - radiusChunks) * 16;
        long maxZ = ((long)centerChunkZ + radiusChunks) * 16 + 15;
        long minZ = ((long)centerChunkZ - radiusChunks) * 16;
        long farX = Math.max(Math.abs(minX - s.spawnX()), Math.abs(maxX - s.spawnX()));
        long farZ = Math.max(Math.abs(minZ - s.spawnZ()), Math.abs(maxZ - s.spawnZ()));
        return farX * farX + farZ * farZ <= r * r;
    }
}
'''

def once(s: str, original: str, replacement: str, name: str) -> str:
    found = s.count(original)
    if found != 1:
        raise ValueError(f'{name}: expected 1 target, found {found}')
    return s.replace(original,replacement,1)

def first_of_two(s: str, original: str, replacement: str, name: str) -> str:
    found = s.count(original)
    if found != 2:
        raise ValueError(f'{name}: expected 2 occurrences, found {found}')
    return s.replace(original, replacement, 1)

def changed(root: Path) -> dict[Path,str]:
    path=lambda s:root/s
    cfg=path('src/main/java/com/example/seedgen/SeedgenConfig.java')
    mod=path('src/main/java/com/example/seedgen/SeedgenMod.java')
    service=path('src/main/java/com/example/seedgen/core/SeedgenGenerationService.java')
    packs=path('src/main/java/com/example/seedgen/core/FunkyTerratonicPacks.java')
    gradle=path('gradle.properties')
    zone=path('src/main/java/com/example/seedgen/core/FunkyTerratonicZone.java')
    if zone.exists(): raise ValueError('The v2 zone class already exists; apply only once on a clean v1 patched source')
    c={f:f.read_text(encoding='utf-8') for f in (cfg,mod,service,packs,gradle)}
    c[cfg]=once(c[cfg],
        '\tpublic boolean funkyTerratonic = false;',
        '\tpublic boolean funkyTerratonic = false;\n'
        '\t// Funky v2: protection settings for the pre-generated vanilla disk.\n'
        '\t// Confirm the exact original spawn coords before using this on SunDroneSMP.\n'
        '\tpublic String funkyServerHost = "sundrone.tplinkdns.com";\n'
        '\tpublic int funkySpawnX = 0;\n'
        '\tpublic int funkySpawnZ = 0;\n'
        '\tpublic int funkyVanillaRadiusBlocks = 10000;\n'
        '\tpublic int funkyBoundaryBufferBlocks = 0;',
        'v2 config fields')
    c[mod]=once(c[mod],
        'import com.example.seedgen.core.FunkyTerratonicPacks;',
        'import com.example.seedgen.core.FunkyTerratonicPacks;\n'
        'import com.example.seedgen.core.FunkyTerratonicZone;',
        'v2 mod import')
    c[mod]=once(c[mod],
        'FunkyTerratonicPacks.configure(config.funkyTerratonic);',
        'FunkyTerratonicPacks.configure(false); // enabled after target server is verified',
        'defer pack activation')
    c[mod]=once(c[mod],
        '\t\t\t\t\tString worldKey = getCurrentWorldKey();',
        '\t\t\t\t\tString worldKey = getCurrentWorldKey();\n'
        '\t\t\t\t\tFunkyTerratonicZone.configure(config, worldKey, client.getSingleplayerServer() != null);\n'
        '\t\t\t\t\tFunkyTerratonicPacks.configure(FunkyTerratonicZone.active());',
        'server guard')
    c[packs]=once(c[packs],
        '    public static void configure(boolean selected) {\n'
        '        enabled = selected;\n'
        '        active = false;',
        '    public static void configure(boolean selected) {\n'
        '        if (enabled == selected) return;\n'
        '        enabled = selected;\n'
        '        active = false;',
        'only reset pack state when mode switches')

    c[service]=once(c[service],
        'import net.minecraft.resources.ResourceKey;',
        'import net.minecraft.resources.ResourceKey;\n'
        'import net.minecraft.tags.TagLoader;',
        'TagLoader import')

    # Verify server, world and all generation targets before creating the session.
    c[service]=once(c[service],
        '\t\tClientLevel level = client.level;\n\t\tconfigureWorkers(config.threads);',
        '\t\tClientLevel level = client.level;\n'
        '\t\tif (config.funkyTerratonic && client.getSingleplayerServer() == null\n'
        '\t\t\t\t&& !FunkyTerratonicZone.isTarget(config, serverAddress)) {\n'
        '\t\t\tretire(Component.literal("Funky Terratonic: blocked on non-target server " + serverAddress));\n'
        '\t\t\treturn;\n'
        '\t\t}\n'
        '\t\tconfigureWorkers(config.threads);',
        'reject unexpected server')
    c[service]=once(c[service],
        '\t\tif (!playerTarget.isActive()) {\n'
        '\t\t\tretire(Component.translatable("command.seedgen.state.waiting_world"));\n'
        '\t\t\treturn;\n'
        '\t\t}',
        '\t\tif (!playerTarget.isActive()) {\n'
        '\t\t\tretire(Component.translatable("command.seedgen.state.waiting_world"));\n'
        '\t\t\treturn;\n'
        '\t\t}\n'
        '\t\tif (FunkyTerratonicZone.windowFullyProtected(dimension, playerTarget.unitX(),\n'
        '\t\t\t\tplayerTarget.unitZ(), playerTarget.radius())\n'
        '\t\t\t\t&& !freecamTarget.isActive() && !xaeroMapTarget.isActive()\n'
        '\t\t\t\t&& !journeyMapTarget.isActive()) {\n'
        '\t\t\tretire(Component.literal("Funky: inside protected vanilla spawn zone; Voxy Server supplies LOD"));\n'
        '\t\t\treturn;\n'
        '\t\t}',
        'avoid unnecessary generator inside vanilla zone')

    c[service]=once(c[service],
        '\t\tprivate final AtomicInteger skippedExisting = new AtomicInteger();',
        '\t\tprivate final AtomicInteger skippedExisting = new AtomicInteger();\n'
        '\t\tprivate final AtomicInteger protectedVanilla = new AtomicInteger();',
        'count protected chunks')

    # Enqueue filter guarantees excluded chunks never enter the rendering receiver.
    c[service]=once(c[service],
        '\t\tprivate void enqueueChunk(int chunkX, int chunkZ) {\n'
        '\t\t\tlong packed = ChunkPos.pack(chunkX, chunkZ);',
        '\t\tprivate void enqueueChunk(int chunkX, int chunkZ) {\n'
        '\t\t\tlong packed = ChunkPos.pack(chunkX, chunkZ);\n'
        '\t\t\tif (FunkyTerratonicZone.isProtected(level.dimension(), chunkX, chunkZ)) {\n'
        '\t\t\t\tif (isCovered(packed) && chunkStates.add(packed, CHUNK_STATE_FINISHED)) {\n'
        '\t\t\t\t\tprotectedVanilla.incrementAndGet();\n'
        '\t\t\t\t}\n'
        '\t\t\t\treturn;\n'
        '\t\t\t}',
        'region queue protected zone check')
    c[service]=first_of_two(c[service],
        '\t\tif (!forcedRetry && owner.receiver.hasData(owner.context.height, chunkX, chunkZ)) {',
        '\t\tif (FunkyTerratonicZone.isProtected(owner.level.dimension(), chunkX, chunkZ)) {\n'
        '\t\t\treturn true;\n'
        '\t\t}\n'
        '\t\tif (!forcedRetry && owner.receiver.hasData(owner.context.height, chunkX, chunkZ)) {',
        'check before generating or retrying')
    # Even if config toggles or a queued attempt races the final output, check again.
    c[service]=once(c[service],
        '\t\tLevelLightEngine lightEngine = owner.context.light(chunkX, chunkZ);\n'
        '\t\towner.receiver.receive(chunk, lightEngine);',
        '\t\tif (FunkyTerratonicZone.isProtected(owner.level.dimension(), chunkX, chunkZ)) {\n'
        '\t\t\treturn true;\n'
        '\t\t}\n'
        '\t\tLevelLightEngine lightEngine = owner.context.light(chunkX, chunkZ);\n'
        '\t\towner.receiver.receive(chunk, lightEngine);',
        'check again before insertion')

    c[service]=once(c[service],
        '\t\t\t\tcurrent.countState(CHUNK_STATE_FAILED));',
        '\t\t\t\tcurrent.countState(CHUNK_STATE_FAILED))\n'
        '\t\t\t\t.copy().append(Component.literal("\\nFunky: protected vanilla chunks skipped: "\n'
        '\t\t\t\t\t\t+ current.protectedVanilla.get()));',
        'display protected count')
    # Root cause of v1 error: block tags must be preloaded for worldgen codecs.
    c[service]=once(c[service],
        '\t\t\t\tRegistryAccess.Frozen loadingAccess =\n'
        '\t\t\t\t\t\tlayers.getAccessForLoading(RegistryLayer.WORLD);',
        '\t\t\t\tRegistryAccess.Frozen loadingAccess =\n'
        '\t\t\t\t\t\tlayers.getAccessForLoading(RegistryLayer.WORLD);',
        'worldgen registry access anchor')

    c[service]=once(c[service],
        '\t\t\t\ttry {\n'
        '\t\t\t\t\tRegistryAccess.Frozen worldRegistries =\n'
        '\t\t\t\t\t\t\tRegistryDataLoader.load(\n'
        '\t\t\t\t\t\t\t\t\t\t\tresources,\n'
        '\t\t\t\t\t\t\t\t\t\t\tloadingAccess.listRegistries().toList(),',
        '\t\t\t\ttry {\n'
        '\t\t\t\t\t// The static tags are required when loading vanilla & Terratonic worldgen.\n'
        '\t\t\t\t\t// v1 omitted this and failed on minecraft:cannot_place_basalt_pillar_on.\n'
        '\t\t\t\t\tvar pendingStaticTags = TagLoader.loadTagsForExistingRegistries(\n'
        '\t\t\t\t\t\t\tresources, layers.getLayer(RegistryLayer.STATIC));\n'
        '\t\t\t\t\tvar worldgenLookups = TagLoader.buildUpdatedLookups(\n'
        '\t\t\t\t\t\t\tloadingAccess, pendingStaticTags);\n'
        '\t\t\t\t\tRegistryAccess.Frozen worldRegistries =\n'
        '\t\t\t\t\t\t\tRegistryDataLoader.load(\n'
        '\t\t\t\t\t\t\t\t\t\t\tresources,\n'
        '\t\t\t\t\t\t\t\t\t\t\tworldgenLookups,',
        'load static block tags before world registries')

    c[gradle]=once(c[gradle], 'mod_version=1.2.10-funky-terratonic.1',
        'mod_version=1.2.10-funky-terratonic.2','v2 version')
    c[zone]=ZONE
    return c

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('seedgen_dir',type=Path)
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    root=args.seedgen_dir.resolve()
    files=changed(root)
    for path,content in files.items():
        print(('CHECK' if args.dry_run else 'WRITE'),path.relative_to(root))
        if not args.dry_run:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding='utf-8')
    print('v2 patch validated' if args.dry_run else 'v2 patch installed')
