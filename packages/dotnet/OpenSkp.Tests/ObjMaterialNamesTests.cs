using System;
using System.Collections.Generic;
using System.Linq;
using OpenSkp;
using Xunit;

namespace OpenSkp.Tests
{
    public class ObjMaterialNamesTests
    {
        [Fact]
        public void ObjAndMtlNamesStayUniqueAfterSanitizing()
        {
            string[] raw = { "Wood/Oak", "Wood_Oak", "Wood_Oak_2" };
            var scene = new Scene
            {
                GltfMaterials = raw.Select(name => (object)new Dictionary<string, object>
                {
                    ["name"] = name
                }).ToList(),
                GlbPrimitives = raw.Select((name, i) => new GlbPrimitive
                {
                    GeomName = name,
                    MaterialIndex = i,
                    Positions = new float[] { 0, 0, 0, 1, 0, 0, 0, 1, 0 },
                    Indices = new uint[] { 0, 1, 2 }
                }).ToList()
            };

            string[] expected = { "Wood_Oak", "Wood_Oak_2_1", "Wood_Oak_2" };
            string[] lines(string input, string prefix) =>
                input.Split('\n').Where(line => line.StartsWith(prefix, StringComparison.Ordinal))
                    .Select(line => line.Substring(prefix.Length)).ToArray();
            Assert.Equal(expected, lines(ObjExport.ToMtl(scene), "newmtl "));
            Assert.Equal(expected, lines(ObjExport.ToObj(scene), "usemtl "));
        }
    }
}
