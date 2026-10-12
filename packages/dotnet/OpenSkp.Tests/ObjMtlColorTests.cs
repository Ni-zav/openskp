using System.Collections.Generic;
using OpenSkp;
using Xunit;

namespace OpenSkp.Tests
{
    public class ObjMtlColorTests
    {
        [Fact]
        public void ToMtl_UsesDoubleArrayFromSceneBuilder()
        {
            var scene = new Scene
            {
                GltfMaterials = new List<object>
                {
                    new Dictionary<string, object>
                    {
                        ["name"] = "RedGlass",
                        ["pbrMetallicRoughness"] = new Dictionary<string, object>
                        {
                            ["baseColorFactor"] = new double[] { 1.0, 0.0, 0.25, 0.5 }
                        }
                    }
                }
            };

            string mtl = ObjExport.ToMtl(scene);
            Assert.Contains("newmtl RedGlass", mtl);
            Assert.Contains("Kd 1.000000 0.000000 0.250000", mtl);
            Assert.Contains("d 0.500000", mtl);
        }

        [Fact]
        public void ToMtl_StillAcceptsFloatLists()
        {
            var scene = new Scene
            {
                GltfMaterials = new List<object>
                {
                    new Dictionary<string, object>
                    {
                        ["pbrMetallicRoughness"] = new Dictionary<string, object>
                        {
                            ["baseColorFactor"] = new List<float> { 0.0f, 1.0f, 0.0f, 1.0f }
                        }
                    }
                }
            };
            Assert.Contains("Kd 0.000000 1.000000 0.000000", ObjExport.ToMtl(scene));
        }
    }
}
