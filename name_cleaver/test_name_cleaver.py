from cleaver import PoliticianNameCleaver, OrganizationNameCleaver, \
        IndividualNameCleaver, UnparseableNameException

try:
    import unittest2 as unittest
except ImportError:
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
        self.assertEqual('Milton Elmer McCullough, Jr.', str(PoliticianNameCleaver('Milton Elmer "Mac" McCullough, Jr (3)').parse()))

    def test_pile_it_on_two(self):
        self.assertEqual('William Steve Southerland, II', str(PoliticianNameCleaver('William Steve Southerland  II (R)').parse()))

    def test_pile_it_on_three(self):
        self.assertEqual('Edward Thomas O\'Donnell, Jr.', str(PoliticianNameCleaver('Edward Thomas O\'Donnell, Jr (D)').parse()))

    def test_standardize_running_mate_names(self):
        self.assertEqual('John Kasich & Mary Taylor', str(PoliticianNameCleaver('Kasich, John & Taylor, Mary').parse()))

    def test_standardize_running_mate_names_with_slash(self):
        self.assertEqual('Mitt Romney & Paul D. Ryan', str(PoliticianNameCleaver('ROMNEY, MITT / RYAN, PAUL D.').parse()))

    def test_we_dont_need_no_steeenking_nicknames(self):
        self.assertEqual('Robert M. McDonnell', str(PoliticianNameCleaver('McDonnell, Robert M (Bob)').parse()))
        self.assertEqual('John J. Duncan, Jr.', str(PoliticianNameCleaver('John J (Jimmy) Duncan Jr (R)').parse()))
        self.assertEqual('Christopher Bond', str(PoliticianNameCleaver('Christopher "Kit" Bond').parse()))

    def test_capitalize_roman_numeral_suffixes(self):
        self.assertEqual('Ken Cuccinelli, II', str(PoliticianNameCleaver('KEN CUCCINELLI II').parse()))
        self.assertEqual('Ken Cuccinelli, II', str(PoliticianNameCleaver('CUCCINELLI II, KEN').parse()))
        self.assertEqual('Ken T. Cuccinelli, II', str(PoliticianNameCleaver('CUCCINELLI II, KEN T').parse()))
        self.assertEqual('Ken T. Cuccinelli, II', str(PoliticianNameCleaver('CUCCINELLI, KEN T II').parse()))
        self.assertEqual('Ken Cuccinelli, IV', str(PoliticianNameCleaver('CUCCINELLI IV, KEN').parse()))
        self.assertEqual('Ken Cuccinelli, IX', str(PoliticianNameCleaver('CUCCINELLI IX, KEN').parse()))

    def test_name_with_two_part_last_name(self):
        self.assertEqual('La Mere', PoliticianNameCleaver('Albert J La Mere').parse().last)
        self.assertEqual('Di Souza', PoliticianNameCleaver('Dinesh Di Souza').parse().last)

    def test_deals_with_last_names_that_look_like_two_part_but_are_not(self):
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
        self.assertEqual('Jerry Leon Carroll', str(PoliticianNameCleaver('Jerry Leon Carroll').parse().plus_metadata('', '')))  # only this one guy is missing both at the moment

    def test_running_mates_with_metadata(self):
        self.assertEqual('Ted Strickland & Lee Fischer (D-OH)', str(PoliticianNameCleaver('STRICKLAND, TED & FISCHER, LEE').parse().plus_metadata('D', 'OH')))

    def test_names_with_weird_parenthetical_stuff(self):
        self.assertEqual('Lynn Swann', str(PoliticianNameCleaver('SWANN, LYNN (COMMITTEE 1)').parse()))

    def test_handles_empty_names(self):
        self.assertEqual('', str(PoliticianNameCleaver('').parse()))

    def test_capitalize_irish_names(self):
        self.assertEqual('Sean O\'Leary', str(PoliticianNameCleaver('SEAN O\'LEARY').parse()))

    def test_primary_name_parts(self):
        self.assertEqual(['Robert', 'Geoff', 'Smith'], PoliticianNameCleaver('Smith, Robert Geoff').parse().primary_name_parts(include_middle=True))
        self.assertEqual(['Robert', 'Smith'], PoliticianNameCleaver('Smith, Robert Geoff').parse().primary_name_parts())

    def test_van_is_valid_first_name(self):
        self.assertEqual(['Van', 'Morrison'], PoliticianNameCleaver('Van Morrison').parse().primary_name_parts())

    def test_alternate_running_mates_format(self):
        self.assertEqual('Obama/Biden 2012', str(PoliticianNameCleaver('2012, Obama/Biden').parse()))

    def test_alternate_punctuation(self):
        self.assertEqual('Charles W. Boustany, Jr.', str(PoliticianNameCleaver('Charles W. Boustany Jr.').parse()))


class TestOrganizationNameCleaver(unittest.TestCase):

    def test_capitalize_pac(self):
        self.assertEqual('Nancy Pelosi Leadership PAC', str(OrganizationNameCleaver('NANCY PELOSI LEADERSHIP PAC').parse()))

    def test_make_single_word_names_ending_in_pac_all_uppercase(self):
        self.assertEqual('ECEPAC', str(OrganizationNameCleaver('ECEPAC').parse()))

    def test_names_starting_with_PAC(self):
        self.assertEqual('PAC For Engineers', str(OrganizationNameCleaver('PAC FOR ENGINEERS').parse()))
        self.assertEqual('PAC 102', str(OrganizationNameCleaver('PAC 102').parse()))

    def test_doesnt_bother_names_containing_string_pac(self):
        self.assertEqual('Pacific Trust', str(OrganizationNameCleaver('PACIFIC TRUST').parse()))

    def test_capitalize_scottish_names(self):
        self.assertEqual('McDonnell Douglas', str(OrganizationNameCleaver('MCDONNELL DOUGLAS').parse()))
        self.assertEqual('MacDonnell Douglas', str(OrganizationNameCleaver('MACDONNELL DOUGLAS').parse()))

    def test_dont_capitalize_just_anything_starting_with_mac(self):
        self.assertEqual('Machinists/Aerospace Workers Union', str(OrganizationNameCleaver('MACHINISTS/AEROSPACE WORKERS UNION').parse()))

    def test_expand(self):
        self.assertEqual('Raytheon Corporation', OrganizationNameCleaver('Raytheon Corp.').parse().expand())
        self.assertEqual('Massachusetts Institute of Technology', OrganizationNameCleaver('Massachusetts Inst. of Technology').parse().expand())

    def test_expand_with_two_tokens_to_expand(self):
        self.assertEqual('Merck & Company Incorporated', OrganizationNameCleaver('Merck & Co., Inc.').parse().expand())

    def test_dont_strip_after_hyphens_too_soon_in_a_name(self):
        self.assertEqual('US-Russia Business Council', OrganizationNameCleaver('US-Russia Business Council').parse().kernel())
        self.assertEqual('Wal-Mart Stores', OrganizationNameCleaver('Wal-Mart Stores, Inc.').parse().kernel())

    def test_strip_hyphens_more_than_three_characters_into_a_name(self):
        # This is not ideal for this name, but we can't get the best for all cases
        self.assertEqual('F Hoffmann', OrganizationNameCleaver('F. HOFFMANN-LA ROCHE LTD and its Affiliates').parse().kernel())

    def test_kernel(self):
        """
        Intended to get only the unique/meaningful words out of a name
        """
        self.assertEqual('Massachusetts Technology', OrganizationNameCleaver('Massachusetts Inst. of Technology').parse().kernel())
        self.assertEqual('Massachusetts Technology', OrganizationNameCleaver('Massachusetts Institute of Technology').parse().kernel())

        self.assertEqual('Walsh', OrganizationNameCleaver('The Walsh Group').parse().kernel())

        self.assertEqual('Health Net', OrganizationNameCleaver('Health Net Inc').parse().kernel())
        self.assertEqual('Health Net', OrganizationNameCleaver('Health Net, Inc.').parse().kernel())

        self.assertEqual('Distilled Spirits Council', OrganizationNameCleaver('Distilled Spirits Council of the U.S., Inc.').parse().kernel())

    def test_handles_empty_names(self):
        self.assertEqual('', str(OrganizationNameCleaver('').parse()))


class TestIndividualNameCleaver(unittest.TestCase):
    cleaver = IndividualNameCleaver

    def cleave_to_str(self, name_input):
        return str(self.cleaver(name_input).parse())

    def test_allow_names_to_have_only_last_name(self):
        self.assertEqual('Lee', self.cleave_to_str('LEE'))

    def test_all_kinds_of_crazy(self):
        self.assertEqual('Stanford Z. Rothschild', self.cleave_to_str('ROTHSCHILD 212, STANFORD Z MR'))

    def test_jr_and_the_like_end_up_at_the_end(self):
        self.assertEqual('Frederick A. "Tripp" Baird, III', self.cleave_to_str('Baird, Frederick A "Tripp" III'))

    def test_nicknames_suffixes_and_honorifics(self):
        self.assertEqual('Frederick A. "Tripp" Baird, III', self.cleave_to_str('Baird, Frederick A "Tripp" III Mr'))
        self.assertEqual('Frederick A. "Tripp" Baird, III', self.cleave_to_str('Baird, Mr Frederick A "Tripp" III'))

    def test_throw_out_mr(self):
        self.assertEqual('T. Boone Pickens', self.cleave_to_str('Mr T Boone Pickens'))
        self.assertEqual('T. Boone Pickens', self.cleave_to_str('Mr. T Boone Pickens'))
        self.assertEqual('T. Boone Pickens', self.cleave_to_str('Pickens, T Boone Mr'))
        self.assertEqual('John L. Nau', self.cleave_to_str(' MR JOHN L NAU,'))

    def test_keep_the_mrs(self):
        self.assertEqual('Mrs. T. Boone Pickens', self.cleave_to_str('Mrs T Boone Pickens'))
        self.assertEqual('Mrs. T. Boone Pickens', self.cleave_to_str('Mrs. T Boone Pickens'))
        self.assertEqual('Mrs. Stanford Z. Rothschild', self.cleave_to_str('ROTHSCHILD 212, STANFORD Z MRS'))

    def test_mrs_walton(self):
        self.assertEqual('Mrs. Jim Walton', self.cleave_to_str('WALTON, JIM MRS'))

    def test_capitalize_roman_numeral_suffixes(self):
        self.assertEqual('Ken Cuccinelli, II', self.cleave_to_str('KEN CUCCINELLI II'))
        self.assertEqual('Ken Cuccinelli, II', self.cleave_to_str('CUCCINELLI II, KEN'))
        self.assertEqual('Ken Cuccinelli, IV', self.cleave_to_str('CUCCINELLI IV, KEN'))
        self.assertEqual('Ken Cuccinelli, IX', self.cleave_to_str('CUCCINELLI IX, KEN'))

    def test_capitalize_scottish_last_names(self):
        self.assertEqual('Ronald McDonald', self.cleave_to_str('RONALD MCDONALD'))
        self.assertEqual('Old MacDonald', self.cleave_to_str('OLD MACDONALD'))

    def test_capitalizes_and_punctuates_initials(self):
        self.assertEqual('B.L. Schwartz', self.cleave_to_str('SCHWARTZ, BL'))

    def test_capitalizes_initials_but_not_honorifics(self):
        self.assertEqual('John Koza', self.cleave_to_str('KOZA, DR JOHN'))

    def test_doesnt_overzealously_detect_doctors(self):
        self.assertEqual('Drew Maloney', self.cleave_to_str('Maloney, Drew'))

    def test_unfazed_by_weird_cop_cont_parenthetical_phrases(self):
        self.assertEqual('Jacqueline A. Schmitz', self.cleave_to_str('SCHMITZ (COP CONT ), JACQUELINE A'))
        self.assertEqual('Hannah Mellman', self.cleave_to_str('MELLMAN (CONT\'D), HANNAH (CONT\'D)'))
        self.assertEqual('Tod Preston', self.cleave_to_str('PRESTON (C O P CONT\'D ), TOD'))

    def test_mr_and_mrs(self):
        self.assertEqual('Kenneth L. Lay', self.cleave_to_str('LAY, KENNETH L MR & MRS'))

    def test_primary_name_parts(self):
        self.assertEqual(['Robert', 'Geoff', 'Smith'], self.cleaver('Smith, Robert Geoff').parse().primary_name_parts(include_middle=True))
        self.assertEqual(['Robert', 'Smith'], self.cleaver('Smith, Robert Geoff').parse().primary_name_parts())

    def test_initialed_first_name(self):
        self.assertEqual('C. Richard Bonebrake', self.cleave_to_str('C. RICHARD BONEBRAKE'))

    def test_degree_gets_thrown_out(self):
        self.assertEqual('C. Richard Bonebrake', self.cleave_to_str('C. RICHARD BONEBRAKE, M.D.'))
        self.assertEqual('John W. Noble, Jr.', self.cleave_to_str('NOBLE JR., JOHN W. MD'))
        self.assertEqual('John W. Noble, Jr.', self.cleave_to_str('NOBLE JR., JOHN W. PHD MD'))
        self.assertEqual('Barney Dinosaur', self.cleave_to_str('DINOSAUR, BARNEY J.D.'))

    def test_two_part_names_skip_suffix_check(self):
        self.assertEqual('Vi Simpson', self.cleave_to_str('SIMPSON, VI'))
        self.assertEqual('J.R. Reskovac', self.cleave_to_str('RESKOVAC, JR'))


class TestCapitalization(unittest.TestCase):

    def test_overrides_dumb_python_titlecasing_for_apostrophes(self):
        self.assertEqual('Phoenix Women\'s Health Center', str(OrganizationNameCleaver('PHOENIX WOMEN\'S HEALTH CENTER').parse()))


class TestOrganizationNameCleaverForIndustries(unittest.TestCase):

    def test_capitalizes_letter_after_slash(self):
        self.assertEqual('Health Services/Hmos', str(OrganizationNameCleaver('HEALTH SERVICES/HMOS').parse()))
        self.assertEqual('Lawyers/Law Firms', str(OrganizationNameCleaver('LAWYERS/LAW FIRMS').parse()))

    def test_capitalizes_letter_after_hyphen(self):
        self.assertEqual('Non-Profit Institutions', str(OrganizationNameCleaver('NON-PROFIT INSTITUTIONS').parse()))
        self.assertEqual('Pro-Israel', str(OrganizationNameCleaver('PRO-ISRAEL').parse()))


class TestUnicode(unittest.TestCase):

    def test_individual(self):
        self.assertEqual(u'Tobias F\u00fcnke'.encode('utf-8'),
                str(IndividualNameCleaver(u'F\u00fcnke, Tobias').parse()))

    def test_politician(self):
        self.assertEqual(u'Tobias F\u00fcnke'.encode('utf-8'),
                str(PoliticianNameCleaver(u'F\u00fcnke, Tobias').parse()))

    def test_politician_plus_metadata(self):
        self.assertEqual(u'Tobias F\u00fcnke (D-CA)'.encode('utf-8'),
                str(PoliticianNameCleaver(u'F\u00fcnke, Tobias').parse().plus_metadata('D', 'CA')))

    def test_politician_running_mates(self):
        self.assertEqual(u'Tobias F\u00fcnke & Lindsay F\u00fcnke'.encode('utf-8'),
                str(PoliticianNameCleaver(u'F\u00fcnke, Tobias & F\u00fcnke, Lindsay').parse()))

    def test_running_mates_with_metadata(self):
        self.assertEqual(u'Ted Strickland & Le\u00e9 Fischer (D-OH)'.encode('utf-8'),
                str(PoliticianNameCleaver(u'STRICKLAND, TED & FISCHER, LE\u00c9').parse().plus_metadata('D', 'OH')))

    def test_organization(self):
        self.assertEqual(u'\u00C6tna, Inc.'.encode('utf-8'),
                str(OrganizationNameCleaver(u'\u00C6tna, Inc.').parse()))


class TestErrors(unittest.TestCase):

    def test_unparseable_politician_name(self):
        with self.assertRaises(UnparseableNameException):
            PoliticianNameCleaver("mr & mrs").parse()

    def test_unparseable_individual_name(self):
        with self.assertRaises(UnparseableNameException):
            IndividualNameCleaver("mr & mrs").parse()

    # this ought to have a test, but I'm not sure how to break this one.
    #def test_unparseable_organization_name(self):
    #    with self.assertRaises(UnparseableNameException):
    #        OrganizationNameCleaver("####!!!").parse()

    def test_parse_safe__individual(self):
        pass
        #with self.assertRaises(UnparseableNameException):
        #    IndividualNameCleaver("BARDEN PHD J D, R CHRISTOPHER").parse()

        #self.assertEqual('BARDEN PHD J D, R CHRISTOPHER', str(IndividualNameCleaver('BARDEN PHD J D, R CHRISTOPHER').parse(safe=True)))

        #with self.assertRaises(UnparseableNameException):
        #    IndividualNameCleaver("gobbledy blah bloop!!!.p,.lcrg%%% #$<").parse()

        #self.assertEqual('gobbledy blah bloop!!!.p,.lcrg%%% #$<', str(IndividualNameCleaver('gobbledy blah bloop!!!.p,.lcrg%%% #$<').parse(safe=True)))

    def test_parse_safe__politician(self):
        pass
        #with self.assertRaises(UnparseableNameException):
        #    PoliticianNameCleaver("BARDEN PHD J D, R CHRISTOPHER").parse()

        #self.assertEqual('BARDEN PHD J D, R CHRISTOPHER', str(PoliticianNameCleaver('BARDEN PHD J D, R CHRISTOPHER').parse(safe=True)))

        #with self.assertRaises(UnparseableNameException):
        #    PoliticianNameCleaver("gobbledy gook bah bah bloop!!!.p,.lcrg%%% #$<").parse()

        #self.assertEqual('gobbledy gook bah bah bloop!!!.p,.lcrg%%% #$<', str(PoliticianNameCleaver('gobbledy gook bah bah bloop!!!.p,.lcrg%%% #$<').parse(safe=True)))

    def test_parse_safe__organization(self):
        self.assertEqual('', OrganizationNameCleaver(None).parse(safe=True))
