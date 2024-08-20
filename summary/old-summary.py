import sys
import math
import bs4 as bs
import urllib.request
import re
import PyPDF2
import nltk
from nltk.stem import WordNetLemmatizer 
import spacy

nltk.download('wordnet')

nlp = spacy.load('en_core_web_sm')
lemmatizer = WordNetLemmatizer() 

def frequency_matrix(sentences):
    freq_matrix = {}
    stopWords = nlp.Defaults.stop_words

    for sent in sentences:
        freq_table = {}
        words = [word.text.lower() for word in sent if word.text.isalnum()]
       
        for word in words:  
            word = lemmatizer.lemmatize(word)
            if word not in stopWords:
                if word in freq_table:
                    freq_table[word] += 1
                else:
                    freq_table[word] = 1

        freq_matrix[sent[:15]] = freq_table

    return freq_matrix

def tf_matrix(freq_matrix):
    tf_matrix = {}

    for sent, freq_table in freq_matrix.items():
        tf_table = {}
        total_words_in_sentence = len(freq_table)
        for word, count in freq_table.items():
            tf_table[word] = count / total_words_in_sentence

        tf_matrix[sent] = tf_table

    return tf_matrix

def sentences_per_words(freq_matrix):
    sent_per_words = {}

    for sent, f_table in freq_matrix.items():
        for word, count in f_table.items():
            if word in sent_per_words:
                sent_per_words[word] += 1
            else:
                sent_per_words[word] = 1

    return sent_per_words

def idf_matrix(freq_matrix, sent_per_words, total_sentences):
    idf_matrix = {}

    for sent, f_table in freq_matrix.items():
        idf_table = {}
        for word in f_table.keys():
            idf_table[word] = math.log10(total_sentences / float(sent_per_words[word]))

        idf_matrix[sent] = idf_table

    return idf_matrix

def tf_idf_matrix(tf_matrix, idf_matrix):
    tf_idf_matrix = {}

    for (sent1, f_table1), (sent2, f_table2) in zip(tf_matrix.items(), idf_matrix.items()):
        tf_idf_table = {}
        for (word1, tf_value), (word2, idf_value) in zip(f_table1.items(), f_table2.items()):  
            tf_idf_table[word1] = float(tf_value * idf_value)

        tf_idf_matrix[sent1] = tf_idf_table

    return tf_idf_matrix

def score_sentences(tf_idf_matrix):
    sentenceScore = {}

    for sent, f_table in tf_idf_matrix.items():
        total_tfidf_score_per_sentence = 0
        total_words_in_sentence = len(f_table)
        for word, tf_idf_score in f_table.items():
            total_tfidf_score_per_sentence += tf_idf_score

        if total_words_in_sentence != 0:
            sentenceScore[sent] = total_tfidf_score_per_sentence / total_words_in_sentence

    return sentenceScore

def average_score(sentence_score):
    total_score = 0
    for sent in sentence_score:
        total_score += sentence_score[sent]

    average_sent_score = (total_score / len(sentence_score))

    return average_sent_score

def create_summary(sentences, sentence_score, threshold):
    summary = ''

    for sentence in sentences:
        if sentence[:15] in sentence_score and sentence_score[sentence[:15]] >= (threshold):
            summary += " " + sentence.text
        
    return summary

text = "The rapid advancement of technology over the past few decades has revolutionized nearly every aspect of modern life. From the way we communicate to how we work, shop, and entertain ourselves, technology has become an integral part of our daily routines. The rise of the internet, in particular, has opened up new avenues for information sharing, learning, and collaboration, enabling people from all corners of the globe to connect and interact in ways that were previously unimaginable. One of the most significant impacts of technology has been on the workforce. Automation and artificial intelligence have transformed industries, leading to increased efficiency and productivity but also raising concerns about job displacement and the future of work. As machines become more capable of performing tasks that were once the domain of humans, there is growing debate over how to balance technological progress with the need to protect workers' livelihoods. Education, too, has been profoundly affected by technology. Online learning platforms and digital resources have made education more accessible to people around the world, breaking down barriers to entry and providing opportunities for lifelong learning. However, this shift has also highlighted the digital divide, as those without access to technology or the internet are at risk of being left behind. In healthcare, technological advancements have led to breakthroughs in medical research, diagnostics, and treatment. Telemedicine has emerged as a powerful tool, allowing patients to consult with healthcare providers remotely, which has been particularly valuable during the COVID-19 pandemic. However, the increasing reliance on digital health tools has also raised concerns about data privacy and the security of sensitive information. As we look to the future, it is clear that technology will continue to play a central role in shaping our world. While it offers tremendous potential for improving quality of life, it also presents challenges that must be addressed. Ensuring that the benefits of technology are shared equitably and that ethical considerations are taken into account will be crucial in navigating the complex landscape of the digital age."

original_words = text.split()
original_words = [w for w in original_words if w.isalnum()]
num_words_in_original_text = len(original_words)

text = nlp(text)

sentences = list(text.sents)
total_sentences = len(sentences)

freq_matrix = frequency_matrix(sentences)

tf_matrix = tf_matrix(freq_matrix)

num_sent_per_words = sentences_per_words(freq_matrix)

idf_matrix = idf_matrix(freq_matrix, num_sent_per_words, total_sentences)

tf_idf_matrix = tf_idf_matrix(tf_matrix, idf_matrix)

sentence_scores = score_sentences(tf_idf_matrix)

threshold = average_score(sentence_scores)

summary = create_summary(sentences, sentence_scores, 1.3 * threshold)

print(summary)