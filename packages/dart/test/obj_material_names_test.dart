import 'dart:typed_data';
import 'package:openskp/openskp.dart';
import 'package:test/test.dart';

void main() {
  test('OBJ and MTL use the same unique names after sanitization', () {
    final rawNames = ['Wood/Oak', 'Wood_Oak', 'Wood_Oak_2'];
    final scene = Scene(
      sceneHierarchy: InstanceNode(),
      meshIndex: {},
      glbPrimitives: [
        for (var i = 0; i < rawNames.length; i++)
          GlbPrimitive(
            geomName: 'part' + i.toString(),
            materialIndex: i,
            positions: Float32List.fromList([0, 0, 0, 1, 0, 0, 0, 1, 0]),
            normals: Float32List(0),
            uvs: Float32List(0),
            indices: Uint32List.fromList([0, 1, 2]),
          )
      ],
      gltfMaterials: [
        for (final name in rawNames)
          {'name': name, 'pbrMetallicRoughness': {'baseColorFactor': [1, 0, 0, 1]}}
      ],
    );
    final expected = ['Wood_Oak', 'Wood_Oak_2_1', 'Wood_Oak_2'];
    List<String> references(String text, String prefix) =>
        text.split('\n').where((line) => line.startsWith(prefix))
            .map((line) => line.substring(prefix.length)).toList();
    expect(references(toMtl(scene), 'newmtl '), expected);
    expect(references(toObj(scene), 'usemtl '), expected);
  });
}
