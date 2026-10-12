"""OBJ and MTL must agree on unique identifiers after name sanitization."""
from array import array

from openskp.export.obj import to_mtl, to_obj
from openskp.scene import GlbPrimitive, Scene


def test_sanitized_material_name_collisions_and_reserved_suffixes():
    names = ["Wood/Oak", "Wood_Oak", "Wood_Oak_2"]
    scene = Scene(
        gltf_materials=[
            {"name": name, "pbrMetallicRoughness": {"baseColorFactor": [1, 0, 0, 1]}}
            for name in names
        ],
        glb_primitives=[
            GlbPrimitive(
                geom_name=f"face{i}",
                material_index=i,
                positions=array("f", [0, 0, 0, 1, 0, 0, 0, 1, 0]),
                normals=array("f"),
                uvs=array("f"),
                indices=array("I", [0, 1, 2]),
            )
            for i in range(len(names))
        ],
    )
    expected = ["Wood_Oak", "Wood_Oak_2_1", "Wood_Oak_2"]
    mtl = to_mtl(scene)
    obj = to_obj(scene)
    assert [line[7:] for line in mtl.splitlines() if line.startswith("newmtl ")] == expected
    assert [line[7:] for line in obj.splitlines() if line.startswith("usemtl ")] == expected
