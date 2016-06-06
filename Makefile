# Path to folder containing archive data (index.json, epub/)
ARCHIVE=res/fimfarchive-20160525

EBOOK_CONVERT=ebook-convert

# The path to EVERY epub, relative to archive/epub/
EPUBS=$(patsubst $(ARCHIVE)/epub/%,%,$(shell find $(ARCHIVE)/epub/ -name *.epub))
TXTS=$(addprefix build/,$(EPUBS:.epub=.txt))
SENTIMENTS=$(TXTS:.txt=.sentiment.json)


all: $(SENTIMENTS)

# Convert epub to txt
build/%.txt: $(ARCHIVE)/epub/%.epub
	@mkdir -p $(dir $@)
	$(EBOOK_CONVERT) $< $@ > /dev/null

# Create sentiment analysis 
%.sentiment.json: %.txt
	./src/analyze_senti.py $^ $@

clean-json:
	find build/ -name *.json | xargs rm -f

# Handy notes for tracking make progress:
# Obtain number of files of a specific type generated via (e.g.)
# find build/ -name *.json | wc -l

.PHONY: clean-json
