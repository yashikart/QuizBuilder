import torch
from transformers import T5ForConditionalGeneration,T5Tokenizer
import xml.etree.ElementTree as ET
import random
import re
import pke


from xml.dom import minidom
from flashtext import KeywordProcessor


def question_answer_generator(sentences_with_Keywords):

    model_path = "t5/model"
    tokenizer_path = "t5/tokenizer"
    model = T5ForConditionalGeneration.from_pretrained(model_path)
    tokenizer = T5Tokenizer.from_pretrained(tokenizer_path)

    print(sentences_with_Keywords)


    out={"title":"One Line Questions"}
    out['questions'] = []
    out['answers'] = []

    for i , j in sentences_with_Keywords.items():
        key = j
        context = i
        for k in key:
            text = "context: "+context + " " + "answer: " + k + " </s>"

            encoding = tokenizer.encode_plus(text,max_length =512, padding=True, return_tensors="pt")

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

            model = model.to(device)

            input_ids,attention_mask  = encoding["input_ids"].to(device), encoding["attention_mask"].to(device)

            model.eval()
            beam_outputs = model.generate(
            input_ids=input_ids,attention_mask=attention_mask,
            max_length=72,
            early_stopping=True,
            num_beams=5,
            num_return_sequences=1)

            for beam_output in beam_outputs:
                sentence = tokenizer.decode(beam_output, skip_special_tokens=True,clean_up_tokenization_spaces=True)
                out['questions'].append(sentence.replace("question:",""))
                ans = " Ans:"+k
                out['answers'].append(ans)


    print("complete framing question and answer.....")
    return out

def templates_question(qa_genrator):

    # Create the root element
    qa = ET.Element("qa")
# Create the title element
    heading = ET.Element("h2")
    heading.text = qa_genrator['title']
    qa.append(heading)
    print("title created")
    for (question, answer) in (zip(qa_genrator['questions'], qa_genrator['answers'])):
    # Create question element
        qa_pair = ET.Element("qa")
        question_element = ET.Element("li")
        question_element.set('style', 'color:brown;')  # Use a custom attribute for formatting
        question_text_element = ET.Element("text")
        question_text_element.text = question
        question_element.append(question_text_element)

    # Create answer element
        answer_element = ET.Element("Ans")
        answer_element.set('style', 'color:blue;')  # Use a custom attribute for formatting
        answer_text_element = ET.Element("text")
        answer_text_element.text = answer
        answer_text_element.append(ET.Element("br"))
        answer_element.append(answer_text_element)

        qa_pair.append(question_element)
        qa_pair.append(answer_element)


        qa.append(qa_pair)

    xmlstr = ET.tostring(qa)
    xmlstr = xmlstr.decode("utf-8")
    prettyxmlstr = minidom.parseString(ET.tostring(qa)).toprettyxml(indent="   ")
    return prettyxmlstr










