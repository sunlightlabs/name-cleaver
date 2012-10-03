import re
from exception import UnparseableNameException
from names     import SUFFIX_RE, PersonName, PoliticianName, RunningMatesNames, \
    OrganizationName



class BaseNameCleaver(object):

    def cannot_parse(self, safe, e=None):
        if safe:
            return self.orig_str
        else:
            # uncomment for debugging
            # if e:
            #    print e
            raise UnparseableNameException("Couldn't parse name: {0}".format(self.name))



class IndividualNameCleaver(BaseNameCleaver):
    object_class = PersonName

    def __init__(self, string):
        self.name = string
        self.orig_str = string

    def parse(self, safe=False):
        if not self.orig_str:
            return ''

        try:
            self.name = self.pre_process(self.name)

            name, honorific, suffix, nick = self.separate_affixes(self.name)

            if honorific and not honorific.endswith('.'):
                honorific += '.'

            name = self.reverse_last_first(name)
            self.name = self.convert_name_to_obj(name, nick, honorific, suffix)
        except Exception, e:
            return self.cannot_parse(safe, e)
        finally:
            if (isinstance (self.name, PersonName) and (self.name.first and self.name.last)):
                return self.name.case_name_parts()
            else:
                return self.cannot_parse(safe)


    def pre_process(self, name):
        # strip any spaces padding parenthetical phrases
        name = re.sub('\(\s*([^)]+)\s*\)', '(\1)', name)

        # get rid of trailing '& mrs'
        name = re.sub(' \& mrs\.?$', '', name, flags=re.IGNORECASE)

        return name

    def separate_affixes(self, name):
        name, honorific = self.extract_matching_portion(r'\b(?P<honorific>[dm][rs]s?[,.]?)(?=(\b|\s))+', name)
        name, suffix = self.extract_suffix(name)
        if suffix:
            suffix = suffix.replace('.', '')
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

    def extract_suffix(self, name):
        return self.extract_matching_portion(r'\b(?P<suffix>%s(?=(\b|\s))+)' % SUFFIX_RE, name)

    def reverse_last_first(self, name):
        """ Takes a name that is in [last, first] format and returns it in a hopefully [first last] order.
            Also extracts the suffix and puts it back on the end, in case it's embedded somewhere in the middle.
        """
        # make sure we don't put a suffix in the middle, as in "Smith, Tom II"
        name, suffix = self.extract_suffix(name)
        split = re.split(', ?', name)

        # make sure that the comma is not just preceding a suffix, such as "Jr",
        # by checking that we have at least 2 name parts and the last doesn't match
        # our suffix regex
        if len(split) >= 2 and not re.match('(?i)%s' % SUFFIX_RE, split[-1].strip()):
            split.reverse()

        if suffix:
            split.append(suffix)

        return ' '.join(split)

    def convert_name_to_obj(self, name, nick, honorific, suffix):
        name = ' '.join([x.strip() for x in [name, nick, suffix, honorific] if x])

        return PersonName().new_from_tokens(*[x for x in re.split('\s+', name)], **{'allow_quoted_nicknames':True})



class PoliticianNameCleaver(IndividualNameCleaver):

    object_class = PoliticianName

    def __init__(self, string):
        super(PoliticianNameCleaver, self).__init__(string)

    def parse(self, safe=False):
        if not self.orig_str:
            return ''

        try:
            self.strip_party()
            self.name = self.convert_name_to_obj(self.name) # important for "last, first", and also running mates
        except Exception, e:
            return self.cannot_parse(safe, e)
        finally:
            if ((isinstance(self.name, PoliticianName) and self.name.first and self.name.last) or isinstance(self.name, RunningMatesNames)):
                return self.name.case_name_parts()
            else:
                return self.cannot_parse(safe)

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
        return PoliticianName().new_from_tokens(*[x for x in re.split('\s+', name) if x])

    def convert_running_mates_names_to_obj(self, name):
        return RunningMatesNames(*[ self.convert_name_to_obj(x) for x in name.split(' & ') ])



class OrganizationNameCleaver(object):
    def __init__(self, string):
        self.name = string
        self.orig_str = string

    def parse(self, safe=False):
        if not self.orig_str:
            return ''

        try:
            self.name = self.name.strip()

            self.name = OrganizationName().new(self.name)
        except Exception, e:
            return self.cannot_parse(safe, e)
        finally:
            if isinstance(self.name, OrganizationName):
                return self.name.case_name_parts()
            else:
                return self.cannot_parse(safe)


    def convert_name_to_obj(self):
        self.name = OrganizationName().new(self.name)


