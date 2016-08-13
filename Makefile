# Path to folder containing archive data (index.json, epub/)
ARCHIVE=res/fimfarchive-20160525

EBOOK_CONVERT=ebook-convert

# The path to EVERY epub, relative to archive/epub/
EPUBS=$(patsubst $(ARCHIVE)/epub/%,%,$(shell find $(ARCHIVE)/epub/ -name *.epub))
TXTS=$(addprefix build/,$(EPUBS:.epub=.txt))
ANSI_TXTS=$(TXTS:.txt=.ansi.txt)
SENTIMENT_JSONS=$(TXTS:.txt=.sentiment.json)
WORDS_JSONS=$(TXTS:.txt=.words.json)
AGG_FILE=build/aggregated.json
IDX_FILE=$(ARCHIVE)/index.json
PLOTS=$(addprefix build/plot/, \
	char_senti_by_month.png char_senti_by_month_smooth.png \
	text_senti_by_month.png text_senti_by_month_smooth.png \
	char_senti_by_storyarc.png text_senti_by_storyarc.png \
	char_senti_by_storyarc_short.png char_senti_by_storyarc_med.png \
	char_senti_by_storyarc_long.png \
	text_senti_by_storyarc_binned.png \
	character_mentions_in_a_sentence.png character_mentions_in_a_story.png \
	story_lengths.png story_lengths_lin_bins.png \
	story_lengths_sentences.png char_pairs.png \
	most_common_words.png most_common_words_aj.png \
	most_common_words_fs.png most_common_words_pp.png \
	most_common_words_rd.png most_common_words_ra.png \
	most_common_words_ts.png \
	most_common_nonwords.png most_common_nonwords_aj.png \
	most_common_nonwords_fs.png most_common_nonwords_pp.png \
	most_common_nonwords_rd.png most_common_nonwords_ra.png \
	most_common_nonwords_ts.png \
	rating_vs_length.png rating_vs_length_linear.png \
	rating_vs_title_length.png rating_vs_title_length_linear.png \
	rating_vs_date.png rating_vs_date_linear.png \
	most_common_titles.png story_status_distr.png rating_vs_char.png \
	rating_vs_char_all.png \
)
TEXT_STATS=$(addprefix build/stats/, word_frequencies.json)


all: $(PLOTS) $(TEXT_STATS)

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
%.png: $(IDX_FILE) $(AGG_FILE)
	mkdir -p $(dir $@)
	./src/plot.py $(IDX_FILE) $(AGG_FILE) $@

# Generate stats:
build/stats/%.json: $(AGG_FILE)
	mkdir -p $(dir $@)
	./src/text_stats.py $(AGG_FILE) $(notdir $@) > $@

clean-json:
	find build/ -name *.json | xargs rm -f

clean-plots:
	rm -f $(PLOTS)

# Remove only empty json files (they were likely corrupted)
clean-empty:
	find build/ -name *.json -empty | xargs rm -f

# Handy notes for tracking make progress:
# Obtain number of files of a specific type generated via (e.g.)
# find build/ -name *.json | wc -l

.PHONY: clean-json clean-plots

# Preserve all "intermediate" targets
.SECONDARY: $(TXTS) $(ANSI_TXTS) $(WORDS_JSONS) $(SENTIMENT_JSONS) $(AGG_FILE)
