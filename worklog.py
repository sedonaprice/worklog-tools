# -*- mode: python ; coding: utf-8 -*-
# Copyright 2014-2015 Peter Williams <peter@newton.cx>
# Licensed under the GNU General Public License, version 3 or higher.

"""
Shared routines for my worklog tools.
"""

# __all__ = b'''nbsp months Holder die warn open_template slurp_template
#               process_template list_data_files load unicode_to_latex
#               html_escape Markup MupText MupItalics MupBold MupUnderline
#               MupLink MupJoin MupList render_latex render_html Formatter
#               ADSCountError parse_ads_cites canonicalize_name surname best_url
#               cite_info compute_cite_stats partition_pubs setup_processing
#               get_ads_cite_count bootstrap_bibtex bootstrap_bibtex_alphabetical'''.split ()
__all__ = r'''nbsp months Holder die warn open_template slurp_template
              process_template list_data_files load unicode_to_latex
              html_escape Markup MupText MupItalics MupBold MupUnderline
              MupLink MupJoin MupList render_latex render_html Formatter
              ADSCountError parse_ads_cites canonicalize_name surname best_url
              cite_info compute_cite_stats partition_pubs setup_processing
              get_ads_cite_count bootstrap_bibtex bootstrap_bibtex_alphabetical'''.split ()

nbsp = u'\u00a0'
months = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split ()


# Infrastructure

from inifile import Holder

def die (fmt, *args):
    if len (args):
        text = fmt % args
    else:
        text = str (fmt)

    raise SystemExit ('error: ' + text)


def warn (fmt, *args):
    if len (args):
        text = fmt % args
    else:
        text = str (fmt)

    import sys
    print >>sys.stderr, 'warning:', text


def open_template (stem):
    from os.path import join, dirname
    from errno import ENOENT

    try:
        return open (join ('templates', stem))
    except IOError as e:
        if e.errno != ENOENT:
            raise

    try:
        return open (join (dirname (__file__), 'templates', stem))
    except Exception as e:
        die ('cannot open template "%s": %s (%s)', stem, e, e.__class__.__name__)


def slurp_template (stem):
    with open_template (stem) as f:
        #return f.read ().decode ('utf8')
        return f.read ()


def process_template (stream, commands, context):
    """Read through a template line-by-line and replace special lines. Each
    regular line is yielded to the caller. `commands` is a dictionary of
    strings to callables; if the first word in a line is in `commands`, the
    callable is invoked, with `context` and the remaining words in the line as
    arguments. Its return value is either a string or an iterable, with each
    iterate being yielded to the caller in the latter case."""

    for line in stream:
        #line = line.decode ('utf8').rstrip ()
        line = line.rstrip ()
        a = line.split ()

        if not len (a) or a[0] not in commands:
            yield line
        else:
            result = commands[a[0]] (context, *a[1:])
            #if isinstance (result, basestring):
            if isinstance (result, str):
                yield result
            else:
                for subline in result:
                    yield subline


def list_data_files (datadir='.'):
    from os import listdir
    from os.path import join

    any = False

    for item in sorted (listdir (datadir)):
        if item.startswith ('.'):
            continue
        if not item.endswith ('.txt'):
            continue

        # Note that if there are text files that contain no records (e.g. all
        # commented), we won't complain.
        any = True
        yield join (datadir, item)

    if not any:
        die ('no data files found in directory "%s"', datadir)


def load (datadir='.'):
    from inifile import read as iniread

    for path in list_data_files (datadir):
        for item in iniread (path):
            yield item


# Text formatting. We have a tiny DOM-type system for markup so we can
# abstract across LaTeX and HTML. Initially I tried to do everything in HTML,
# and then convert that to LaTeX, but the layers of escaping got a little
# worrisome, and some constructs just don't work well in that model (e.g.
# tables). So we do this silliness instead.

from unicode_to_latex import unicode_to_latex

def html_escape (text):
    """Escape special characters for our dumb subset of HTML."""

    # return (unicode (text)
    #         .replace ('&', '&amp;')
    #         .replace ('<', '&lt;')
    #         .replace ('>', '&gt;')
    #         .replace ('"', '&quot;')
    #         .replace ("'", '&apos;')
    #         .replace (u"\u0303", "~"))
    return (str (text)
            .replace ('&', '&amp;')
            .replace ('<', '&lt;')
            .replace ('>', '&gt;')
            .replace ('"', '&quot;')
            .replace ("'", '&apos;')
            .replace (u"\u0303", "~"))

class Markup (object):
    def _latex (self):
        raise NotImplementedError ()

    def _html (self):
        raise NotImplementedError ()

    def latex (self):
        return u''.join (self._latex ())

    def html (self):
        return u''.join (self._html ())



def _maybe_wrap_text (thing):
    if isinstance (thing, Markup):
        return thing
    return MupText (thing)


class MupText (Markup):
    def __init__ (self, text):
        #self.text = unicode (text)
        self.text = str (text)

    def _latex (self):
        arr = [unicode_to_latex (self.text)]
        for i, t in enumerate(arr):
            if "KMOS3D" in t:
                k3d_orig = "KMOS3D"
                #k3d = r"KMOS$^{3D}$"
                k3d = r"KMOS$^{\hbox{\textit{{\scriptsize{3D}}}}}$"
                tmp = t.split(k3d_orig)
                out = k3d.join(tmp)
                arr[i] = out
                t = out


            if "\$" in t:
                tmp = t.split("\$")
                out = r"$".join(tmp)
                arr[i] = out
                t = out

            #
            #
            if r"{\alpha}" in t:
                tmp = t.split(r"{\alpha}")
                out = r"{\ensuremath{\alpha}}".join(tmp)
                arr[i] = out
                t = out
            #
            #
            if r"\{\textbackslash{}alpha\}" in t:
                tmp = t.split(r"\{\textbackslash{}alpha\}")
                out = r"{\ensuremath{\alpha}}".join(tmp)
                arr[i] = out
                t = out
            #
            if r"{\lesssim}" in t:
                tmp = t.split(r"{\lesssim}")
                out = r"{\ensuremath{\lesssim}}".join(tmp)
                arr[i] = out
                t = out
            #
            if r"\{\textbackslash{}lesssim\}" in t:
                tmp = t.split(r"\{\textbackslash{}lesssim\}")
                out = r"{\ensuremath{\lesssim}}".join(tmp)
                arr[i] = out
                t = out

            if r"\_\{" in t:
                tmp = t.split(r"\_\{")
                out = ''
                pre = tmp[0]
                for j in range(len(tmp)):
                    if j < len(tmp)-1:
                        subs = tmp[j+1].split("\}")[0]
                        out += pre+r"\ensuremath{_{\mathrm{"+subs+r"}}}"
                        try:
                            pre = "}".join(tmp[j+1].split("\}")[1:])
                        except:
                            pre = ""
                    else:
                        out += pre
                arr[i] = out
                t = out

            if "\~" in t:
                tmp = t.split("\~")
                out = r"\ensuremath{\sim}".join(tmp)
                arr[i] = out
                t = out

            if r"\textbackslash{}sim" in t:
                tmp = t.split(r"\textbackslash{}sim")
                out = r"\ensuremath{\sim}".join(tmp)
                arr[i] = out
                t = out


            if "\{sim\}" in t:
                tmp = t.split("\{sim\}")
                out = r"\ensuremath{\sim}".join(tmp)
                arr[i] = out
                t = out

            if " sim " in t:
                tmp = t.split(" sim ")
                out = r"\ensuremath{\sim}".join(tmp)
                arr[i] = out
                t = out

            if r"\{\textbackslash{}tilde\}" in t:
                tmp = t.split(r"\{\textbackslash{}tilde\}")
                out = r"\ensuremath{\sim}".join(tmp)
                arr[i] = out
                t = out

            #

            if r"\textbackslash{}tilde" in t:
                tmp = t.split(r"\textbackslash{}tilde")
                out = r"\ensuremath{\sim}".join(tmp)
                arr[i] = out
                t = out

            if r"{\ensuremath{\sim}}" in t:
                tmp = t.split(r"{\ensuremath{\sim}}")
                out = r"\ensuremath{\sim}".join(tmp)
                arr[i] = out
                t = out

            if r"\{\}" in t:
                out = "".join(t.split(r"\{\}"))
                arr[i] = out
                t = out



        return arr
        #return [unicode_to_latex (self.text)]

    def _html (self):
        arr = [html_escape (self.text)]
        # for i, t in enumerate(arr):
        #     if "_{" in t:
        #         tmp = t.split('_{')
        #         out = tmp[0]+r"<sub>"+''.join(tmp.split("}"))+r"</sub>"
        #         arr[i] = out

        for i, t in enumerate(arr):
            if r"KMOS3D" in t:
                k3d_orig = "KMOS3D"
                k3d = r"KMOS<sup>3D</sup>$"
                tmp = t.split(k3d_orig)
                out = k3d.join(tmp)
                arr[i] = out
                t = out

            if r"_{" in t:
                tmp = t.split(r'_{')
                out = ''
                pre = tmp[0]
                for j in range(len(tmp)):
                    if j < len(tmp)-1:
                        subs = tmp[j+1].split("}")[0]
                        #''.join(tmp[j+1].split("}"))
                        out += pre+r"<sub>"+subs+r"</sub>"
                        try:
                            pre = "}".join(tmp[j+1].split("}")[1:])
                        except:
                            pre = ""
                    else:
                        out += pre
                arr[i] = out
                t = out
            #
            #
            if r"{\alpha}" in t:
                tmp = t.split(r"{\alpha}")
                out = u"\u03B1".join(tmp)
                arr[i] = out
                t = out
            #
            if r"{\lesssim}" in t:
                tmp = t.split(r"{\lesssim}")
                out = u"\u2272".join(tmp)
                arr[i] = out
                t = out
                #
            #
            if r"--" in t:
                tmp = t.split(r"--")
                out = r"-".join(tmp)
                arr[i] = out
                t = out

            if "$" in t:
                tmp = t.split("$")
                out = r"".join(tmp)
                arr[i] = out
                t = out

            if r"\sim" in t:
                tmp = t.split(r"\sim")
                out = r"~".join(tmp)
                arr[i] = out
                t = out

            if r"sim" in t:
                tmp = t.split(r"sim")
                out = r"~".join(tmp)
                arr[i] = out
                t = out
            if r"{\tilde}" in t:
                    tmp = t.split(r"{\tilde}")
                    out = r"~".join(tmp)
                    arr[i] = out
                    t = out
            if r"\tilde" in t:
                tmp = t.split(r"\tilde")
                out = r"~".join(tmp)
                arr[i] = out
                t = out


            if r"{}" in t:
                out = "".join(t.split(r"{}"))
                arr[i] = out
                t = out




        return arr
        #return [html_escape (self.text)]


class MupItalics (Markup):
    def __init__ (self, inner):
        self.inner = _maybe_wrap_text (inner)

    def _latex (self):
        return [u'\\textit{'] + self.inner._latex () + [u'}']

    def _html (self):
        return [u'<i>'] + self.inner._html () + [u'</i>']


class MupBold (Markup):
    def __init__ (self, inner):
        self.inner = _maybe_wrap_text (inner)

    def _latex (self):
        return [u'\\textbf{'] + self.inner._latex () + [u'}']

    def _html (self):
        return [u'<b>'] + self.inner._html () + [u'</b>']


class MupUnderline (Markup):
    def __init__ (self, inner):
        self.inner = _maybe_wrap_text (inner)

    def _latex (self):
        return [u'\\underline{'] + self.inner._latex () + [u'}']

    def _html (self):
        return [u'<u>'] + self.inner._html () + [u'</u>']


class MupLink (Markup):
    def __init__ (self, url, inner):
        #self.url = unicode (url)
        self.url = str (url)
        self.inner = _maybe_wrap_text (inner)

    def _latex (self):
        return ([u'\\href{', self.url.replace ('%', '\\%'), u'}{'] +
                self.inner._latex () + [u'}'])

    def _html (self):
        return ([u'<a href="', html_escape (self.url), u'">'] +
                self.inner._html () + [u'</a>'])


class MupJoin (Markup):
    def __init__ (self, sep, items):
        self.sep = _maybe_wrap_text (sep)
        self.items = [_maybe_wrap_text (i) for i in items]

    def _latex (self):
        esep = self.sep._latex ()
        result = []
        first = True

        for i in self.items:
            if first:
                first = False
            else:
                result += esep

            result += i._latex ()

        return result

    def _html (self):
        esep = self.sep._html ()
        result = []
        first = True

        for i in self.items:
            if first:
                first = False
            else:
                result += esep

            result += i._html ()

        return result


class MupList (Markup):
    def __init__ (self, ordered, items):
        self.ordered = bool (ordered)
        self.items = [_maybe_wrap_text (i) for i in items]

    def _latex (self):
        if self.ordered:
            res = [u'\\begin{enumerate}']
        else:
            res = [u'\\begin{itemize}']

        for i in self.items:
            res.append (u'\n\\item ')
            res += i._latex ()

        if self.ordered:
            res.append (u'\n\\end{enumerate}\n')
        else:
            res.append (u'\n\\end{itemize}\n')

        return res

    def _html (self):
        if self.ordered:
            res = [u'<ol>']
        else:
            res = [u'<ul>']

        for i in self.items:
            res.append (u'\n<li>')
            res += i._html ()
            res.append (u'</li>')

        if self.ordered:
            res.append (u'\n</ol>\n')
        else:
            res.append (u'\n</ul>\n')

        return res


def render_latex (value):
    if isinstance (value, int):
        #return unicode (value)
        return str (value)
    #if isinstance (value, unicode):
    if isinstance (value, str):
        return unicode_to_latex (value)
    #if isinstance (value, str):
    if isinstance (value, bytes):
        return unicode_to_latex (str (value))
    if isinstance (value, Markup):
        return value.latex ()
    raise ValueError ('don\'t know how to render %r into latex' % value)


def render_html (value):
    if isinstance (value, int):
        #return unicode (value)
        return str (value)
    #if isinstance (value, unicode):
    if isinstance (value, str):
        return html_escape (value)
    #if isinstance (value, str):
    if isinstance (value, bytes):
        return html_escape (str (value))
    if isinstance (value, Markup):
        return value.html ()
    raise ValueError ('don\'t know how to render %r into HTML' % value)



class Formatter (object):
    r"""Substituted items are delimited by pipes |likethis|. This works well in
    both HTML and Latex. If `israw`, the non-substituted template text is
    returned verbatim; otherwise, it is escaped.

    We have a special hack. If the substituted item is specified as
    |texturl:foo|, the key "foo" will be looked in `item` and output as a link
    whose text value is the same as its URL: i.e.

       <a href="http://...">http://...</a>

    This particular tactic is needed to work with textual URLs in LaTeX, since
    the \url{} and \href{} commands redefine character codes such that the
    standard LaTeX escaping mechanism is inappropriate. In particular, URLs
    with tildes were breaking.

    """
    def __init__ (self, renderer, israw, text):
        from re import split
        pieces = split (r'(\|[^|]+\|)', text)

        def process (piece):
            if len (piece) and piece[0] == '|':
                return True, piece[1:-1]
            return False, piece

        self.tmplinfo = [process (p) for p in pieces]
        self.renderer = renderer
        self.israw = israw

    def _handle_one (self, tmpldata, item):
        issubst, text = tmpldata

        if not issubst:
            if self.israw:
                return text
            return self.renderer (text)

        try:
            if text.startswith ('texturl:'):
                thing = item.get (text[8:])
                thing = MupLink (thing, thing)
            else:
                thing = item.get (text)
            return self.renderer (thing)
        except ValueError as e:
            # raise ValueError ((u'while rendering field "%s" of item %s: %s' \
            #                    % (text, item, e)).encode ('utf-8'))
            raise ValueError ((u'while rendering field "%s" of item %s: %s' \
                               % (text, item, e)))
    def __call__ (self, item):
        return ''.join (self._handle_one (d, item) for d in self.tmplinfo)


# Utilities for dealing with publications.

def parse_ads_cites (pub):
    from time import mktime

    if not pub.has ('adscites'):
        return None

    try:
        a = pub.adscites.split ()[:2]
        y, m, d = [int (x) for x in a[0].split ('/')]
        lastupdate = int (mktime ((y, m, d, 0, 0, 0, 0, 0, 0)))
        cites = int (a[1])
    except Exception:
        warn ('cannot parse adscites entry "%s"', pub.adscites)
        return None

    return Holder (lastupdate=lastupdate, cites=cites)


def canonicalize_name (name):
    """Convert a name into "canonical" form, by which I mean something like "PKG
    Williams". The returned string uses a nonbreaking space between the two
    pieces.

    I handle spaces in surnames by replacing them with underscores. Hopefully
    none of my coauthors will ever have an underscore in their names.

    TODO: handle "Surname, First Middle" etc.
    TODO: also Russian initials: Yu. G. Levin
    """

    bits = name.strip ().split ()
    surname = bits[-1].replace ('_', ' ')
    rest = bits[:-1]
    abbrev = []

    for item in rest:
        for j,char in enumerate(item):
            if char.isupper () or char == '-':
                abbrev.append (char)
            #Handle uncapitalized hyphenated names:
            elif j > 0:
                if item[j-1] == '-' and (not char.isupper()):
                    abbrev.append (char) #char.upper())

    #return ''.join (abbrev) + nbsp + surname
    nameout = surname +',' + nbsp + '. '.join (abbrev)+'.'
    # Clean up case of someone having a hyphenated first name:
    bits = nameout.strip ().split ('. -. ')
    nameout = '.-'.join(bits)

    return nameout


def surname (name):
    return name.strip ().split ()[-1].replace ('_', ' ')

def not_surname (name):
    return " ".join(name.strip ().split ()[:-1]).replace ('_', ' ')


def best_url (item):
    #from urllib2 import quote
    from urllib.parse import quote

    if item.has ('bibcode'):
        return 'http://ui.adsabs.harvard.edu/abs/' + quote (item.bibcode)
    if item.has ('doi'):
        return 'http://dx.doi.org/' + quote (item.doi)
    if item.has ('url'):
        return item.url
    if item.has ('arxiv'):
        return 'http://arxiv.org/abs/' + quote (item.arxiv)

    return None


def cite_info (oitem, context):
    """Create a Holder with citation text from a publication item. This can then
    be fed into a template however one wants. The various computed fields are
    are Unicode or Markups.

    `oitem` = original item; not to be modified
    `aitem` = augmented item; = oitem + new fields
    """

    aitem = oitem.copy ()

    # Canonicalized authors with bolding of self and underlining of advisees.
    cauths = [canonicalize_name (a) for a in oitem.authors.split (';')]

    aitem.nsf_full_authors = MupJoin (', ', cauths)

    myidx = int (oitem.mypos) - 1
    cauths[myidx] = MupBold (cauths[myidx])

    advposlist = oitem.get ('advpos', '')
    if len (advposlist):
        for i in [int (x) - 1 for x in advposlist.split (',')]:
            cauths[i] = MupUnderline (cauths[i])

    aitem.full_authors = MupJoin (', ', cauths)

    # --------------------------------------------------------------
    # Make a full authors list with semicolons and & at end:
    if len(cauths) == 1:
        aitem.full_authors_semi = cauths[0]
    if len(cauths) == 2:
        aitem.full_authors_semi = MupJoin (' & ', cauths)
    else:
        aitem.full_authors_semi = MupJoin('; ', cauths[:-1])
        aitem.full_authors_semi = MupJoin('; & ', [aitem.full_authors_semi, cauths[-1]])


    # --------------------------------------------------------------

    # Short list of authors, possibly abbreviating my name.
    #sauths = [surname (a)+", "+not_surname(a) for a in oitem.authors.split (';')]
    sauths = [surname (a)  for a in oitem.authors.split (';')]
    if context.my_abbrev_name is not None:
        sauths[myidx] = context.my_abbrev_name

    #print "sauths:", sauths

    if len (advposlist):
        for i in [int (x) - 1 for x in advposlist.split (',')]:
            sauths[i] = MupUnderline (sauths[i])

    # Like canonicalized name scheme instead:
    if len (sauths) == 1:
        aitem.short_authors = cauths[0] #sauths[0]
    elif len (sauths) == 2:
        aitem.short_authors = MupJoin (' & ', cauths) #sauths)
    elif (len (sauths) >= 3) & (len (sauths) <= 5):
        aitem.short_authors = MupJoin (', ', cauths[:-1]) #sauths)
        aitem.short_authors = MupJoin(', & ', [aitem.short_authors, cauths[-1]])
    else:
        #aitem.short_authors = MupJoin (' ', [sauths[0], 'et' + nbsp + 'al.'])
        sauthsstr = MupJoin (', ', cauths[0:3])
        aitem.short_authors = MupJoin (', ', [sauthsstr, 'et' + nbsp + 'al.'])


        if ((context.my_abbrev_name is not None) & (myidx > 2)):
            sauths[myidx] = MupBold(sauths[myidx])
            sauthsstr = aitem.short_authors
            aitem.short_authors = MupJoin (', ', [sauthsstr, 'including '])
            sauthsstr = aitem.short_authors
            aitem.short_authors = MupJoin (' ', [sauthsstr, sauths[myidx]])


    # --------------------------------------------------------------

    # Short list of authors, for IN PREP PUBLICATIONS: possibly abbreviating my name.
    sprepauths = [surname (a)  for a in oitem.authors.split (';')]
    if context.my_abbrev_name is not None:
        sprepauths[myidx] = context.my_abbrev_name

    if len (advposlist):
        for i in [int (x) - 1 for x in advposlist.split (',')]:
            sprepauths[i] = MupUnderline (sprepauths[i])

    # Like canonicalized name scheme instead:
    if len (sprepauths) == 1:
        sprepauthsstr = cauths[0]
        aitem.short_prep_authors =  MupJoin (', ', [sprepauthsstr, 'et' + nbsp + 'al.'])
    elif len (sprepauths) == 2:
        sprepauthsstr = MupJoin (', ', cauths[0:2])
        aitem.short_prep_authors = MupJoin (', ', [sprepauthsstr, 'et' + nbsp + 'al.'])
    elif (len (sprepauths) >= 3):
        sprepauthsstr = MupJoin (', ', cauths[0:3])
        aitem.short_prep_authors = MupJoin (', ', [sprepauthsstr, 'et' + nbsp + 'al.'])


        if ((context.my_abbrev_name is not None) & (myidx > 2)):
            sprepauths[myidx] = MupBold(sprepauths[myidx])
            sprepauthsstr = aitem.short_prep_authors
            aitem.short_prep_authors = MupJoin (', ', [sprepauthsstr, 'including '])
            sprepauthsstr = aitem.short_prep_authors
            aitem.short_prep_authors = MupJoin (' ', [sprepauthsstr, sauths[myidx]])

    # --------------------------------------------------------------

    if oitem.refereed == 'y':
        aitem.refereed_mark = u'»'
    else:
        aitem.refereed_mark = u''

    # Title with replaced quotes, for nesting in double-quotes, and
    # optionally-bolded for first authorship.
    aitem.quotable_title = MupText(oitem.title.replace (u'“', u'‘').replace (u'”', u'’'))
    #words_title = aitem.quotable_title.split(' ')
    #aitem.quotable_title = MupJoin (' ', words_title)


    # try:
    #     print "aitem.title=", aitem.title
    # except:
    #     pass
    # try:
    #     print "aitem.quotable_title=", aitem.quotable_title
    # except:
    #     pass

    if myidx == 0:
        aitem.bold_if_first_title = MupBold (oitem.title)
    else:
        aitem.bold_if_first_title = oitem.title

    # Pub year and nicely-formatted date
    try:
        aitem.year, aitem.month = map (int, oitem.pubdate.split ('/'))
        aitem.pubdate = u'%d%s%s' % (aitem.year, nbsp, months[aitem.month - 1])
    except:
        tmp = oitem.pubdate.split ('/')
        aitem.year = tmp[0]
        aitem.month = int(tmp[1])
        aitem.pubdate = u'%s%s%s' % (aitem.year, nbsp, months[aitem.month - 1])

    # Template-friendly citation count
    citeinfo = parse_ads_cites (oitem)
    if citeinfo is not None and citeinfo.cites > 0:
        aitem.citecountnote = u' [%d]' % citeinfo.cites
        aitem.citecountnotelonger = u' [citations: %d]' % citeinfo.cites
    else:
        aitem.citecountnote = u''
        aitem.citecountnotelonger = u''

    # Make citation to have commas:
    citetmp = aitem.cite.split(' ')
    citetmp_orig = citetmp
    citetmp2 = ', '.join(citetmp)
    #aitem.cite = MupJoin (', ', citetmp)
    # Clean up any underscores to force spaces:
    citetmp = citetmp2.split('_')
    aitem.cite = MupJoin(' ', citetmp)

    # Chunk the cite to get stuff:
    citetmp = citetmp_orig
    try:
        tmpjourn = ' '.join(citetmp[0].split("_"))
        if tmpjourn.lower() == 'apj':
            fulljourn = 'The Astrophysical Journal'
        elif tmpjourn.lower() == 'apjs':
            fulljourn = 'The Astrophysical Journal Supplementary Series'
        #
        elif tmpjourn.lower() == 'apjl':
            fulljourn = 'The Astrophysical Journal Letters'
        elif tmpjourn.lower() == 'mnras':
            fulljourn = 'The Monthly Notices of the Royal Astronomical Society'
        #
        elif tmpjourn.lower() == 'araa':
            fulljourn = 'Annual Review of Astronomy \& Astrophysics,'
        #
        elif tmpjourn.lower() == 'aj':
            fulljourn = 'The Astronomical Journal'
        #
        elif (tmpjourn.lower() == 'pasp') | (tmpjourn.lower() == '\pasp'):
            fulljourn = 'The Publications of the Astronomical Society of the Pacific'
        elif (tmpjourn.lower() == '\procspie') | (tmpjourn.lower() == 'procspie'):
            fulljourn = 'Proceedings of SPIE'

        else:
            fulljourn = tmpjourn
        fulljournal = fulljourn
        volume = 'v. '+citetmp[1]
        pages = 'p. '+citetmp[2]
        nsfcite = fulljournal+', '+volume+', '+pages

        aitem.nsfcite = nsfcite
    except:
        tmpjourn = ''.join(citetmp[0].split("arXiv:"))
        aitem.nsfcite = 'ArXiv e-prints: '+tmpjourn


    # Citation text with link
    url = best_url (oitem)
    aitem.adsurl = url
    if url is None:
        aitem.lcite = aitem.cite
    else:
        aitem.lcite = MupLink (url, aitem.cite)

    # Title with link
    if url is None:
        aitem.title_link = aitem.title
    else:
        aitem.title_link = MupLink (url, aitem.title)

    # Other links for the web pub list
    #from urllib2 import quote as urlquote
    from urllib.parse import quote as urlquote

    aitem.abstract_link = u''
    aitem.preprint_link = u''
    aitem.official_link = u''
    aitem.other_link = u''

    if oitem.has ('bibcode'):
        aitem.abstract_link = MupLink ('http://ui.adsabs.harvard.edu/abs/' + urlquote (oitem.bibcode),
                                      'abstract')

    if oitem.has ('arxiv'):
        aitem.preprint_link = MupLink ('http://arxiv.org/abs/' + urlquote (oitem.arxiv),
                                      'preprint')

    if oitem.has ('doi'):
        aitem.official_link = MupLink ('http://dx.doi.org/' + urlquote (oitem.doi),
                                      'official')

    if oitem.has ('url') and not oitem.has ('doi'):
        aitem.other_link = MupLink (oitem.url, oitem.kind)

    return aitem


def compute_cite_stats (pubs):
    """Compute an h-index and other stats from the known publications."""
    from time import gmtime

    stats = Holder ()
    stats.refpubs = 0
    stats.refcites = 0
    stats.reffirstauth = 0
    stats.reffirstauthcites = 0
    cites = []
    dates = []

    for pub in pubs:
        if pub.refereed == 'y':
            stats.refpubs += 1
            if int (pub.mypos) == 1:
                stats.reffirstauth += 1

        citeinfo = parse_ads_cites (pub)
        if citeinfo is None:
            continue
        if citeinfo.cites < 1:
            continue

        cites.append (citeinfo.cites)
        dates.append (citeinfo.lastupdate)

        if pub.refereed == 'y':
            stats.refcites += citeinfo.cites

            if int (pub.mypos) == 1:
                stats.reffirstauthcites += citeinfo.cites


    if not len (cites):
        stats.meddate = 0
        stats.hindex = 0
    else:
        ranked = sorted (cites, reverse=True)
        index = 0

        while index < len (ranked) and ranked[index] >= index + 1:
            index += 1

        dates = sorted (dates)
        stats.meddate = dates[len (dates) // 2]
        stats.hindex = index

    stats.year, stats.month, stats.day = gmtime (stats.meddate)[:3]
    stats.monthstr = months[stats.month - 1]
    stats.italich = MupItalics ('h')
    #stats.adslink = MupLink ('http://labs.adsabs.harvard.edu/adsabs', 'ADS')
    stats.adslink = MupLink ('http://ui.adsabs.harvard.edu/', 'ADS')
    return stats



def partition_pubs (pubs):
    groups = Holder ()
    groups.all = []
    groups.refereed = []
    groups.refpreprint = []
    groups.non_refereed = []
    groups.all_formal = []
    groups.all_non_refereed = []
    groups.informal = []

    groups.first = []
    groups.contrib = []

    groups.prep = []
    groups.prepsub = []

    for pub in pubs:
        refereed = (pub.refereed == 'y')
        refpreprint = (pub.get ('refpreprint', 'n') == 'y')
        formal = (pub.get ('informal', 'n') == 'n')
        # we assume refereed implies formal.

        try:
            prep = (pub.get ('prep', 'n') == 'y')
            prepsub = (pub.get ('prepsub', 'n') == 'y')
        except:
            prep = False
            prepsub = False


        first = (pub.mypos == '1')

        #print pub.mypos

        if ((not prep) & (not prepsub)):
            groups.all.append (pub)

        if first & (not prep) & (not prepsub) & (refereed | refpreprint):
            #print "is first"
            groups.first.append (pub)
        elif (not first) & (not prep) & (not prepsub) & (refereed | refpreprint):
            #print "is contrib"
            groups.contrib.append (pub)
        elif prep:
            groups.prep.append (pub)
        elif prepsub:
            groups.prepsub.append (pub)
        # else:
        #     #

        if formal:
            groups.all_formal.append (pub)

        if refereed:
            groups.refereed.append (pub)
        elif refpreprint:
            groups.refpreprint.append (pub)
        else:
            groups.all_non_refereed.append (pub)

            if formal:
                groups.non_refereed.append (pub)
            else:
                groups.informal.append (pub)

    groups.all_rev = groups.all[::-1]
    groups.refereed_rev = groups.refereed[::-1]
    groups.refpreprint_rev = groups.refpreprint[::-1]
    groups.non_refereed_rev = groups.non_refereed[::-1]
    groups.informal_rev = groups.informal[::-1]

    groups.first = groups.first[::-1]
    groups.contrib = groups.contrib[::-1]
    return groups


#
def compute_team_talks (talks):

    collabs = {}

    for talk in talks:


        try:
            team = talk.collab
            quantity = 1
            year = talk.year
        except Exception as e:
            die ('error processing outcome of team talk <%s>: %s', talk, e)

        if team not in collabs:
            unit = 'talk'
            meeting_unit = 'meeting'
            lastyear = year
            collabs[team] = (quantity, unit, meeting_unit, lastyear)
        else:
            q0, unit, meeting_unit, lastyear = collabs[team]
            if q0 >= 1:
                unit = 'talks'
                meeting_unit = 'meetings'
            if year > lastyear:
                lastyear = year
            collabs[team] = (q0 + quantity, unit, meeting_unit, lastyear)

    # return sorted((Holder (collab=k, unit=v[1], collab_meet_unit=v[2],
    #                     total=unicode (v[0]), lastyear=v[3])
    #                 for (k, v) in collabs.iteritems ()),
    #                     key=lambda h: h.lastyear, reverse=True)
    return sorted((Holder (collab=k, unit=v[1], collab_meet_unit=v[2],
                        total=str (v[0]), lastyear=v[3])
                    for (k, v) in collabs.items ()),
                        key=lambda h: h.lastyear, reverse=True)

# Utilities for dealing with allocated observing time. Namely, we total up the
# time allocated for each telescope as PI.

def compute_observing_experience (observing):
    allocs = {}
    facil_inst_list = []

    for obs in observing:

        amount = obs.get ('time')
        if amount is None:
            die ('no "nights" for obs %s', obs)

        try:
            facil = obs.facil
            facil_desc = obs.facil_desc
            inst = obs.inst
            facil_inst = facil+': '+inst
            quantity, units = amount.split ()
            quantity = float (quantity)
        except Exception as e:
            die ('error processing outcome of obs <%s>: %s', obs, e)

        if facil_inst not in allocs:
                allocs[facil_inst] = (facil, facil_desc, inst, quantity, units)
                facil_inst_list.append(facil_inst)
        else:
            facil, facil_desc, inst, q0, u0 = allocs[facil_inst]
            if u0 != units:
                die ('disagreeing time units for %s: both "%s" and "%s"',
                     facil_inst, u0, units)
            allocs[facil_inst] = (facil, facil_desc, inst, q0 + quantity, u0)

    #print "allocs=", allocs

    allocs_out = {}
    for facil_inst in facil_inst_list:
        facil, facil_desc, inst, quantity, units = allocs[facil_inst]
        if (quantity).is_integer():
            quantity = int(quantity)

        if units == 'nght':
            if quantity > 1:
                units = 'nights'
            else:
                units = 'night'


        if facil not in allocs_out:
            #inst_list = inst+' ('+unicode(quantity)+' '+units+')'
            inst_list = inst+' ('+str(quantity)+' '+units+')'
            allocs_out[facil] = (facil_desc, inst_list)
        else:
            facil_desc, inst_list = allocs_out[facil]
            #inst_list_new = inst+' ('+unicode(quantity)+' '+units+')'
            inst_list_new = inst+' ('+str(quantity)+' '+units+')'
            allocs_out[facil] = (facil_desc, inst_list+', '+inst_list_new)


    # return sorted ((Holder (facil=k, facil_desc=v[0], inst_list=v[1])
    #                 for (k, v) in allocs_out.iteritems ()),
    #                key=lambda h: h.facil)
    return sorted ((Holder (facil=k, facil_desc=v[0], inst_list=v[1])
                    for (k, v) in allocs_out.items ()),
                   key=lambda h: h.facil)

def compute_time_allocations (props):
    allocs = {}

    for prop in props:
        if prop.get ('mepi', 'n') != 'y':
            continue # self as PI only

        if prop.get ('accepted', 'n') != 'y':
            continue # only accepted ones!

        amount = prop.get ('award')
        if amount is None:
            amount = prop.get ('request')
        if amount is None:
            die ('no "award" or "request" for proposal %s', prop)

        try:
            facil = prop.facil
            quantity, units = amount.split ()
            quantity = float (quantity)
        except Exception as e:
            die ('error processing outcome of proposal <%s>: %s', prop, e)

        if facil not in allocs:
            allocs[facil] = (quantity, units)
        else:
            q0, u0 = allocs[facil]
            if u0 != units:
                die ('disagreeing time units for %s: both "%s" and "%s"',
                     facil, u0, units)
            allocs[facil] = (q0 + quantity, u0)

    # return sorted ((Holder (facil=k, total=unicode (v[0]), unit=v[1])
    #                 for (k, v) in allocs.iteritems ()),
    #                key=lambda h: h.facil)
    return sorted ((Holder (facil=k, total=str (v[0]), unit=v[1])
                    for (k, v) in allocs.items ()),
                   key=lambda h: h.facil)

# Utilities for dealing with public code repositories

def process_repositories (items):
    #from urllib2 import quote as urlquote
    from urllib.parse import quote as urlquote
    repos = []

    for i in items:
        if i.section != 'repo':
            continue
        if i.get ('skip', 'n') == 'y':
            continue
        if i.usercommits == '0':
            continue

        repo = i.copy ()
        repos.append (repo)

        if i.service == 'github':
            repo.linkname = MupLink ('https://github.com/' + urlquote (i.name), i.name)
        else:
            repo.linkname = i.name

        repo.commit_frac = '%.0f%%' % (100. * int (i.usercommits) / int (i.allcommits))
        if repo.commit_frac == '0%':
            repo.commit_frac = '<1%'

        repo.luc_year, repo.luc_month, repo.luc_day = [int (x) for x in i.lastusercommit.split ('/')]
        repo.date = '%04d %s' % (repo.luc_year, months[repo.luc_month - 1])
        repo._datekey = repo.luc_year * 10000 + repo.luc_month * 100 + repo.luc_day

    return sorted (repos, key=lambda r: r._datekey)


# Commands for templates

def cmd_cite_stats (context, template):
    info = compute_cite_stats (context.pubgroups.all_formal)
    return Formatter (context.render, False, slurp_template (template)) (info)

#
def cmd_cite_stats_tex (context, template):
    info = compute_cite_stats (context.pubgroups.all_formal)
    return Formatter (context.render, True, slurp_template (template)) (info)

def cmd_format (context, *inline_template):
    inline_template = ' '.join (inline_template)
    context.cur_formatter = Formatter (context.render, True, inline_template)

    # Every time reset alt, flag check:
    context.cur_formatter_alt = None
    context.format_alt_flag_check = None
    return ''

def cmd_format_alt (context, *inline_template):
    inline_template = ' '.join (inline_template)
    context.cur_formatter_alt = Formatter (context.render, True, inline_template)

    if inline_template.strip() == 'None':
        context.cur_formatter_alt = None

    return ''

def cmd_format_alt_flag_check (context, flag_to_check):
    context.format_alt_flag_check = flag_to_check

    if flag_to_check.strip() == 'None':
        context.format_alt_flag_check = None

    return ''

def cmd_my_abbrev_name (context, *text):
    context.my_abbrev_name = ' '.join (text)
    return ''


def cmd_pub_list (context, group):
    if context.cur_formatter is None:
        die ('cannot use PUBLIST command before using FORMAT')

    pubs = context.pubgroups.get (group)
    npubs = len (pubs)

    # Put something in here to sort by pub year/month?

    for num, pub in enumerate (pubs):
        info = cite_info (pub, context)
        info.number = num + 1
        info.rev_number = npubs - num
        yield context.cur_formatter (info)

def cmd_obsexp_list(context, sections):
    if context.cur_formatter is None:
        die ('cannot use OBSEXPLIST command before using FORMAT')

    for info in context.obs_exp:
        yield context.cur_formatter (info)


def cmd_talloc_list (context):
    if context.cur_formatter is None:
        die ('cannot use TALLOCLIST command before using FORMAT')

    for info in context.time_allocs:
        yield context.cur_formatter (info)

def cmd_team_talk_list (context, sections):
    if context.cur_formatter is None:
        die ('cannot use TEAMTALKLIST command before using FORMAT')

    num = 0
    for info in context.team_talks_counts:
        num += 1

    #num = 2
    for i,info in enumerate(context.team_talks_counts):
        if i < num-1:
            end=';'
        else:
            end=''
        info.end = end
        yield context.cur_formatter (info)


def _rev_misc_list (context, sections, gate):
    if context.cur_formatter is None:
        die ('cannot use RMISCLIST* command before using FORMAT')

    sections = frozenset (sections.split (','))

    for item in context.items[::-1]:
        if item.section not in sections:
            continue
        if not gate (item):
            continue

        if context.format_alt_flag_check is not None:
            if item.__dict__[context.format_alt_flag_check].strip() == '':
                yield context.cur_formatter_alt (item)
            else:
                yield context.cur_formatter (item)
        else:
            yield context.cur_formatter (item)



def cmd_rev_misc_list (context, sections):
    return _rev_misc_list (context, sections, lambda i: True)

def cmd_rev_misc_list_if (context, sections, gatefield):
    """Same a RMISCLIST, but only shows items where a certain item
    is True. XXX: this kind of approach could get out of hand
    quickly."""
    return _rev_misc_list (context, sections,
                           lambda i: i.get (gatefield, 'n') == 'y')

def cmd_rev_misc_list_if_not (context, sections, gatefield):
    return _rev_misc_list (context, sections,
                           lambda i: i.get (gatefield, 'n') != 'y')

#
def cmd_rev_misc_list_switch (context, sections, gatefield, case):
    """Same a RMISCLIST, but only shows items where a certain item
    is True. XXX: this kind of approach could get out of hand
    quickly."""
    return _rev_misc_list (context, sections,
                           lambda i: i.get (gatefield, 'n') == case)

def cmd_rev_repo_list (context, sections):
    if context.cur_formatter is None:
        die ('cannot use RREPOLIST command before using FORMAT')

    sections = frozenset (sections.split (','))

    for item in context.repos[::-1]:
        if item.section not in sections:
            continue
        yield context.cur_formatter (item)


def cmd_today (context):
    """Note the trailing period in the output."""
    from time import time, localtime

    # This is a little bit gross.
    yr, mo, dy = localtime (time ())[:3]
    text = '%s%s%d,%s%d.' % (months[mo - 1], nbsp, dy, nbsp, yr)
    return context.render (text)

def cmd_today_invert (context):
    """No trailing period in the output, DD MM YYYY"""
    from time import time, localtime

    # This is a little bit gross.
    yr, mo, dy = localtime (time ())[:3]
    text = '%d %s %d' % (dy, months[mo - 1], yr)
    return context.render (text)


def setup_processing (render, datadir):
    context = Holder ()
    context.render = render
    context.items = list (load (datadir))
    context.pubs = [i for i in context.items if i.section == 'pub']
    context.pubgroups = partition_pubs (context.pubs)
    context.props = [i for i in context.items if i.section == 'prop']
    context.time_allocs = compute_time_allocations (context.props)


    context.team_talks = [i for i in context.items if ((i.section == 'talk') & \
                    (i.get ('venue', 'n') == 'team'))]
    context.team_talks_counts = compute_team_talks (context.team_talks)

    context.observing = [i for i in context.items if i.section == 'obs']
    context.obs_exp = compute_observing_experience (context.observing)

    context.repos = process_repositories (context.items)
    context.cur_formatter = None
    context.cur_formatter_alt = None
    context.format_alt_flag_check = None

    context.my_abbrev_name = None

    commands = {}
    commands['CITESTATS'] = cmd_cite_stats
    commands['CITESTATS_TEX'] = cmd_cite_stats_tex

    commands['FORMAT'] = cmd_format
    commands['FORMAT_ALT'] = cmd_format_alt
    commands['FORMAT_ALT_FLAG_CHECK'] = cmd_format_alt_flag_check

    commands['MYABBREVNAME'] = cmd_my_abbrev_name
    commands['PUBLIST'] = cmd_pub_list
    commands['TALLOCLIST'] = cmd_talloc_list


    commands['OBSEXPLIST'] = cmd_obsexp_list

    commands['TEAMTALKLIST'] = cmd_team_talk_list

    commands['RMISCLIST'] = cmd_rev_misc_list
    commands['RMISCLIST_IF'] = cmd_rev_misc_list_if
    commands['RMISCLIST_IF_NOT'] = cmd_rev_misc_list_if_not
    commands['RMISCLIST_CASE'] = cmd_rev_misc_list_switch
    commands['RREPOLIST'] = cmd_rev_repo_list
    commands['TODAY.'] = cmd_today
    commands['TODAY'] = cmd_today_invert

    return context, commands


# ADS citation counts

# this custom format returns exactly the ADS citation count
_ads_url_tmpl = (r'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?'
                 r'bibcode=%(bibcode)s&data_type=Custom&format=%%25c&nocookieset=1')


class ADSCountError (Exception):
    def __init__ (self, fmt, args):
        super (ADSCountError, self).__init__ (fmt % args)


def get_ads_cite_count_OLD (bibcode):
    #import httplib
    import http.client
    #from urllib2 import urlopen, quote, URLError
    from urllib.request import urlopen
    from urllib.parse import quote
    from urllib.error import URLError
    url = _ads_url_tmpl % {'bibcode': quote (bibcode)}
    lastnonempty = None

    if bibcode != '':
        try:
            for line in urlopen (url):
                line = line.strip ()
                if len (line):
                    lastnonempty = line
        #except httplib.BadStatusLine as e:
        except http.client.BadStatusLine as e:
            raise ADSCountError ('received bad HTTP status: %r', e)
        except URLError as e:
            raise ADSCountError (str (e))

        if lastnonempty is None:
            raise ADSCountError ('got only empty lines')

        if lastnonempty.startswith ('Retrieved 0 abstracts'):
            raise ADSCountError ('no such bibcode')

        try:
            count = int (lastnonempty)
        except Exception:
            raise ADSCountError ('got unexpected final line %r', lastnonempty)
    else:
        count = 0

    return count


#
def get_ads_cite_count (bibcode):

    import json
    import requests
    import os.path

    mod_path = os.path.abspath(os.path.dirname(__file__))
    token_file = os.path.join(mod_path, "adsabs_token.txt")
    with open(token_file) as f:
        token=f.readline()

    #import httplib
    import http.client
    #from urllib2 import urlopen, quote, URLError
    from urllib.request import urlopen
    from urllib.parse import quote
    from urllib.error import URLError
    url = _ads_url_tmpl % {'bibcode': quote (bibcode)}
    n_cites = None

    if bibcode != '':
        try:
            # to pass a dictionary in the request payload, convert it to a string first using the json package
            bibcode = {"bibcodes":[bibcode]}
            r = requests.post("https://api.adsabs.harvard.edu/v1/metrics", \
                             headers={"Authorization": "Bearer " + token, "Content-type": "application/json"}, \
                             data=json.dumps(bibcode))
            try:
                n_cites = r.json()['citation stats']['total number of citations']
            except:
                print(r.json())
                #raise ValueError
                n_cites = 0
        except URLError as e:
            raise ADSCountError (str (e))

        if n_cites is None:
            raise ADSCountError ('got only empty lines')

        try:
            count = int (n_cites)
        except Exception:
            raise ADSCountError ('got unexpected final line %r', n_cites)
    else:
        count = 0

    return count





# Bootstrapping from a BibTeX file. This is currently aimed 100% at
# ADS-generated BibTeX; it'd be nice to make it more general.

def _write_with_wrapping (outfile, key, value):
    # we assume whitespace is fungible.

    if '#' in value:
        #print >>outfile, ('%s = "%s"' % (key, value)).encode ('utf-8')
        #print(('%s = "%s"' % (key, value)).decode("utf-8"), file=outfile)
        print(('%s = "%s"' % (key, value)), file=outfile)
        return

    bits = value.split ()
    ofs = len (key) + 2
    head = 0
    tail = 0

    while tail < len (bits):
        ofs += len (bits[tail]) + 1
        tail += 1

        if ofs > 78:
            if head == 0:
                s = '%s = %s' % (key, ' '.join (bits[head:tail]))
            else:
                s = '  %s' % (' '.join (bits[head:tail]))
            #print >>outfile, s.encode ('utf-8')
            #print(s.decode("utf-8"), file=outfile)
            print(s, file=outfile)
            head = tail
            ofs = 1

    if head == 0:
        s = '%s = %s' % (key, ' '.join (bits[head:tail]))
    elif head < len (bits):
        s = '  %s' % (' '.join (bits[head:tail]))
    else:
        return

    #print >>outfile, s.encode ('utf-8')
    #print(s.decode("utf-8"), file=outfile)
    print(s, file=outfile)


def _bib_fixup_author (text):
    text = text.replace ('{', '').replace ('}', '').replace ('~', ' ')
    surname, rest = text.split (',', 1)
    return rest + ' ' + surname.replace (' ', '_')


_bib_months = {'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
               'may': '05',  'jun': '06',  'jul': '07',  'aug': '08',
               'sep': '09',  'oct': '10',  'nov': '11',  'dec': '12'}

_bib_journals = {'\\aap': 'A&Ap', '\\aj': 'AJ', '\\apj': 'ApJ',
                 '\\apjl': 'ApJL', '\\apjs': 'ApJS', '\\araa': 'ARA&A',
                 '\\mnras': 'MNRAS', '\\pasa': 'PASA'}


def _bib_cite (rec):
    if 'journal' in rec and 'volume' in rec and 'pages' in rec:
        return ' '.join ((rec['journal'], rec['volume'], rec['pages']))

    if 'series' in rec and 'volume' in rec and 'pages' in rec:
        return ' '.join ((rec['series'], rec['volume'], rec['pages']))

    if rec.get ('type') == 'inproceedings' and 'booktitle' in rec and 'pages' in rec:
        return u'proceedings of “%s”, %s' % (rec['booktitle'], rec['pages'])

    if rec.get ('journal') == u'ArXiv e-prints' and 'eprint' in rec:
        return u'arXiv:' + rec['eprint']

    return None


class BibCustomizer (object):
    # By "customize" the bibtexparser module just means post-processing. These
    # are a bunch of ad-hoc hacks based on what ADS gives us.

    def __init__ (self, mysurname):
        self.mylsurname = mysurname.lower ()

    def __call__ (self, rec):
        from bibtexparser.customization import author, type, convert_to_unicode
        rec = type (convert_to_unicode (rec))

        for key in rec.keys ():
            val = rec.get (key)
            val = (val
                   .replace ('{\\nbsp}', nbsp)
                   .replace ('``', u'“')
                   .replace ("''", u'”'))
            rec[key] = val

        if 'journal' in rec:
            rec['journal'] = _bib_journals.get (rec['journal'].lower (),
                                                rec['journal'])

        rec = author (rec)

        if 'author' in rec:
            newauths = []

            for idx, text in enumerate (rec['author']):
                text = text.replace ('{', '').replace ('}', '').replace ('~', ' ')
                surname, rest = text.split (',', 1)
                if surname.lower () == self.mylsurname:
                    #rec['wl_mypos'] = unicode (idx + 1)
                    rec['wl_mypos'] = str (idx + 1)
                newauths.append (rest + ' ' + surname.replace (' ', '_'))

            rec['author'] = '; '.join (newauths)

        rec['wl_cite'] = _bib_cite (rec)
        return rec


def bootstrap_bibtex (bibfile, outdir, mysurname):
    import os.path

    # XXX we assume heavily that we're dealing with ADS bibtex.

    from bibtexparser.bparser import BibTexParser
    bp = BibTexParser (bibfile, customization=BibCustomizer (mysurname))
    byyear = {}

    for rec in bp.get_entry_list ():
        year = rec.get ('year', 'noyear')

        if year in byyear:
            outfile = byyear[year]
        else:
            outfile = open (os.path.join (outdir, year + 'p.txt'), 'w')
            byyear[year] = outfile
            # print >>outfile, '# -*- conf -*-'
            # print >>outfile, '# XXX for all records, refereed status is guessed crudely'
            print('# -*- conf -*-', file=outfile)
            print('# XXX for all records, refereed status is guessed crudely', file=outfile)
        #print >>outfile, '\n[pub]'
        print('\n[pub]', file=outfile)

        if 'title' in rec:
            _write_with_wrapping (outfile, 'title', rec['title'])
        else:
            #print >>outfile, 'title = ? # XXX no title for this record'
            print('title = ? # XXX no title for this record', file=outfile)

        if 'author' in rec:
            _write_with_wrapping (outfile, 'authors', rec['author'])
        else:
            #print >>outfile, 'authors = ? # XXX no authors for this record'
            print('authors = ? # XXX no authors for this record', file=outfile)

        if 'wl_mypos' in rec:
            _write_with_wrapping (outfile, 'mypos', rec['wl_mypos'])
        else:
            #print >>outfile, 'mypos = 0 # XXX cannot determine "mypos" for this record'
            print('mypos = 0 # XXX cannot determine "mypos" for this record', file=outfile)

        if 'year' in rec and 'month' in rec:
            _write_with_wrapping (outfile, 'pubdate',
                                  rec['year'] + '/' +
                                  _bib_months.get (rec['month'].lower (),
                                                   rec['month']))
        elif 'year' in rec:
            #print >>outfile, 'pubdate = %s/01 # XXX actual month unknown' % rec['year']
            print('pubdate = %s/01 # XXX actual month unknown' % rec['year'], file=outfile)
        else:
            #print >>outfile, 'pubdate = ? # XXX no year and month for this record'
            print('pubdate = ? # XXX no year and month for this record', file=outfile)

        if 'id' in rec:
            _write_with_wrapping (outfile, 'bibcode', rec['id'])

        if 'eprint' in rec:
            _write_with_wrapping (outfile, 'arxiv', rec['eprint'])

        if 'doi' in rec:
            _write_with_wrapping (outfile, 'doi', rec['doi'])

        refereed = 'journal' in rec
        #print >>outfile, 'refereed = %s' % 'ny'[refereed]
        print('refereed = %s' % 'ny'[refereed], file=outfile)

        cite = _bib_cite (rec)
        if cite is not None:
            _write_with_wrapping (outfile, 'cite', cite)
        else:
            #print >>outfile, 'cite = ? # XXX cannot infer citation text'
            print('cite = ? # XXX cannot infer citation text', file=outfile)

    #for f in byyear.itervalues ():
    for f in iter(byyear.values()):
        f.close ()

#
def bootstrap_bibtex_alphabetical (bibfile, outdir, mysurname):
    import os.path

    # XXX we assume heavily that we're dealing with ADS bibtex.

    from bibtexparser.bparser import BibTexParser
    bp = BibTexParser (bibfile, customization=BibCustomizer (mysurname))
    byyear = {}


    outfile = open (os.path.join (outdir,  'nsf_pub_log.txt'), 'w')

    # print >>outfile, '# -*- conf -*-'
    # print >>outfile, '# XXX for all records, refereed status is guessed crudely'
    print('# -*- conf -*-', file=outfile)
    print('# XXX for all records, refereed status is guessed crudely', file=outfile)




    for rec in bp.get_entry_list ():

        year = rec.get ('year', 'noyear')

        #print >>outfile, '\n[pub]'
        print('\n[pub]', file=outfile)

        if 'title' in rec:
            _write_with_wrapping (outfile, 'title', rec['title'])
        else:
            #print >>outfile, 'title = ? # XXX no title for this record'
            print('title = ? # XXX no title for this record', file=outfile)

        if 'author' in rec:
            _write_with_wrapping (outfile, 'authors', rec['author'])
        else:
            #print >>outfile, 'authors = ? # XXX no authors for this record'
            print('authors = ? # XXX no authors for this record', file=outfile)

        if 'wl_mypos' in rec:
            _write_with_wrapping (outfile, 'mypos', rec['wl_mypos'])
        else:
            #print >>outfile, 'mypos = 0 # XXX cannot determine "mypos" for this record'
            print('mypos = 0 # XXX cannot determine "mypos" for this record', file=outfile)

        if 'year' in rec and 'month' in rec:
            _write_with_wrapping (outfile, 'pubdate',
                                  rec['year'] + '/' +
                                  _bib_months.get (rec['month'].lower (),
                                                   rec['month']))
        elif 'year' in rec:
            #print >>outfile, 'pubdate = %s/01 # XXX actual month unknown' % rec['year']
            print('pubdate = %s/01 # XXX actual month unknown' % rec['year'], file=outfile)
        else:
            #print >>outfile, 'pubdate = ? # XXX no year and month for this record'
            print('pubdate = ? # XXX no year and month for this record', file=outfile)

        if 'id' in rec:
            _write_with_wrapping (outfile, 'bibcode', rec['id'])

        if 'eprint' in rec:
            _write_with_wrapping (outfile, 'arxiv', rec['eprint'])

        if 'doi' in rec:
            _write_with_wrapping (outfile, 'doi', rec['doi'])

        refereed = 'journal' in rec
        #print >>outfile, 'refereed = %s' % 'ny'[refereed]
        print('refereed = %s' % 'ny'[refereed], file=outfile)

        cite = _bib_cite (rec)
        if cite is not None:
            _write_with_wrapping (outfile, 'cite', cite)
        else:
            #print >>outfile, 'cite = ? # XXX cannot infer citation text'
            print('cite = ? # XXX cannot infer citation text', file=outfile)

    #for f in byyear.itervalues ():
    for f in iter(byyear.values()):
        f.close ()
