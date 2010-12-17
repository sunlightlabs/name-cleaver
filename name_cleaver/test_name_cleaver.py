from name_cleaver import PoliticianNameCleaver
from nose.plugins.skip import Skip, SkipTest
import unittest

class TestPoliticianNameCleaver(unittest.TestCase):

    def test_case_converts_in_non_mixed_case_names_only(self):
        self.assertEqual('Antonio dAlesio', str(PoliticianNameCleaver('Antonio dAlesio').parse()))

    def test_upper_case_scot_with_party(self):
        self.assertEqual('Emory MacDonald', str(PoliticianNameCleaver('MACDONALD, EMORY (R)').parse()))

    def test_last_first_mixed_case_scot_with_party(self):
        self.assertEqual('Emory MacDonald', str(PoliticianNameCleaver('MacDonald, Emory (R)').parse()))

    def test_first_last_mixed_case_with_party(self):
        self.assertEqual('Nancy Pelosi', str(PoliticianNameCleaver('Nancy Pelosi (D)').parse()))

    def test_not_everything_is_a_scot(self):
        self.assertEqual('Adam Mack', str(PoliticianNameCleaver('ADAM MACK').parse()))
        self.assertEqual('Don Womackey', str(PoliticianNameCleaver('DON WOMACKEY').parse()))

    def test_last_first(self):
        self.assertEqual('Albert Gore', str(PoliticianNameCleaver('Gore, Albert').parse()))

    def test_pile_it_on(self):
        self.assertEqual('Milton Elmer McCullough Jr', str(PoliticianNameCleaver('Milton Elmer "Mac" McCullough, Jr (3)').parse()))

    def test_pile_it_on_two(self):
        self.assertEqual('William Steve Southerland II', str(PoliticianNameCleaver('William Steve Southerland  II (R)').parse()))

    def test_pile_it_on_three(self):
        self.assertEqual('Edward Thomas O\'Donnell Jr', str(PoliticianNameCleaver('Edward Thomas O\'Donnell, Jr (D)').parse()))

    def test_standardize_running_mate_names(self):
        self.assertEqual('John Kasich & Mary Taylor', str(PoliticianNameCleaver('Kasich, John & Taylor, Mary').parse()))

    def test_we_dont_need_no_steeenking_nicknames(self):
        self.assertEqual('Robert M McDonnell', str(PoliticianNameCleaver('McDonnell, Robert M (Bob)').parse()))
        self.assertEqual('John J Duncan Jr', str(PoliticianNameCleaver('John J (Jimmy) Duncan Jr (R)').parse()))
        self.assertEqual('Christopher Bond', str(PoliticianNameCleaver('Christopher "Kit" Bond').parse()))

    def test_capitalize_roman_numeral_suffixes(self):
        self.assertEqual('Ken Cuccinelli II', str(PoliticianNameCleaver('KEN CUCCINELLI II').parse()))
        self.assertEqual('Ken Cuccinelli II', str(PoliticianNameCleaver('CUCCINELLI II, KEN').parse()))
        self.assertEqual('Ken Cuccinelli IV', str(PoliticianNameCleaver('CUCCINELLI IV, KEN').parse()))
        self.assertEqual('Ken Cuccinelli IX', str(PoliticianNameCleaver('CUCCINELLI IX, KEN').parse()))

    def test_name_with_two_part_last_name(self):
        self.assertEqual('La Mere', PoliticianNameCleaver('Albert J La Mere').parse().last)
        self.assertEqual('Di Souza', PoliticianNameCleaver('Dinesh Di Souza').parse().last)

    def deals_with_last_names_that_look_like_two_part_but_are_not(self):
        name = PoliticianNameCleaver('Quoc Van (D)').parse()
        self.assertEqual('Quoc', name.first)
        self.assertEqual('Van', name.last)

    def test_doesnt_misinterpret_roman_numeral_characters_in_last_name_as_suffix(self):
        self.assertEqual('Vickers', PoliticianNameCleaver('Audrey C Vickers').parse().last)

    def test_multiple_middle_names(self):
        self.assertEqual('Swift Eagle', PoliticianNameCleaver('Alexander Swift Eagle Justice').parse().middle)

    def test_edgar_de_lisle_ross(self):
        name = PoliticianNameCleaver('Edgar de L\'Isle Ross (R)').parse()
        self.assertEqual('Edgar', name.first)
        self.assertEqual('de L\'Isle', name.middle)
        self.assertEqual('Ross', name.last)
        self.assertEqual(None, name.suffix)

    def test_with_metadata(self):
        self.assertEqual('Charles Schumer (D-NY)', str(PoliticianNameCleaver('Charles Schumer').parse().plus_metadata('D', 'NY')))
        self.assertEqual('Barack Obama (D)', str(PoliticianNameCleaver('Barack Obama').parse().plus_metadata('D', '')))
        self.assertEqual('Charles Schumer (NY)', str(PoliticianNameCleaver('Charles Schumer').parse().plus_metadata('', 'NY')))
        self.assertEqual('Jerry Leon Carroll', str(PoliticianNameCleaver('Jerry Leon Carroll').parse().plus_metadata('', ''))) # only this one guy is missing both at the moment

    def test_running_mates_with_metadata(self):
        self.assertEqual('Ted Strickland & Lee Fischer (D-OH)', str(PoliticianNameCleaver('STRICKLAND, TED & FISCHER, LEE').parse().plus_metadata('D', 'OH')))

