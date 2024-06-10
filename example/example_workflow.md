
# Example workflow with worklog-tools: CV and Publication list in HTML + LaTeX

I'm eternally grateful to [Peter Williams](http://newton.cx/~peter/) for 
writing ``worklog-tools``! This package was an absolute game changer for me 
in my CV + publication list management --- see the 
[publications list](https://sedonaprice.github.io/publications.html) 
and [CV](https://sedonaprice.github.io/shprice-cv-web.pdf)
on my webpage for examples of my typical usage! 

There 
are some things I've changed in this fork's codebase to address things 
I wanted for my usage cases (how I wanted 
to specify/mark up my entries; how I wanted to split by author; 
name handling of coauthors with multi-word last names; etc).  

I've shown a number of these updates in the examples files. 

However, for information on all the other options, please see Peter's original 
documentation in the [README](../README.md) and his original 
[example files](pkgw/). 


> **Quickstart notes**:\
> Copy the example template and log files, tweak to make your own changes, 
> and don't forget to edit the ``Makefile`` with any changed/new filenames!


## Installing ``worklog-tools``

Clone this repo into a folder of your choosing (sorry no fancy conda/pip 
installs here): 
```
cd $PATH_ABOVE_WLTOOLS
git clone https://github.com/sedonaprice/worklog-tools.git
```
Most requirements should be included in a standard python installation. 

## Workflow for updating CV & Publications

### 1. Adding entries to the yearly INI log files 

(If necessary, start a new INI log file for the year in question.) 


#### A. For publications: 

##### (i) Get bibtex entries for new publications. 

I personally do an ADS search for myself 
(eg, [this search](https://ui.adsabs.harvard.edu/search/p_=0&q=%3Dauthor%3A(%22price%2C%20sedona%22%20or%20%22price%2C%20sedona%20h%22%20or%20%22price%2C%20s%20h%22%20or%20%22price%2C%20s%22)&sort=date%20desc%2C%20bibcode%20desc)), 
and then add new publications to my ADS publication library (checkboxes > 
"Add papers to library" when logged in). 
I then go to "Export > BibTeX" within my libary and copy the full output into 
a file in my directory containing my log files (e.g., ``shprice-ADS.bbl``)

*I highly recommend 
[making one](https://ui.adsabs.harvard.edu/help/libraries/), 
as you can update it on-the-fly, and I have had job applications request 
such a link!*

##### (ii) Use worklog-tools bootstrap-bibtex to parse into INI format

The subcommand ``bootstrap-bibtex`` parses 
a BibTeX file into the specific ``INI`` format ``worklog-tools`` expects. 

Within the directory containing my log files, I run 
```
$PATH_TO_WLTOOLS/wltool bootstrap-bibtex shprice-ADS.bbl Price bibtex_output
```
which runs through the specified BibTeX file, identifies my 
author position by my surname, and saves parsed ``INI`` files within 
the specified output directory (``bibtex_output/YYYYp.txt``). 


I pretty much always forget the syntax, but Peter's 
usage prompts are super helpful. (I start with ```$PATH_TO_WLTOOLS/wltool```, 
then ```$PATH_TO_WLTOOLS/wltool bootstrap-bibtex```.)


##### (iii) Copy entries into yearly log files

I then copy the parsed entries from the parsed INI files 
(eg, ``bibtex_output/YYYYp.txt``) into my log files (``YYYY.txt``). 
I use this as an opportunity to clean up weird things in the 
title or author formatting (ADS always seems to have new creative 
ways of typesetting titles, I have no idea how). 
(I also do this to get updated entries for papers that are now accepted.)

_**Note:** Within each log file, the last entries are placed **first**, so I 
typically enter things in chronological order (to ensure they show up 
in reverse chronological order, or most recent first) for my CV._



#### B. For other CV entries: 

Following the examples, add a new entry with the appropriate record type 
and fill in all relevant entries. 
I mostly copy and paste from old examples, to ensure formatting is correct. 

One tricky thing in some of my hacks: I haven't coded things in 
a way that fails gracefully when certain keys are missing. 
For talks in particular, there are often entries like 

```
extra = #
```
which is necessary to for the code to run, but means that value is empty. 
Keep these as-is, or add text as relevant! 
(Particularly note the *spaces* are 
very important for the syntax. 
I unfortunately haven't had the time to figure out a way to gracefully 
code this so missing keys don't throw errors.)


_**Note:** As with the publications, the last entries in each log file 
are placed **first**, so I 
typically enter things in chronological order (to ensure they show up 
in reverse chronological order, or most recent first) for my CV._



### 2. Updating & (re)building files 


#### A. Updating citations

Prior to running ``worklog-tools`` to generate updated files, I typically 
update the ADS citations. 

To fetch citations from ADS, you'll need to store an API token in 
``ads-token.secret`` within the directory where you're building your files 
-- you'll need an ADS user account to get one from this 
[link](https://ui.adsabs.harvard.edu/user/settings/token). 
_(Also good practice to add such a file to your ``.gitignore`` if you're 
using a shared repo!)_

Running the subcommand
```
$PATH_TO_WLTOOLS/wltool update-cites
```
within the directory containing your yearly log files will update the 
citations for each publication entry found within these files. 



#### B. Building files

Finally, I run 
```
make all
```
or for specific files, 
```
make cv.pdf
```
within the directory with my log files. 


You'll need to edit your ```Makefile``` with instructions 
on how to build new files from the template. 

> [!WARNING]  
> **This includes editing the path `toolsdir` at the top of the file.**

The existing examples are a great starting place (note the 
_html_ or _latex_ are the parsing formats, which can also 
support _markdown_). 


## Other tips: 

### Modifying files for different formatting

If I need eg a CV that includes the publication list, or a different 
way of styling the same set of information (eg, a short author list 
vs a full author list), I create a new 
template that merges/starts with elements of other examples I have. 

One thing to note is that these new templates should be added to the 
``Makefile`` to use commands such as ``make publications_short_auth.pdf`` 
that build a new document out of ``publications_short_auth.tmpl.tex``. 


> **Fork also supports Markdown**:\
> In addition to the examples with HTML and LaTeX, it is possible 
> to use Markdown templates -- which can be particularly helpful 
> if you use static site generators like [hugo](https://gohugo.io/) 
> to build websites out of template components. 
> (Largely this is the same as HTML, 
> and I personally have a bit of raw HTML in my markdown 
> publication templates.)
