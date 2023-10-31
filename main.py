
import torch
import nltk
import pke
nltk.download('punkt')
nltk.download('brown')
nltk.download('wordnet')
from PyPDF2 import PdfReader
from nltk.tokenize import sent_tokenize
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def extraction_from_pdf(pdfpath):
    text = ''
    pdf_file = open(pdfpath, 'rb')
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def summarizer(extractedtext):

    checkpoint = "sshleifer/distilbart-cnn-12-6"

    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
    sentences = nltk.tokenize.sent_tokenize(extractedtext)
    length = 0
    chunk = ""
    chunks = []
    count = -1
    for sentence in sentences:
        count += 1
        combined_length = len(tokenizer.tokenize(sentence)) + length # add the no. of sentence tokens to the length counter

        if combined_length  <= tokenizer.max_len_single_sentence: # if it doesn't exceed
            chunk += sentence + " " # add the sentence to the chunk
            length = combined_length # update the length counter

    # if it is the last sentence
            if count == len(sentences) - 1:
                chunks.append(chunk.strip()) # save the chunk

        else:
            chunks.append(chunk.strip()) # save the chunk

    # reset
            length = 0
            chunk = ""

    # take care of the overflow sentence
            chunk += sentence + " "
            length = len(tokenizer.tokenize(sentence))

# inputs to the model
    inputs = [tokenizer(chunk, return_tensors="pt") for chunk in chunks]

    summary = " "
    for input in inputs:
        output = model.generate(**input)
        summary += tokenizer.decode(*output, skip_special_tokens=True) + "\n"

    return summary








# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    extraction_from_pdf('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
