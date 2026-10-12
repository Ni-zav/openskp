#include "openskp/obj_export.hpp"

#include <gtest/gtest.h>

#include <string>
#include <utility>
#include <vector>

namespace openskp {
namespace {

TEST(ObjExport, SanitizedMaterialNamesDoNotCollide) {
  Scene scene;
  scene.gltf_materials.resize(3);
  scene.gltf_materials[0].name = "Wood/Oak";
  scene.gltf_materials[1].name = "Wood_Oak";
  scene.gltf_materials[2].name = "Wood_Oak_2";
  for (int i = 0; i < 3; ++i) {
    GlbPrimitive prim;
    prim.material_index = i;
    prim.positions = {0, 0, 0, 1, 0, 0, 0, 1, 0};
    prim.indices = {0, 1, 2};
    scene.glb_primitives.push_back(std::move(prim));
  }

  const auto mtl = to_mtl(scene);
  const auto obj = to_obj(scene);
  const std::vector<std::string> expected = {"Wood_Oak", "Wood_Oak_2_1", "Wood_Oak_2"};
  for (const auto& name : expected) {
    EXPECT_NE(mtl.find("newmtl " + name + "\n"), std::string::npos);
    EXPECT_NE(obj.find("usemtl " + name + "\n"), std::string::npos);
  }
  // Colliding names may never share a material identifier.
  EXPECT_EQ(mtl.find("newmtl Wood_Oak\n"), mtl.rfind("newmtl Wood_Oak\n"));
}

}  // namespace
}  // namespace openskp
