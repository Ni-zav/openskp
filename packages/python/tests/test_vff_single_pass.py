"""Regression coverage for the fused VFF metadata traversal (openskp#431)."""
import struct

from openskp._core import (
    CONTAINER_TAGS,
    _collect_vff_record,
    _find_page_node,
    _scan_instance_transforms,
    _scan_vertex_positions,
    parse_tlv_recursive,
)


def tlv(tag, payload=b''):
    return bytes.fromhex(tag) + struct.pack('<I', len(payload)) + payload


def entity_id(value):
    return tlv('DC05', b'\xde\x05' + struct.pack('<I', 1) + bytes([value]))


def test_single_pass_collects_vff_metadata_and_preserves_transform_walk():
    matrix = (1., 0., 0., 0., 1., 0., 0., 0., 1., 5., 6., 7., 1.)
    nested = tlv('6419', tlv('D007', entity_id(9)) +
                 tlv('6619', struct.pack('<13d', *matrix)))
    instance = tlv('6419', tlv('D007', entity_id(8)) +
                   tlv('6619', struct.pack('<13d', *matrix)) + nested)
    vertex = tlv('C409', entity_id(42) + tlv('C509', struct.pack('<3d', 1, 2, 3)))
    definition = tlv('7C15', entity_id(99) + tlv('7D15', bytes(range(16))) +
                     tlv('7E15', b'Wall') +
                     tlv('581B', tlv('5D1B', b'\x01') +
                         tlv('5E1B', b'\x00')) +
                     vertex + instance)
    layer = tlv('993A', tlv('8C3C', entity_id(5) +
                        tlv('8D3C', b'Furniture') + tlv('8E3C', b'\x01')))
    material = tlv('C832', entity_id(6) + tlv('CC32', b'Timber'))
    page = tlv('0702', b'')
    data = tlv('F701', layer + material + definition + page)
    root = parse_tlv_recursive(data, 0, len(data), CONTAINER_TAGS)[0]

    layers, hidden, materials, defs, vertices, transforms = {}, {}, {}, {}, {}, {}
    found_page = _collect_vff_record(
        root, layers, hidden, materials, defs, vertices, transforms, None)

    assert layers == {5: 'Furniture'}
    assert hidden == {'Furniture': True}
    assert materials == {6: 'Timber'}
    assert defs[99]['guid'] == bytes(range(16)).hex().upper()
    assert defs[99]['name'] == 'Wall'
    assert defs[99]['always_faces_camera'] is True
    assert defs[99]['shadows_face_sun'] is False
    assert defs[99]['builder'].vertices[42] == (1., 2., 3.)
    assert vertices == {'2a': (1., 2., 3.)}
    assert found_page is _find_page_node(root)

    reference_vertices, reference_transforms = {}, {}
    _scan_vertex_positions(root, reference_vertices)
    _scan_instance_transforms(root, reference_transforms)
    assert vertices == reference_vertices
    assert transforms == reference_transforms
    assert transforms['08'][9:12] == [5., 6., 7.]
    assert transforms['09'][9:12] == [10., 12., 14.]


def test_first_page_wins_and_no_hidden_flag_does_not_override_existing_value():
    page1 = tlv('0702', b'one')
    data1 = tlv('F701', tlv('993A', tlv('8C3C', entity_id(5) +
                                      tlv('8D3C', b'Layer0'))) + page1)
    data2 = tlv('F701', tlv('0702', b'two'))
    roots = [parse_tlv_recursive(d, 0, len(d), CONTAINER_TAGS)[0]
             for d in (data1, data2)]
    layers, hidden, materials, defs, vertices, transforms = {}, {'Layer0': True}, {}, {}, {}, {}
    page = None
    for root in roots:
        page = _collect_vff_record(
            root, layers, hidden, materials, defs, vertices, transforms, page)
    assert page is _find_page_node(roots[0])
    assert hidden == {'Layer0': True}
    assert layers == {5: 'Layer0'}
