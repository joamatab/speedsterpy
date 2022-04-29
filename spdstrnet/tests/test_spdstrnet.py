import unittest
import sys
import gdstk
import numpy as np
from loguru import logger
from spdstrnet import (
    check_point_inside_polygon,
    check_polygon_overlap,
    check_polygon_overlap,
    bool_polygon_overlap_check,
    get_common_edges,
    check_neighbour_polygons,
    check_same_polygon,
    check_polygon_contains_polygon,
)


class TestGeometry(unittest.TestCase):
    ld = {"met1": {"layer": 1, "datatype": 0}, "met2": {"layer": 2, "datatype": 0}}

    def test_check_point_inside_polygon(self):
        point = [0.3, 0.3]
        point2 = [3.1, 3.1]
        poly = gdstk.rectangle((0.0, 0.0), (3.0, 1.0), **self.ld["met1"])
        self.assertTrue(check_point_inside_polygon(poly, point))
        self.assertFalse(check_point_inside_polygon(poly, point2))

    def test_check_polygon_overlap(self):
        poly = gdstk.rectangle((0.0, 0.0), (3.0, 1.0), **self.ld["met1"])
        poly2 = gdstk.rectangle((0.0, 0.0), (1.0, 3.0), **self.ld["met1"])
        poly3 = gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met2"])
        poly4 = gdstk.rectangle((1.0, 0.0), (2.0, 1.0), **self.ld["met2"])

        self.assertIsNotNone(check_polygon_overlap(poly, poly2))
        self.assertIsNotNone(check_polygon_overlap(poly, poly3))
        self.assertIsNone(check_polygon_overlap(poly3, poly4))
        self.assertIsNone(check_polygon_overlap(poly2, poly4))

    def test_bool_polygon_overlap_check(self):
        poly = gdstk.rectangle((0.0, 0.0), (3.0, 1.0), **self.ld["met1"])
        poly2 = gdstk.rectangle((0.0, 0.0), (1.0, 3.0), **self.ld["met1"])
        poly3 = gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met2"])
        poly4 = gdstk.rectangle((1.0, 0.0), (2.0, 1.0), **self.ld["met2"])

        self.assertTrue(bool_polygon_overlap_check(poly, poly2))
        self.assertTrue(bool_polygon_overlap_check(poly, poly3))
        self.assertFalse(bool_polygon_overlap_check(poly3, poly4))
        self.assertFalse(bool_polygon_overlap_check(poly2, poly4))

    def test_get_common_edges(self):
        poly = gdstk.rectangle((0.0, 0.0), (3.0, 1.0), **self.ld["met1"])
        poly2 = gdstk.rectangle((0.0, 0.0), (1.0, 3.0), **self.ld["met1"])
        poly3 = gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met2"])
        poly4 = gdstk.rectangle((1.0, 0.0), (2.0, 1.0), **self.ld["met2"])
        poly5 = gdstk.rectangle((2.0, 0.0), (4.0, 4.0), **self.ld["met1"])
        edges = {
            "t1": [[(0.0, 0.0), (1.0, 0.0)], [(0.0, 1.0), (0.0, 0.0)]],
            "t2": [
                [(1.0, 1.0), (1.0, 0.0)],
            ],
        }
        self.assertIsNotNone(get_common_edges(poly, poly2))
        self.assertEqual(get_common_edges(poly, poly2)[0], edges["t1"][0])
        self.assertIsNotNone(get_common_edges(poly3, poly4))
        self.assertEqual(get_common_edges(poly3, poly4)[0], edges["t2"][0])
        self.assertIsNone(get_common_edges(poly3, poly5))
        self.assertIsNotNone(get_common_edges(poly, poly5))

    def test_check_neighbour_polygon(self):
        poly = gdstk.rectangle((0.0, 0.0), (3.0, 1.0), **self.ld["met1"])
        poly2 = gdstk.rectangle((0.0, 0.0), (1.0, 3.0), **self.ld["met1"])
        poly3 = gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met2"])
        poly4 = gdstk.rectangle((1.0, 0.0), (2.0, 1.0), **self.ld["met2"])
        poly5 = gdstk.rectangle((2.0, 0.0), (4.0, 4.0), **self.ld["met1"])
        self.assertFalse(check_neighbour_polygons(poly, poly2))
        self.assertTrue(check_neighbour_polygons(poly3, poly4))
        self.assertFalse(check_neighbour_polygons(poly4, poly5))
        self.assertFalse(check_neighbour_polygons(poly2, poly4))

    def test_check_same_polygon(self):
        points = [(0, 0), (1, 0), (1, 1), (0, 1)]
        tests = {
            "t1": [
                gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met1"]),
                gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met1"]),
            ],
            "t2": [
                gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met1"]),
                gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met2"]),
            ],
            "t3": [
                gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met2"]),
                gdstk.rectangle((0.0, 0.0), (3.0, 1.0), **self.ld["met2"]),
            ],
            "t4": [
                gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met2"]),
                gdstk.Polygon(points, **self.ld["met2"]),
            ],
            "t5": [
                gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met2"]),
                gdstk.Polygon(points, **self.ld["met1"]),
            ],
        }
        self.assertTrue(check_same_polygon(tests["t1"][0], tests["t1"][1]))
        self.assertFalse(check_same_polygon(tests["t2"][0], tests["t2"][1]))
        self.assertFalse(check_same_polygon(tests["t3"][0], tests["t3"][1]))
        self.assertTrue(check_same_polygon(tests["t4"][0], tests["t4"][1]))
        self.assertFalse(check_same_polygon(tests["t5"][0], tests["t5"][1]))

    def test_check_polygon_contains_polygon(self):
        points = [(0, 0), (1, 0), (1, 1), (0, 1)]
        tests = {
            "t1": [
                gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met1"]),
                gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met1"]),
            ],
            "t2": [
                gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met1"]),
                gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met2"]),
            ],
            "t3": [
                gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met2"]),
                gdstk.rectangle((0.0, 0.0), (3.0, 1.0), **self.ld["met2"]),
            ],
            "t4": [
                gdstk.rectangle((0.0, 0.0), (4.0, 4.0), **self.ld["met2"]),
                gdstk.rectangle((1.0, 1.0), (3.0, 3.0), **self.ld["met2"]),
            ],
            "t5": [
                gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met2"]),
                gdstk.rectangle((1.0, 1.0), (3.0, 3.0), **self.ld["met2"]),
            ],
        }
        self.assertTrue(check_polygon_contains_polygon(tests["t1"][0], tests["t1"][1]))
        self.assertTrue(check_polygon_contains_polygon(tests["t1"][1], tests["t1"][0]))
        self.assertFalse(check_polygon_contains_polygon(tests["t2"][0], tests["t2"][1]))
        self.assertFalse(check_polygon_contains_polygon(tests["t3"][0], tests["t3"][1]))
        self.assertTrue(check_polygon_contains_polygon(tests["t3"][1], tests["t3"][0]))
        self.assertTrue(check_polygon_contains_polygon(tests["t4"][0], tests["t4"][1]))
        self.assertFalse(check_polygon_contains_polygon(tests["t5"][0], tests["t5"][1]))
        self.assertFalse(check_polygon_contains_polygon(tests["t5"][1], tests["t5"][0]))

    def test_find_centroid(self):
        polys = [
            gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met1"]),
            gdstk.rectangle((0.0, 0.0), (1.0, 1.0), **self.ld["met1"]),
            gdstk.Polygon([(0, 0), (1, 0), (1, 1)]),
            gdstk.Polygon([(0, 0), (1, 0), (2, 1), (1, 3), (0, 3), (-1, 2)]),
        ]

    def test_unit_vec(self):
        pass

    def test_saturate_vector(self):
        pass

    def test_check_neighbour_direction(self):
        pass

    def test_get_direction_between_rects(self):
        pass

    def test_fragment_polygon(self):
        pass

    def test_fragment_net(self):
        pass

    def test_get_polygons_by_spec(self):
        pass

    def test_get_polygons_dict(self):
        pass

    def test_check_polygon_in_cell(self):
        pass

    def test_check_via_connection(self):
        pass

    def test_join_overlapping_polygons_cell(self):
        pass

    def test_fuse_overlapping_cells(self):
        pass

    def test_select_abstraction_depth(self):
        pass

    def test_add_port(self):
        pass


if __name__ == "__main__":
    unittest.main()
