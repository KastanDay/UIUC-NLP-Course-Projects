TAC KBP RUFES 2020 Evaluation Annotations
June 2, 2021

1. Introduction

Text Analysis Conference (TAC) is a series of workshops organized by
the National Institute of Standards and Technology (NIST). TAC was
developed to encourage research in natural language processing (NLP)
and related applications by providing a large test collection, common
evaluation procedures, and a forum for researchers to share their
results.

The goal of the TAC Knowledge Base Population (KBP) Recognizing Ultra
Fine-grained EntitieS (RUFES) task is to extract mentions of
pre-defined entity types from any language, and cluster together
mentions of the same entity. RUFES 2020 challenges systems to
recognize name, nominal, and pronominal mentions of entities in news
articles, from an ontology with over 200 types that cover a variety of
topics in the news.  More information about the TAC KBP 2020 RUFES
task can be found at https://tac.nist.gov/2020/KBP/RUFES/.
 
This release contains source data and gold references of 106
Washington Post news articles annotated for the evaluation.

2. Directory Structure

./readme.txt -- this file

./data/rsd/ -- "raw source data" (rsd) plain text form of the news
               article
./data/ltf/ -- "logical text format" (ltf) derived from the rsd

./annotations/ -- annotated references including
    gold.tab -- annotations of all 106 documents (union of two below)
    minus_feedback_gold.tab -- annotations of 10 documents on which
    			       feedback was provided to participants
                	       on their first submission
    feedback_gold.tab -- annotations with 10 feedback documents
    		      	 removed

./docs/ -- documentation related to the evaluation, including
    KBP2020TaskSpec_V1.0.pdf
    RUFES2020AnnotationGuidelines.v1.1_draft.pdf
    RUFES2020OntologyV1.2.xlsx

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

The format of each annotation output file conforms to the format as
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
ID's may have non-alphanumeric characters such as punctuations. There
is no tab or leading/trailing white space for any entity ID.

Field 6: entity types: a set of type indicators for the mention,
multiple types at all levels are separated by the “;” delimiter.

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

@2012-2019 Washington Post, @2020-2021 National Institute of Standards
and Technology 
