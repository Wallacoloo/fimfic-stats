# Path to folder containing archive data (index.json, epub/)
ARCHIVE=res/fimfarchive-20160525

EBOOK_CONVERT=ebook-convert

# The path to EVERY epub, relative to archive/epub/
EPUBS=$(patsubst $(ARCHIVE)/epub/%,%,$(shell find $(ARCHIVE)/epub/ -name *.epub))
TXTS=$(addprefix build/,$(EPUBS:.epub=.txt))
SENTIMENTS=$(TXTS:.txt=.sentiment.json)
AGG_FILE=build/aggregated.json
PLOTS=$(addprefix build/plot/, \
	char_senti_by_month.png char_senti_by_month_smooth.png \
	text_senti_by_month.png text_senti_by_month_smooth.png \
)


all: $(PLOTS)

# Convert epub to txt
build/%.txt: $(ARCHIVE)/epub/%.epub
	@mkdir -p $(dir $@)
	$(EBOOK_CONVERT) $< $@ > /dev/null

# Create sentiment analysis 
%.sentiment.json: %.txt
	./src/analyze_senti.py $^ $@

# Aggregate analyses
$(AGG_FILE): $(SENTIMENTS)
	./src/aggregate.py $(ARCHIVE)/index.json build/ $@

# Generate plots:
%.png: $(AGG_FILE)
	mkdir -p $(dir $@)
	./src/plot.py $(AGG_FILE) $@

clean-json:
	find build/ -name *.json | xargs rm -f

# Handy notes for tracking make progress:
# Obtain number of files of a specific type generated via (e.g.)
# find build/ -name *.json | wc -l

.PHONY: clean-json
