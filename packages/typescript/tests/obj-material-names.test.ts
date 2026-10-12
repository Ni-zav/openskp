import { describe, expect, it } from 'vitest';
import { toMTL, toOBJ } from '../src/obj';
import type { SkpScene } from '../src/model';

describe('OBJ material name collisions', () => {
  it('generates unique, matching OBJ and MTL names without stealing reserved names', () => {
    const names = ['Wood/Oak', 'Wood_Oak', 'Wood_Oak_2'];
    const scene = {
      gltfMaterials: names.map(name => ({
        name, pbrMetallicRoughness: { baseColorFactor: [1, 0, 0, 1] },
      })),
      glbPrimitives: names.map((name, materialIndex) => ({
        geomName: name, materialIndex,
        positions: new Float32Array([0, 0, 0, 1, 0, 0, 0, 1, 0]),
        normals: new Float32Array(0), uvs: new Float32Array(0),
        indices: new Uint32Array([0, 1, 2]),
      })),
    } as SkpScene;
    const expected = ['Wood_Oak', 'Wood_Oak_2_1', 'Wood_Oak_2'];
    expect(toMTL(scene).split('\n').filter(s => s.startsWith('newmtl ')).map(s => s.slice(7))).toEqual(expected);
    expect(toOBJ(scene).split('\n').filter(s => s.startsWith('usemtl ')).map(s => s.slice(7))).toEqual(expected);
  });
});
