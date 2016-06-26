# Path to folder containing archive data (index.json, epub/)
ARCHIVE=res/fimfarchive-20160525

EBOOK_CONVERT=ebook-convert

# The path to EVERY epub, relative to archive/epub/
EPUBS=$(patsubst $(ARCHIVE)/epub/%,%,$(shell find $(ARCHIVE)/epub/ -name *.epub))
TXTS=$(addprefix build/,$(EPUBS:.epub=.txt))
SENTIMENT_JSONS=$(TXTS:.txt=.sentiment.json)
WORDS_JSONS=$(TXTS:.txt=.words.json)
AGG_FILE=build/aggregated.json
PLOTS=$(addprefix build/plot/, \
	char_senti_by_month.png char_senti_by_month_smooth.png \
	text_senti_by_month.png text_senti_by_month_smooth.png \
	char_senti_by_storyarc.png text_senti_by_storyarc.png \
	char_senti_by_storyarc_short.png char_senti_by_storyarc_med.png \
	char_senti_by_storyarc_long.png \
	text_senti_by_storyarc_binned.png \
	character_mentions_in_a_sentence.png character_mentions_in_a_story.png \
	story_lengths.png story_lengths_lin_bins.png \
	char_pairs.png \
	most_common_words.png most_common_words_aj.png \
	most_common_words_fs.png most_common_words_pp.png \
	most_common_words_rd.png most_common_words_ra.png \
	most_common_words_ts.png \
	most_common_nonwords.png most_common_nonwords_aj.png \
	most_common_nonwords_fs.png most_common_nonwords_pp.png \
	most_common_nonwords_rd.png most_common_nonwords_ra.png \
	most_common_nonwords_ts.png \
)


all: $(PLOTS)

# Convert epub to txt (it may contain unicode)
build/%.txt: $(ARCHIVE)/epub/%.epub
	@mkdir -p $(dir $@)
	$(EBOOK_CONVERT) $< $@ > /dev/null

# Replace all unicode characters with their nearest ascii equivalent (we want this to detect quotation marks, etc easily).
%.ansi.txt: %.txt
	unidecode $^ > $@

# Create sentiment analysis 
%.sentiment.json: %.ansi.txt
	./src/analyze_senti.py $^ $@

# Word-association analysis
%.words.json: %.ansi.txt
	./src/analyze_words.py $^ $@

# Aggregate analyses
$(AGG_FILE): $(SENTIMENT_JSONS) $(WORDS_JSONS)
	./src/aggregate.py $(ARCHIVE)/index.json build/ $@

# Generate plots:
%.png: $(AGG_FILE)
	mkdir -p $(dir $@)
	./src/plot.py $(AGG_FILE) $@

clean-json:
	find build/ -name *.json | xargs rm -f

clean-plots:
	rm -f $(PLOTS)

# Handy notes for tracking make progress:
# Obtain number of files of a specific type generated via (e.g.)
# find build/ -name *.json | wc -l

.PHONY: clean-json
