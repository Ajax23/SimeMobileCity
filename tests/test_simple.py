import os
import sys

import shutil
import unittest

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

        # Distance
        route_len = topo.dist_charge(1955541, False)
        self.assertEqual(round(route_len, 2), 333.71)
        route_len, route = topo.dist_charge(1955541, True)

        # Plot
        topo.plot(routes=[route, route], is_station=False)
        topo.plot(routes=[route], is_station=False)
        topo.plot(is_station=True)
        plt.savefig("output/map.pdf", format="pdf", dpi=1000)

        # Getter
        self.assertEqual(list(topo.get_G())[0], 128236)
        self.assertEqual(list(topo.get_Gp())[0], 128236)
        self.assertEqual(list(topo.get_station())[0], 5156040713)
        self.assertEqual(topo.get_capacity()[1249710076], 4)
        self.assertEqual(topo.get_nodes()[0], 128236)


    ######
    # MC #
    ######
    def test_mc(self):
        # self.skipTest("Temporary")

        name = "Munich, Bavaria, Germany"
        mc = cs.MC([cs.User()], {"name": name})


if __name__ == '__main__':
    unittest.main(verbosity=2)
