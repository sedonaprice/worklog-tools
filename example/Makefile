# This work is dedicated to the public domain.

# Basic settings

toolsdir = ~/software_public/worklog-tools

# `make` targets are:
#
#        all - the default; create {shprice-cv,shprice-pubs}.{pdf,html}
#    summary - summarize entries
# update-ads - update ADS citation counts
#      clean - delete generated files

# Settings that probably won't need to be changed:

driver = $(toolsdir)/wltool
infos = $(wildcard *.txt)

# Rules:
all: cv.pdf pubs.pdf pubs.html

pubs.tex: $(driver) pubs.tmpl.tex $(infos)
	python $< latex  pubs.tmpl.tex >$@.new && mv -f $@.new $@

cv.tex: $(driver) cv.tmpl.tex $(infos)
	python $< latex  cv.tmpl.tex >$@.new && mv -f $@.new $@

pubs.html: $(driver) pubs.tmpl.html $(infos)
	python $< html pubs.tmpl.html >$@.new && mv -f $@.new $@


summary: $(infos)
	python $(driver) summarize

update-ads:
	python $(driver) update-cites

clean-tmp:
	-rm -f *.aux *.log *.log2 *.out

clean:
	-rm -f *.aux *.log *.log2 *.out pubs.html cv.pdf cv.tex pubs.pdf pubs.tex

%.pdf: %.tex
	@echo + making $@ -- error messages are in $*.log2 if anything goes wrong
	pdflatex $< >$*.log2
	pdflatex $< >$*.log2


# clear default make rules:
.SUFFIXES:
