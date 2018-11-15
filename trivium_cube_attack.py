import logging
logging.basicConfig(level=logging.INFO)
import cube_attack
from trivium import Trivium
from blackboxpoly import BlackBoxPoly
from blackboxpoly import sum_mod2


class TriviumCubeAttack(cube_attack.CubeAttack):
    def __init__(self, n_rounds, action="verify"):
        super().__init__(degree=80)

        self.bbpoly = Trivium(n_rounds)
        # print ("hello : {}".format(self.bbpoly))
        self.action = action

