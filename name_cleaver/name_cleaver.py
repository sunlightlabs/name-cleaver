import re

SUFFIX_RE = '([js]r\.?|[IVX]{2,})'


class Name(object):
    scottish_re = r'(?i)\b(?P<mc>ma?c)(?P<first_letter>\w)\w+'

    def primary_name_parts(self):
        raise NotImplementedError("Subclasses of Name must implement primary_name_parts.")

    def is_mixed_case(self):
        return re.match(r'[A-Z][a-z]', ' '.join([x for x in self.primary_name_parts() if x]))

    def uppercase_the_scots(self, name_portion):
        matches = re.search(self.scottish_re, name_portion)

        if matches:
            mc = matches.group('mc')
            first_letter = matches.group('first_letter')
            return re.sub(mc + first_letter, mc.title() + first_letter.upper(), name_portion)
        else:
            return name_portion



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
        #self.primary_name = primary
        #self.suffix = suffix

    def case_name_parts(self):
        if not self.is_mixed_case():
            self.name = self.name.title()
            self.name = self.uppercase_the_scots(self.name)

            if re.match(r'(?i)^\w*PAC$', self.name):
                self.name = self.name.upper() # if there's only one word that ends in PAC, make the whole thing uppercase
            else:
                self.name = re.sub(r'(?i)\bpac\b', 'PAC', self.name) # otherwise just uppercase the PAC part

            self.name = self.uppercase_the_scots(self.name)

        return self

    def primary_name_parts(self):
        return [ self.name ]

    def __str__(self):
        return self.name

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
        #return re.sub(r'[,.*&:;]*', '', name)
        return re.sub(r'[,.*:;]*', '', name)

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

    family_name_prefixes = ('de', 'di', 'du', 'la', 'van', 'von')
    allowed_honorifics = ['mrs']

    def new(self, first, last, **kwargs):
        self.first = first.strip()
        self.last = last.strip()

        self.middle = kwargs.get('middle')
        if self.middle:
            self.middle = self.middle.strip()

        self.suffix = kwargs.get('suffix')
        if self.suffix:
            self.suffix = self.suffix.strip()

        self.honorific = kwargs.get('honorific')
        if self.honorific:
            self.honorific = self.honorific.strip()

        return self

    def new_from_tokens(self, *args, **kwargs):
        """
            Takes in a name that has been split by spaces.
            Names which are in [last, first] format need to be preprocessed.

            This can take name parts in in these orders:
            first, middle, last, suffix, honorific
            first, middle, last, honorific
            first, middle, last, suffix
            first, last, suffix
            first, last, honorific
            first, middle, last
            first, last
            last
        """
        if kwargs.get('allow_quoted_nicknames'):
            args = [ x.strip() for x in args if not re.match(r'^[(]', x) ]
        else:
            args = [ x.strip() for x in args if not re.match(r'^[("]', x) ]

        self.detect_and_fix_two_part_name(args)

        num_parts = len(args)

        if num_parts == 5:
            self.first, self.middle, self.last, self.suffix, self.honorific = args

        elif num_parts == 4:
            if self.is_an_honorific(args[-1]):
                self.first, self.middle, self.last, self.honorific = args
            elif self.is_a_suffix(args[-1]):
                self.first, self.middle, self.last, self.suffix = args
            else:
                # if the last isn't an honorific or a suffix,
                # consider it the last name and consider
                # the middle two parts as the middle name
                self.first = args[0]
                self.middle = ' '.join(args[1:3])
                self.last = args[3]

        elif num_parts == 3:
            if self.is_an_honorific(args[-1]):
                self.first, self.last, self.honorific = args
            elif self.is_a_suffix(args[-1]):
                self.first, self.last, self.suffix = args
            else:
                self.first, self.middle, self.last = args

        elif num_parts == 2:
            self.first, self.last = args

        elif num_parts == 1:
            self.last = args[0]

        else:
            raise "The name was empty."

        return self

    def is_a_suffix(self, name_part):
        return re.match(r'(?i)^%s$' % SUFFIX_RE, name_part)

    def is_an_honorific(self, name_part):
        return re.match(r'^(?i)\s*m[rs]s?.?\s*$', name_part)

    def detect_and_fix_two_part_name(self, args):
        i = 0
        while i < len(args) - 1:
            if args[i].lower() in self.family_name_prefixes:
                args[i] = ' '.join(args[i:i+2])
                del(args[i+1])
                break
            else:
                i += 1

    def __str__(self):
        return self.name_str()

    def name_str(self):
        return ' '.join([x.strip() for x in [
            self.honorific if self.honorific and self.honorific.lower() in self.allowed_honorifics else '',
            self.first,
            self.middle,
            self.last,
            self.suffix
        ] if x])

    def case_name_parts(self):
        if not self.is_mixed_case():
            self.first = self.first.title() if self.first else None

            if self.last:
                self.last = self.last.title()
                self.last = self.uppercase_the_scots(self.last)

            self.middle = self.middle.title() if self.middle else None

            if self.suffix:
                if re.match(r'(?i).*[js]r', self.suffix):
                    self.suffix = self.suffix.title()
                else:
                    self.suffix = self.suffix.upper()

        return self

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
            party_state = "-".join([x for x in [self.party, self.state] if x]) # because presidential candidates are listed without a state
            return "{0} ({1})".format(self.name_str(), party_state)
        else:
            return self.name_str()


class PoliticianName(PoliticalMetadata, PersonName):
    pass


class RunningMatesNames(PoliticalMetadata):

    def __init__(self, mate1, mate2):
        self.mate1 = mate1
        self.mate2 = mate2

    def name_str(self):
        return ' & '.join([str(self.mate1), str(self.mate2)])

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
        name, honorific, suffix = self.separate_affixes(self.name)
        print 'name: {0}; honorific: {1}; suffix: {2}'.format(name, honorific, suffix)
        self.name = self.convert_name_to_obj(name, honorific, suffix)
        assert isinstance(self.name, PersonName), "Didn't give back a PersonName object for %s!" % self.name

        return self.name.case_name_parts()

    def separate_affixes(self, name):
        # this should match both honorifics (mr/mrs/ms) and jr/sr/II/III
        matches = re.search(r'(?i)^\s*(?P<name>.*)\b((?P<honorific>m[rs]s?[.,]?)|(?P<suffix>([js]r|I{2,})))?\s*$', name)
        if matches:
            return matches.group('name', 'honorific', 'suffix')
        else:
            return name, None, None

    def reverse_last_first(self, name):
        split = name.split(', ')

        # make sure that we don't have "Jr" preceded by a comma
        if len(split) >= 2 and not re.match('(?i)%s' % SUFFIX_RE, split[-1].strip()):
            split.reverse()

        return ' '.join(split)

    def convert_name_to_obj(self, name, honorific, suffix):
        name = self.reverse_last_first(name)

        name = re.sub(r'\d{2,}\s*$', '', name) # strip any trailing numbers
        name = re.sub(r'^(?i)\s*m[rs]s?\.?\s+', '', name) # strip leading 'Mr' if not caught by the other algorithm (e.g. the name was in first last format to begin with)
        name = ' '.join([x.strip() for x in [honorific, name, suffix] if x])

        return PersonName().new_from_tokens(*[x for x in name.split(' ')], allow_quoted_nicknames=True)



class PoliticianNameCleaver(IndividualNameCleaver):

    object_class = PoliticianName

    def __init__(self, string):
        super(PoliticianNameCleaver, self).__init__(string)

    def parse(self):
        self.strip_party()
        self.convert_to_standard_order() # important for "last, first", and also running mates
        assert isinstance(self.name, PoliticianName) or isinstance(self.name, RunningMatesNames), "Didn't give back a PoliticianName or RunningMatesNames object for %s!" % self.name

        return self.name.case_name_parts()

    def strip_party(self):
        if '(' in self.name:
            self.name = re.sub(r'\s*\([^)]+\)\s*$', '', self.name)

    def convert_to_standard_order(self):
        if '&' in self.name:
            self.name = self.convert_running_mates_to_obj()
        else:
            self.name = self.convert_name_to_obj(self.name)

    def reverse_last_first(self, name):
        split = name.split(', ')

        # make sure that we don't have "Jr" preceded by a comma
        if len(split) >= 2 and not re.match('(?i)%s' % SUFFIX_RE, split[-1].strip()):
            split.reverse()

        return ' '.join(split)

    def convert_name_to_obj(self, name):
        name = self.reverse_last_first(name)
        return PoliticianName().new_from_tokens(*[x for x in name.split(' ') if x])

    def convert_running_mates_to_obj(self):
        return RunningMatesNames(*[ self.convert_name_to_obj(x) for x in self.name.split(' & ') ])



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



