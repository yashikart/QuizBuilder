import traceback
import xml.etree.ElementTree as et
import random
import re
import pke


from xml.dom import minidom
from flashtext import KeywordProcessor
from pprint import pprint

def get_noun(summary):
    extractor = pke.unsupervised.TextRank()
    extractor.load_document(summary, language='en')
    pos = {'NOUN','ADJ', 'ADV'}
    extractor.candidate_selection(pos=pos)
    # 4. build the Multipartite graph and rank candidates using random walk,
    #    alpha controls the weight adjustment mechanism, see TopicRank for
    #    threshold/method parameters.
    extractor.candidate_weighting(window=3,
                              pos=pos,
                              top_percent=0.80)
    keyphrases = extractor.get_n_best(n=20)
    results = []
    for scored_keywords in keyphrases:
        for keyword in scored_keywords:
            if isinstance(keyword, str):
                results.append(keyword)
    return results



def get_sentences_for_keyword(keywords, sentences):
    keyword_processor = KeywordProcessor()
    keyword_sentences = {}
    for word in keywords:
        keyword_sentences[word] = []
        keyword_processor.add_keyword(word)
    for sentence in sentences:
        keywords_found = keyword_processor.extract_keywords(sentence)
        for key in keywords_found:
            keyword_sentences[key].append(sentence)

    for key in keyword_sentences.keys():
        values = keyword_sentences[key]
        values = sorted(values, key=len, reverse=True)
        keyword_sentences[key] = values
    return keyword_sentences



def get_fill_in_the_blanks(sentence_mapping):
    out={"title":"Fill in the blanks for these sentences with matching words at the top"}
    blank_sentences = []
    processed = []
    keys=[]
    for key in sentence_mapping:
        if len(sentence_mapping[key])>0:
            sent = sentence_mapping[key][0]
            # Compile a regular expression pattern into a regular expression object, which can be used for matching and other methods
            insensitive_sent = re.compile(re.escape(key), re.IGNORECASE)
            no_of_replacements =  len(re.findall(re.escape(key),sent,re.IGNORECASE))
            line = insensitive_sent.sub(' _________ ', sent)
            if (sentence_mapping[key][0] not in processed) and no_of_replacements<2:
                blank_sentences.append(line)
                processed.append(sentence_mapping[key][0])
                keys.append(key)
    out["sentences"]=blank_sentences[:20]
    out["keys"]=keys[:20]
    return out


def placing_elemnts_fill_blanks(fill_in_the_blanks):

    root = et.Element("div")

    heading = et.Element("h2")
    heading.text = fill_in_the_blanks['title']

    keywords = et.Element("var")
    keywords.set('style', 'color: red;')

    all_keys = fill_in_the_blanks['keys']
    random.shuffle(all_keys)

    for index, blank in enumerate(all_keys):
        child = et.Element("span")
        child.text = blank
        keywords.append(child)
    # Add a comma after each element except the last one
        if index < len(all_keys) - 1:
            comma = et.Element("span")
            comma.text = ', '
            keywords.append(comma)



    sentences = et.Element("ol")
    sentences.set('style', 'color:brown;')
    for sentence in fill_in_the_blanks['sentences']:
        child=et.Element("li")
        child.text = sentence
        sentences.append(child)
        sentences.append(et.Element("br"))

    heading_content = et.Element("h4")

    root.append(heading)
    heading_content.append(keywords)
    heading_content.append(sentences)
    root.append(heading_content)

    xmlstr = et.tostring(root)
    xmlstr = xmlstr.decode("utf-8")
    prettyxmlstr = minidom.parseString(et.tostring(root)).toprettyxml(indent="   ")
    return prettyxmlstr


