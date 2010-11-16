import re, string, itertools

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
        split.reverse()
        return ' '.join(split)

    def convert_name_to_obj(self, name):
        name = self.reverse_last_first(name)
        return Name().new_from_tokens(*name.split(' '))

    def convert_running_mates_to_obj(self):
        return RunningMatesNames(*[ self.convert_name_to_obj(x) for x in self.name.split(' & ') ])


class Name:
    first = None
    middle = None
    last = None
    suffix = None

    last_name_prefixes = ('de', 'di', 'du', 'la', 'van', 'von')

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
        args = [ x.strip() for x in args if not re.match(r'\(', x) ]

        if len(args) == 4:
            self.first, self.middle, self.last, self.suffix = args

        elif len(args) == 3:

            if re.match(r'(?i)^([js]r\.?|[IVX]{2,})$', args[-1]):
                self.first, self.last, self.suffix = args
            else:
                self.first, self.middle, self.last = args

        elif len(args) == 2:
            self.first, self.last = args

        elif len(args) == 1:
            self.last = args[0]

        self.detect_and_fix_two_part_last_name()


        return self

    def detect_and_fix_two_part_last_name(self):
        if self.last and self.last.lower() in self.last_name_prefixes:
            self.last = ' '.join([self.last, self.suffix])
            self.suffix = None
        elif self.middle and self.middle.lower() in self.last_name_prefixes:
            self.last = ' '.join([self.middle, self.last])
            self.middle = None
        elif self.suffix and len(self.suffix) > 3:
            self.middle = ' '.join([self.middle, self.last])
            self.suffix = None

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
        matches = re.search(r'(?i)(?P<mc>ma?c)(?P<first_letter>\w)', self.last)

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


