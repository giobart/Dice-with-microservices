import random as rnd
import unittest

from monolith.classes.DiceSet import DiceSet, Die, InvalidDiceSet
from monolith.utility.diceutils import RESOURCES_DIR, get_die_faces_list


class TestDie(unittest.TestCase):

    def test_create_dice_set_with_size(self):
        diceset = DiceSet('standard', 6)
        thrown = diceset.throw_dice()
        self.assertEqual(len(thrown), 6)

    # test for each die if the given face was in the list of all possible
    # faces for that die #
    def test_correct_dices_thrown(self):
        diceset = DiceSet('standard', 6)
        thrown = diceset.throw_dice()
        for i in range(6):
            face_list = get_die_faces_list("standard", i)
            self.assertTrue(thrown[i] in face_list)

    def test_dice_set_not_exists_fail(self):
        self.assertRaises(InvalidDiceSet, DiceSet, 'LukeImYourFather', 6)

    def test_die_init(self):
        die = Die(RESOURCES_DIR + '/diceset/standard/die0.txt')
        check = ['bike', 'moonandstars', 'bag', 'bird', 'crying', 'angry']
        self.assertEqual(die.faces, check)

    def test_die_pip(self):
        rnd.seed(574891)
        die = Die(RESOURCES_DIR + '/diceset/standard/die0.txt')
        res = die.throw_die()
        self.assertEqual(res, 'bag')