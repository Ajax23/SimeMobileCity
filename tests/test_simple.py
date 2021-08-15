import os
import sys

import shutil
import unittest

import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt

import chargesim as cs


class UserModelCase(unittest.TestCase):
    #################
    # Remove Output #
    #################
    @classmethod
    def setUpClass(self):
        if os.path.isdir("tests"):
            os.chdir("tests")

        folder = 'output'
        cs.utils.mkdirp(folder)
        cs.utils.mkdirp(folder+"/temp")
        open(folder+"/temp.txt", 'a').close()

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        # Set style
        # sns.set_style("white",{"xtick.bottom": True,'ytick.left': True})
        # sns.set_context("paper")
        # sns.set_palette(sns.color_palette("deep"))


    #########
    # Utils #
    #########
    def test_utils(self):
        file_link = "output/test/test.txt"

        cs.utils.mkdirp("output/test")

        with open(file_link, "w") as file_out:
            file_out.write("TEST")
        cs.utils.copy(file_link, file_link+"t")
        cs.utils.replace(file_link+"t", "TEST", "DOTA")
        with open(file_link+"t", "r") as file_in:
            for line in file_in:
                self.assertEqual(line, "DOTA\n")

        self.assertEqual(cs.utils.column([[1, 1, 1], [2, 2, 2]]), [[1, 2], [1, 2], [1, 2]])

        cs.utils.save([1, 1, 1], file_link)
        self.assertEqual(cs.utils.load(file_link), [1, 1, 1])

        print()
        cs.utils.toc(cs.utils.tic(), message="Test", is_print=True)
        self.assertEqual(round(cs.utils.toc(cs.utils.tic(), is_print=True)), 0)


    ########
    # User #
    ########
    def test_user(self):
        # Initialize
        user = cs.User()

        # Ident
        user.set_ident("DOTA")
        self.assertEqual(user.get_ident(), "DOTA")

        # Probability
        user.set_p({day: {hour: 1/7 for hour in range(24)} for day in range(7)})
        user.set_p_day(0, {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1})
        self.assertEqual(user.get_p_day(0), {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1})
        user.set_p_hour(0, 0, 0.5)
        self.assertEqual(user.get_p_hour(0, 0), 0.5)
        self.assertEqual(user.get_p()[0][0], 0.5)


    #######
    # Car #
    #######
    def test_car(self):
        # Initialize
        car = cs.Car(100)

        # Ident
        car.set_ident("DOTA")
        self.assertEqual(car.get_ident(), "DOTA")

        # Size
        car.set_size(150)
        self.assertEqual(car.get_size(), 150)


    #######
    # Map #
    #######
    def test_map(self):
        # self.skipTest("Temporary")

        # Load
        name = "Munich, Bavaria, Germany"
        # name = "Piedmont, California, USA"
        # topo = cs.Map({"name": name}, tags={})
        # cs.utils.save(topo.get_G(), "data/munich_G.obj")
        # cs.utils.save(topo.get_Gp(), "data/munich_Gp.obj")

        G = cs.utils.load("data/munich_G.obj")
        Gp = cs.utils.load("data/munich_Gp.obj")
        topo = cs.Map({"name": name, "G": G, "Gp": Gp})
        self.assertEqual(list(topo.get_G())[0], 128236)
        self.assertEqual(list(topo.get_Gp())[0], 128236)
        self.assertEqual(topo.get_nodes()[0], 128236)

        # Poi
        P, _ = topo.poi("cafe", radius=0, is_gdf=True)
        P = topo.poi("cafe", radius=300)

        # Charging stations
        C, capacity = topo.charging_station()
        self.assertEqual(list(C)[0], 5156040713)
        self.assertEqual(capacity[1249710076], 4)

        # Distance
        route_len = topo.dist_poi(1955541, C, False)
        self.assertEqual(round(route_len, 2), 333.71)
        route_len, route = topo.dist_poi(1955541, C, True)

        # Plot
        topo.plot(pois=[P])
        plt.savefig("output/map_cafe.pdf", format="pdf", dpi=1000)

        topo.plot(routes=[route, route])
        topo.plot(routes=[route])
        topo.plot(pois=[C])
        plt.savefig("output/map_charge.pdf", format="pdf", dpi=1000)


    #######
    # Poi #
    #######
    def test_poi(self):
        # self.skipTest("Temporary")

        # Initialize
        name = "Munich, Bavaria, Germany"
        G = cs.utils.load("data/munich_G.obj")
        Gp = cs.utils.load("data/munich_Gp.obj")
        topo = cs.Map({"name": name, "G": G, "Gp": Gp})
        poi = cs.Poi(topo, "cafe")

        self.assertEqual(poi.get_map(), topo)
        self.assertEqual(poi.get_name(), "cafe")
        self.assertEqual(list(poi.get_G())[0], 4692207617)
        self.assertEqual(poi.get_nodes()[0], 4692207617)

        # Probability
        poi.set_p({day: {hour: 1/7 for hour in range(24)} for day in range(7)})
        poi.set_p_day(0, {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1})
        self.assertEqual(poi.get_p_day(0), {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1})
        poi.set_p_hour(0, 0, 0.5)
        self.assertEqual(poi.get_p_hour(0, 0), 0.5)
        self.assertEqual(poi.get_p()[0][0], 0.5)


    ######
    # MC #
    ######
    def test_mc(self):
        # self.skipTest("Temporary")

        name = "Munich, Bavaria, Germany"
        mc = cs.MC([cs.User()], {"name": name})


if __name__ == '__main__':
    unittest.main(verbosity=2)
