TAC KBP RUFES 2020 Sample Annotations V1.1
January 14, 2021

0. Revisions

V1.1: Removed invalid type (PER.SituationalRole) from all annotations
in V1.0 and changed a type for one mention.

1. Introduction

This release contains a set of 50 fully annotated news articles,
selected from the same period (from January 2012 to October 2013) as
the development data set “TAC KBP RUFES2020 Development Data”
(released November 12, 2020).

This annotated dataset has approximately 25k words. The average word
count (exluding the date) for each article is about 500 words with an
upper limit of 655 words. Long articles were truncated at a paragraph
boundary before annotation to fit the limit.

2. Directory Structure

./readme.txt -- this file

./data/rsd/ -- "raw source data" (rsd) plain text form of the news
               article
./data/ltf/ -- "logical text format" (ltf) derived from the rsd

./docs/ -- containing ontology and annotation guidelines

./annotations/edl.tab -- annotation output

3. File Format Description

Each rsd file is organized into paragraphs with the first paragraph
being the article title and the second paragraph being the article
publishing date and time in GMT. The remaining paragraphs contain the
original text of the news article excluding any non-text markups and
URL links. A line feed terminates each paragraph.

Each ltf.xml file contains a fully segmented and tokenized version of
the corresponding rsd file. Segments (paragraphs) and the tokens
(words) are marked off by XML tags (SEG and TOKEN), with "id"
attributes (which are only unique within a given XML file) and
character offset attributes relative to the corresponding rsd.txt
file.

The format of the annotation output file conforms to the format as
specified in the task specifications. The output contains one line for
each entity mention where each line has the following tab-delimited
fields:

Filed 1: system run ID

Field 2: mention ID: unique for each entity mention. 

Field 3: mention string: the full name of a named mention, or the
single head string of a nominal or pronominal mention.

Field 4: mention justification: an ID for a document in the source
corpus from which the mention was extracted, the starting UTF-8
character offset of the mention, and the ending UTF-8 character offset
of the mention; in the format: <document ID>:<mention start
offset>-<mention end offset>.

Field 5: entity ID: unique for each entity in the document. Annotators
may have used a canonical name for the entity ID or a more descriptive
phrase when a named mention is not available in the document. Some
ID's may have non-alphanumeric characters such as puctuations. There
is no tab or no leading/trailing white space for any entity ID.

Field 6: entity types: a set of type indicators for the mention,
multiple types at all levels are separated by “;” delimiter.

Field 7: mention type: “NAM” (for name mentions), “NOM” (for nominal
mentions), or “PRO” (for pronominal mentions).

Field 8: a confidence value. For the annotation, the value is 1.0

3. File Name Convention

Each original Washington Post news article has a unique document
ID. The publishing date (YYYYMMDD) and the source (WAPO) are combined
with the document id for the file name for each news article. An
example is as follows: 

20130529_WAPO_919ac0d0-bf35-11e2-9b09-1638acc3942e.{rsd.txt, ltf.xml}

4. Copyright

@2012-2019 Washington Post, @2020 National Institute of Standards and Technology
