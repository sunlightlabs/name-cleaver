import re
from exception import UnparseableNameException
from names import SUFFIX_RE, DEGREE_RE, PersonName, PoliticianName, RunningMatesNames, \
    OrganizationName
from nicknames import NICKNAMES


class BaseNameCleaver(object):

    def cannot_parse(self, safe, e=None):
        if safe:
            return self.orig_str
        else:
            # uncomment for debugging
            #if e:
            #   print e
            raise UnparseableNameException(u"Couldn't parse name: {0}".format(self.name))


class IndividualNameCleaver(BaseNameCleaver):
    object_class = PersonName

    def __init__(self, string):
        self.name = string
        self.orig_str = string

    def parse(self, safe=False):
        if not self.orig_str:
            return ''

        if not ' ' in self.name:
            self.name = self.object_class().new_from_tokens(self.name)
            return self.name.case_name_parts()
        else:
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
                if (isinstance(self.name, self.object_class) and self.name.last):
                    return self.name.case_name_parts()
                else:
                    return self.cannot_parse(safe)

    def pre_process(self, name):
        # strip any spaces padding parenthetical phrases
        name = re.sub('\(\s*([^)]+)\s*\)', '(\1)', name)

        # get rid of trailing '& mrs'
        name = re.sub(' (?i)\& mrs\.?$', '', name)

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
        m = re.finditer(pattern, name, flags=re.IGNORECASE)

        matched_portion = None
        match_strings = []

        for match in m:
            matched_piece = match.group()
            match_strings.append(matched_piece)
            name = re.sub('\s*{0}\s*'.format(matched_piece), '', name)

        if len(match_strings):
            matched_portion = ' '.join(match_strings)

        return name, matched_portion

    def extract_suffix(self, name):
        """
        Returns a tuple of (name, suffix), or (name, None) if no suffix could be found.
        As the method name indicates, the name is returned without the suffix.

        Suffixes deemed to be degrees are discarded.
        """
        # don't extract suffixes if we can't reasonably suspect we have enough parts to the name for there to be one
        if len(name.strip().split()) > 2:
            name, suffix = self.extract_matching_portion(r'\b(?P<suffix>{})(?=\b|\s)'.format(SUFFIX_RE), name)
            suffix, degree = self.extract_matching_portion(DEGREE_RE, suffix or '')
            return name, suffix or None

        return name, None

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
        if len(split) >= 2:
            split.reverse()

        if suffix:
            split.append(suffix)

        return ' '.join(split)

    def convert_name_to_obj(self, name, nick, honorific, suffix):
        name = ' '.join([x.strip().strip('.') for x in [name, nick, suffix, honorific] if x])

        return self.object_class().new_from_tokens(*[x for x in re.split('\s+', name)], **{'allow_quoted_nicknames': True})

    @classmethod
    def name_processing_failed(cls, subject_name):
        return subject_name and (isinstance(subject_name, RunningMatesNames) or not subject_name.last)

    @classmethod
    def compare(cls, name1, name2):
        score = 0

        # score last name
        if name1.last == name2.last:
            score += 1
        else:
            return 0

        # score first name
        if name1.first and name2.first and name1.first == name2.first:
            score += 1
        elif name1.first and name2.first:
            for name_set in NICKNAMES:
                if set(name_set).issuperset([name1.first, name2.first]):
                    score += 0.6
                    break

            if name1.first == name2.middle and name2.first == name1.middle:
                score += 0.8
            else:
                try:
                    # this was failing in cases where an odd organization name was in the mix
                    if name1.first[0] == name2.first[0]:
                        score += 0.1
                except:
                    return 0

        # score middle name
        if name1.middle and name2.middle:
            # we only want to count the middle name for much if we've already
            # got a match on first and last, to avoid getting high scores for
            # names which only match on last and middle
            if score > 1.1:
                if name1.middle == name2.middle:
                    score += 1
                elif name1.middle[0] == name2.middle[0]:
                    score += .5
                else:
                    score -= 1.5

            else:
                score += .2

        return score


class PoliticianNameCleaver(IndividualNameCleaver):

    object_class = PoliticianName

    def __init__(self, string):
        super(PoliticianNameCleaver, self).__init__(string)

    def parse(self, safe=False):
        if not self.orig_str:
            return ''

        if not ' ' in self.name:
            self.name = self.object_class().new_from_tokens(self.name)
            return self.name.case_name_parts()
        else:
            try:
                self.strip_party()
                self.name = self.convert_name_to_obj(self.name)  # important for "last, first", and also running mates
            except Exception, e:
                return self.cannot_parse(safe, e)
            finally:
                if ((isinstance(self.name, self.object_class) and self.name.last) or isinstance(self.name, RunningMatesNames)):
                    return self.name.case_name_parts()
                else:
                    return self.cannot_parse(safe)

    def strip_party(self):
        if '(' in self.name:
            self.name = re.sub(r'\s*\([^)]+\)\s*$', '', self.name)

    def convert_name_to_obj(self, name):
        if '&' in name or '/' in name:
            return self.convert_running_mates_names_to_obj(name)
        else:
            return self.convert_regular_name_to_obj(name)

    def convert_regular_name_to_obj(self, name):
        name = self.reverse_last_first(name)
        return self.object_class().new_from_tokens(*[x for x in re.split('\s+', name) if x])

    def convert_running_mates_names_to_obj(self, name):
        return RunningMatesNames(*[self.convert_name_to_obj(x) for x in re.split(' [&/] ', name)])


class OrganizationNameCleaver(object):
    object_class = OrganizationName

    def __init__(self, string):
        self.name = string
        self.orig_str = string

    def parse(self, safe=False):
        if not self.orig_str:
            return ''

        try:
            self.name = self.name.strip()

            self.name = self.object_class().new(self.name)
        except Exception, e:
            return self.cannot_parse(safe, e)
        finally:
            if isinstance(self.name, self.object_class):
                return self.name.case_name_parts()
            else:
                return self.cannot_parse(safe)

    def convert_name_to_obj(self):
        self.name = self.object_class().new(self.name)

    @classmethod
    def name_processing_failed(cls, subject_name):
        return not isinstance(subject_name, cls.object_class)

    @classmethod
    def compare(cls, match, subject):
        """
            Accepts two OrganizationName objects and returns an arbitrary,
            numerical score based upon how well the names match.
        """
        if match.expand().lower() == subject.expand().lower():
            return 4
        elif match.kernel().lower() == subject.kernel().lower():
            return 3
        # law and lobbying firms in CRP data typically list only the first two partners
        # before 'et al'
        elif ',' in subject.expand():  # we may have a list of partners
            if subject.crp_style_firm_name() == str(match).lower():
                return 3
        else:
            return 2
