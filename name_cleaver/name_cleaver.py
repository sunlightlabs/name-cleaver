import re

SUFFIX_RE = '([js]r\.?|[IVX]{2,})'


class Name(object):
    scottish_re = r'(?i)\b(?P<mc>ma?c)(?!hin)(?P<first_letter>\w)\w+'

    def primary_name_parts(self):
        raise NotImplementedError("Subclasses of Name must implement primary_name_parts.")

    def non_empty_primary_name_parts(self):
        return ' '.join([ x for x in self.primary_name_parts() if x ])

    def is_mixed_case(self):
        return re.search(r'[A-Z][a-z]', self.non_empty_primary_name_parts())

    def uppercase_the_scots(self, name_portion):
        matches = re.search(self.scottish_re, name_portion)

        if matches:
            mc = matches.group('mc')
            first_letter = matches.group('first_letter')
            return re.sub(mc + first_letter, mc.title() + first_letter.upper(), name_portion)
        else:
            return name_portion

    def fix_case_for_possessives(self, name):
        return re.sub(r"(\w+)'S\b", "\\1's", name)


class OrganizationName(Name):
    abbreviations = {
        'assns': 'Associations',
        'assn': 'Association',
        'cmte': 'Committee',
        'cltn': 'Coalition',
        'inst': 'Institute',
        'corp': 'Corporation',
        'co': 'Company',
        'fedn' : 'Federation',
        'fed': 'Federal',
        'fzco': 'Company',
        'usa': 'USA',
        'us': 'United States',
        'dept': 'Department',
        'assoc': 'Associates',
        'natl': 'National',
        'nat\'l': 'National',
        'intl': 'International',
        'inc': 'Incorporated',
        'llc': 'LLC',
        'llp': 'LLP',
        'lp': 'LP',
        'plc': 'PLC',
        'ltd': 'Limited',
        'univ': 'University',
        'colls': 'Colleges',
        'coll': 'College',
        'amer': 'American',
        'ed': 'Educational',
    }
    filler_words = 'The And Of In For Group'.split()

    name = None

    #suffix = None

    def new(self, name):
        self.name = name
        return self

    def case_name_parts(self):
        if not self.is_mixed_case():
            self.name = self.name.title()
            self.name = self.uppercase_the_scots(self.name)

            if re.match(r'(?i)^\w*PAC$', self.name):
                self.name = self.name.upper() # if there's only one word that ends in PAC, make the whole thing uppercase
            else:
                self.name = re.sub(r'(?i)\bpac\b', 'PAC', self.name) # otherwise just uppercase the PAC part

            self.name = self.uppercase_the_scots(self.name)
            self.name = self.fix_case_for_possessives(self.name)

        return self

    def primary_name_parts(self):
        return [ self.without_extra_phrases() ]

    def __unicode__(self):
        return unicode(self.name)

    def __str__(self):
        return unicode(self.name).encode('utf-8')

    def without_extra_phrases(self):
        """Removes parenthethical and dashed phrases"""
        # the last parenthesis is optional, because sometimes they are truncated
        name = re.sub(r'\s*\([^)]*\)?\s*$', '', self.name)
        name = re.sub(r'(?i)\s* formerly.*$', '', name)
        name = re.sub(r'(?i)\s*and its affiliates$', '', name)
        name = re.sub(r'\bet al\b', '', name)
        # strip everything after the hyphen if there are at least four characters preceding it
        return re.sub(r'(\w{4,})-+.*$', '\\1', name)

    def without_punctuation(self):
        name = re.sub(r'/', ' ', self.without_extra_phrases())
        return re.sub(r'[,.*:;+]*', '', name)

    def expand(self):
        return ' '.join(self.abbreviations.get(w.lower(), w) for w in self.without_punctuation().split())

    def kernel(self):
        stop_words = [ y.lower() for y in self.abbreviations.values() + self.filler_words ]
        kernel = ' '.join([ x for x in self.expand().split() if x.lower() not in stop_words ])

        # this is a hack to get around the fact that this is the only two-word phrase we want to block
        # amongst our stop words. if we end up with more, we may need a better way to do this
        kernel = re.sub(r'\s*United States', '', kernel)

        return kernel



class PersonName(Name):
    honorific = None
    first = None
    middle = None
    last = None
    suffix = None
    nick = None

    family_name_prefixes = ('de', 'di', 'du', 'la', 'van', 'von')
    allowed_honorifics = ['mrs', 'mrs.']

    def new(self, first, last, **kwargs):
        self.first = first.strip()
        self.last = last.strip()

        self.set_and_clean_option('middle', kwargs)
        self.set_and_clean_option('suffix', kwargs)
        self.set_and_clean_option('honorific', kwargs)
        self.set_and_clean_option('nick', kwargs)

        return self

    def set_and_clean_option(self, optname, kwargs):
        optval = kwargs.get(optname)

        if optval:
            optval = optval.strip()
            setattr(self, optname, optval)

    def new_from_tokens(self, *args, **kwargs):
        """
            Takes in a name that has been split by spaces.
            Names which are in [last, first] format need to be preprocessed.
            The nickname must be in double quotes to be recognized as such.

            This can take name parts in in these orders:
            first, middle, last, nick, suffix, honorific
            first, middle, last, nick, suffix
            first, middle, last, suffix, honorific
            first, middle, last, honorific
            first, middle, last, suffix
            first, middle, last, nick
            first, last, honorific
            first, last, suffix
            first, last, nick
            first, middle, last
            first, last
            last
        """
        if kwargs.get('allow_quoted_nicknames'):
            args = [ x.strip() for x in args if not re.match(r'^[(]', x) ]
        else:
            args = [ x.strip() for x in args if not re.match(r'^[("]', x) ]

        self.detect_and_fix_two_part_name(args)

        # set defaults
        self.first = ''
        self.last = ''

        # the final few tokens should always be detectable, otherwise a last name
        if len(args):
            if self.is_an_honorific(args[-1]):
                self.honorific = args.pop()
            if self.is_a_suffix(args[-1]):
                self.suffix = args.pop()
            if self.is_a_nickname(args[-1]):
                self.nick = args.pop()
            self.last = args.pop()

        num_remaining_parts = len(args)

        if num_remaining_parts == 3:
            # if we've still got this many parts, we'll consider what's left as first name
            # plus multi-part middle name
            self.first = args[0]
            self.middle = ' '.join(args[1:3])

        elif num_remaining_parts == 2:
            self.first, self.middle = args

        elif num_remaining_parts == 1:
            self.first = ' '.join(args)

        return self

    def is_a_suffix(self, name_part):
        return re.match(r'(?i)^%s$' % SUFFIX_RE, name_part)

    def is_an_honorific(self, name_part):
        return re.match(r'^(?i)\s*[dm][rs]s?[.,]?\s*$', name_part)

    def is_a_nickname(self, name_part):
        return re.match(r'^["(].*[")]$', name_part)

    def detect_and_fix_two_part_name(self, args):
        """
        This detects common family name prefixes and joins them to the last name,
        so names like "De Kuyper" don't end up with "De" as a middle name.
        """
        i = 0
        while i < len(args) - 1:
            if args[i].lower() in self.family_name_prefixes:
                args[i] = ' '.join(args[i:i+2])
                del(args[i+1])
                break
            else:
                i += 1

    def __unicode__(self):
        return unicode(self.name_str())

    def __str__(self):
        return unicode(self.name_str()).encode('utf-8')

    def name_str(self):
        return ' '.join([x.strip() for x in [
            self.honorific if self.honorific and self.honorific.lower() in self.allowed_honorifics else '',
            self.first,
            self.middle,
            self.nick,
            self.last,
            self.suffix
        ] if x])

    def case_name_parts(self):
        if not self.is_mixed_case():
            self.honorific = self.honorific.title() if self.honorific else None
            self.nick = self.nick.title() if self.nick else None

            if self.first:
                self.first = self.first.title()
                self.first = self.capitalize_and_punctuate_initials(self.first)

            if self.last:
                self.last = self.last.title()
                self.last = self.uppercase_the_scots(self.last)

            self.middle = self.middle.title() if self.middle else None

            if self.suffix:
                # Title case Jr/Sr, but uppercase roman numerals
                if re.match(r'(?i).*[js]r', self.suffix):
                    self.suffix = self.suffix.title()
                else:
                    self.suffix = self.suffix.upper()

        return self

    def is_only_initials(self, name_part):
        """
        Let's assume we have a name like "B.J." if the name is two to three
        characters and consonants only.
        """
        return re.match(r'(?i)[^aeiouy]{2,3}$', name_part)

    def capitalize_and_punctuate_initials(self, name_part):
        if self.is_only_initials(name_part):
            return ''.join([ '{0}.'.format(x.upper()) for x in name_part])
        else:
            return name_part

    def primary_name_parts(self):
        return [ self.first, self.last ]



class PoliticalMetadata():
    party = None
    state = None

    def plus_metadata(self, party, state):
        self.party = party
        self.state = state

        return self

    def __str__(self):
        if self.party or self.state:
            party_state = u"-".join([ x for x in [self.party, self.state] if x ]) # because presidential candidates are listed without a state
            return unicode(u"{0} ({1})".format(unicode(self.name_str()), party_state)).encode('utf-8')
        else:
            return unicode(self.name_str()).encode('utf-8')


class PoliticianName(PoliticalMetadata, PersonName):
    pass


class RunningMatesNames(PoliticalMetadata):

    def __init__(self, mate1, mate2):
        self.mate1 = mate1
        self.mate2 = mate2

    def name_str(self):
        return u' & '.join([unicode(self.mate1), unicode(self.mate2)])

    def __repr__(self):
        return self.__str__()

    def mates(self):
        return [ self.mate1, self.mate2 ]

    def is_mixed_case(self):
        for mate in self.mates():
            if mate.is_mixed_case():
                return True

        return False

    def case_name_parts(self):
        for mate in self.mates():
            mate.case_name_parts()

        return self



class IndividualNameCleaver(object):
    object_class = PersonName

    def __init__(self, string):
        self.name = string

    def parse(self):
        name, honorific, suffix, nick = self.separate_affixes(self.name)

        if honorific and not honorific.endswith('.'):
            honorific += '.'

        name = self.reverse_last_first(name)
        self.name = self.convert_name_to_obj(name, nick, honorific, suffix)
        assert isinstance(self.name, PersonName), "Didn't give back a PersonName object for %s!" % self.name

        return self.name.case_name_parts()

    def separate_affixes(self, name):
        name, honorific = self.extract_matching_portion(r'\b(?P<honorific>[dm][rs]s?[,.]?)(?=(\b|\s))+', name)
        name, suffix = self.extract_matching_portion(r'\b(?P<suffix>([js]r|[IVX]{2,}))(?=(\b|\s))+', name)
        name, junk = self.extract_matching_portion(r'(?P<junk_numbers>\b\d{2,}(?=(\b|\s))+)', name)
        name, nick = self.extract_matching_portion(r'("[^"]*")', name)

        # strip trailing non alphanumeric characters
        name = re.sub(r'[^a-zA-Z0-9]$', '', name)

        return name, honorific, suffix, nick

    def extract_matching_portion(self, pattern, name):
        m = re.search(pattern, name, flags=re.IGNORECASE)

        if m:
            matched_piece = m.group()
            name = re.sub('\s*{0}\s*'.format(matched_piece), '', name)
        else:
            matched_piece = None

        return name, matched_piece

    def reverse_last_first(self, name):
        # make sure we don't put a suffix in the middle, as in "Smith, Tom II"
        name, suffix = self.extract_matching_portion(r'\b(?P<suffix>([js]r|[IVX]{2,}))(?=(\b|\s))+', name)
        split = re.split(', ?', name)

        # make sure that we don't have "Jr" preceded by a comma
        if len(split) >= 2 and not re.match('(?i)%s' % SUFFIX_RE, split[-1].strip()):
            split.reverse()

        if suffix:
            split.append(suffix)

        return ' '.join(split)

    def convert_name_to_obj(self, name, nick, honorific, suffix):
        name = ' '.join([x.strip() for x in [name, nick, suffix, honorific] if x])

        return PersonName().new_from_tokens(*[x for x in name.split(' ')], **{'allow_quoted_nicknames':True})



class PoliticianNameCleaver(IndividualNameCleaver):

    object_class = PoliticianName

    def __init__(self, string):
        super(PoliticianNameCleaver, self).__init__(string)

    def parse(self):
        self.strip_party()
        self.name = self.convert_name_to_obj(self.name) # important for "last, first", and also running mates
        assert isinstance(self.name, PoliticianName) or isinstance(self.name, RunningMatesNames), "Didn't give back a PoliticianName or RunningMatesNames object for %s!" % self.name

        return self.name.case_name_parts()

    def strip_party(self):
        if '(' in self.name:
            self.name = re.sub(r'\s*\([^)]+\)\s*$', '', self.name)

    def convert_name_to_obj(self, name):
        if '&' in name:
            return self.convert_running_mates_names_to_obj(name)
        else:
            return self.convert_regular_name_to_obj(name)

    def convert_regular_name_to_obj(self, name):
        name = self.reverse_last_first(name)
        return PoliticianName().new_from_tokens(*[x for x in name.split(' ') if x])

    def convert_running_mates_names_to_obj(self, name):
        return RunningMatesNames(*[ self.convert_name_to_obj(x) for x in name.split(' & ') ])



class OrganizationNameCleaver(object):
    def __init__(self, string):
        self.name = string

    def parse(self, long_form=False):
        self.name = self.name.strip()

        self.name = OrganizationName().new(self.name)
        assert isinstance(self.name, OrganizationName)

        return self.name.case_name_parts()

    def convert_name_to_obj(self):
        self.name = OrganizationName().new(self.name)


