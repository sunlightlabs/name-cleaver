import re, string, itertools

SUFFIX_RE = '([js]r\.?|[IVX]{2,})'

class PoliticianNameCleaver():

    def __init__(self, string):
        self.name = string

    def parse(self):
        self.strip_party()
        self.convert_to_standard_order() # important for "last, first", and also running mates
        assert isinstance(self.name, Name) or isinstance(self.name, RunningMatesNames), "Names didn't give back a Name object for %s!" % self.name

        return self.name.case_name_parts()

    def strip_party(self):
        if '(' in self.name:
            self.name = re.sub(r'\s*\(\w+\)\s*$', '', self.name)

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
        return Name().new_from_tokens(*[x for x in name.split(' ') if x])

    def convert_running_mates_to_obj(self):
        return RunningMatesNames(*[ self.convert_name_to_obj(x) for x in self.name.split(' & ') ])


class Name:
    first = None
    middle = None
    last = None
    suffix = None

    family_name_prefixes = ('de', 'di', 'du', 'la', 'van', 'von')

    def new(self, first, last, **kwargs):
        self.first = first.strip()
        self.last = last.strip()
        self.middle = kwargs.get('middle', None)
        if self.middle:
            self.middle = self.middle.strip()
        self.suffix = kwargs.get('suffix', None)
        if self.suffix:
            self.suffix = self.suffix.strip()

        return self

    def new_from_tokens(self, *args):
        args = [ x.strip() for x in args if not re.match(r'^[("]', x) ]

        self.detect_and_fix_two_part_name(args)

        if len(args) == 4:
            if self.is_a_suffix(args[-1]):
                self.first, self.middle, self.last, self.suffix = args
            else:
                self.first = args[0]
                self.middle = ' '.join(args[1:3])
                self.last = args[3]

        elif len(args) == 3:

            if self.is_a_suffix(args[-1]):
                self.first, self.last, self.suffix = args
            else:
                self.first, self.middle, self.last = args

        elif len(args) == 2:
            self.first, self.last = args

        elif len(args) == 1:
            self.last = args[0]

        return self

    def is_a_suffix(self, name_part):
        return re.match(r'(?i)^%s$' % SUFFIX_RE, name_part)

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
        return ' '.join([x for x in [self.first, self.middle, self.last, self.suffix] if x])

    def is_mixed_case(self):
        return re.match(r'[A-Z][a-z]', ' '.join([x for x in [self.first, self.last] if x]))

    def case_name_parts(self):
        if not self.is_mixed_case():
            self.first = self.first.title() if self.first else None

            if self.last:
                self.last = self.last.title()
                self.uppercase_the_scots()

            self.middle = self.middle.title() if self.middle else None

            if self.suffix:
                if re.match(r'(?i).*[js]r', self.suffix):
                    self.suffix = self.suffix.title()
                else:
                    self.suffix = self.suffix.upper()

        return self

    def uppercase_the_scots(self):
        matches = re.search(r'(?i)\b(?P<mc>ma?c)(?P<first_letter>\w)\w+', self.last)

        if matches:
            mc = matches.group('mc')
            first_letter = matches.group('first_letter')
            self.last = re.sub(mc + first_letter, mc.title() + first_letter.upper(), self.last)


class RunningMatesNames:

    def __init__(self, mate1, mate2):
        self.mate1 = mate1
        self.mate2 = mate2

    def __str__(self):
        return ' & '.join([str(self.mate1), str(self.mate2)])

    def __repr__(self):
        return ' & '.join([str(self.mate1), str(self.mate2)])

    def mates(self):
        return [ self.mate1, self.mate2 ]

    def is_mixed_case(self):
        for mate in self.mates():
            if mate.is_mixed_case(): return True

        return False

    def case_name_parts(self):
        for mate in self.mates():
            mate.case_name_parts()

        return self

    def uppercase_the_scots(self):
        for mate in self.mates():
            mate.uppercase_the_scots()


