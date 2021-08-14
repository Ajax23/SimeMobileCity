import os
import sys

import shutil
import unittest

import pandas as pd
import seaborn as sns
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
        user = cs.User()

        # Ident
        user.set_ident("DOTA")
        self.assertEqual(user.get_ident(), "DOTA")

        # Probability
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

        name = "Munich, Bavaria, Germany"
        # name = "Piedmont, California, USA"
        # topo = cs.Map({"name": name}, tags={})
        # cs.utils.save(topo.get_G(), "data/munich_G.obj")
        # cs.utils.save(topo.get_Gp(), "data/munich_Gp.obj")

        G = cs.utils.load("data/munich_G.obj")
        Gp = cs.utils.load("data/munich_Gp.obj")
        topo = cs.Map({"name": name, "G": G, "Gp": Gp})

        route_len, route = topo.dist_charge(1955541, True)
        self.assertEqual(round(route_len, 2), 333.71)

        topo.plot(routes=[route, route], is_station=False)
        topo.plot(routes=[route], is_station=False)
        topo.plot(is_station=True)
        
        plt.savefig("output/map.pdf", format="pdf", dpi=1000)


if __name__ == '__main__':
    unittest.main(verbosity=2)
