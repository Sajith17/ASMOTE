import tensorflow as tf
import numpy as np
import pandas as pd
import pickle
import regex as re

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Embedding, Dense, LSTM, Bidirectional, Input
from tensorflow.keras.optimizers import Adam
from tensorflow_addons.text.crf_wrapper import CRFModelWrapper

T1, T2 = 71, 25
with open("models/tokenizer.pickle", "rb") as f:
    tokenizer = pickle.load(f)
extractor = tf.keras.models.load_model("models/extractor_model.tf")
pair_classfier = tf.keras.models.load_model("models/pair_classifier.h5")
polarity_classifier = tf.keras.models.load_model("models/polarity_classifier.h5")


def predict_triplets(sentence):
    sentences = sentence.split(".")
    sentences = [i for i in sentences if i]
    regex_sentence = [re.findall(r"\b[\'\w]+\b", i) for i in sentences]
    new_sentences = [" ".join(i) for i in regex_sentence]
    tokenized = pad_sequences(
        tokenizer.texts_to_sequences(np.array(new_sentences)), maxlen=T1, padding="post"
    )
    labels = extractor.predict(tokenized)
    pair_sent = []
    mask = []
    aspects = []
    opinions = []
    aspects_i = []
    opinions_i = []
    for i in range(len(labels)):
        aspect_indices = []
        opinion_indices = []
        current_aspect_index = []
        current_opinion_index = []
        aspect = []
        opinion = []
        current_aspect = ""
        current_opinion = ""
        for j in range(len(labels[0])):
            if labels[i][j] == 2:
                if current_aspect_index:
                    aspect_indices.append(current_aspect_index)
                    aspect.append(current_aspect)
                current_aspect_index = [j]
                current_aspect = regex_sentence[i][j] + " "
            elif labels[i][j] == 3:
                current_aspect_index.append(j)
                current_aspect += regex_sentence[i][j] + " "
            elif labels[i][j] == 4:
                if current_opinion_index:
                    opinion_indices.append(current_opinion_index)
                    opinion.append(current_opinion)
                current_opinion_index = [j]
                current_opinion = regex_sentence[i][j] + " "
            elif labels[i][j] == 5:
                current_opinion_index.append(j)
                current_opinion += regex_sentence[i][j] + " "
        if current_aspect_index:
            aspect_indices.append(current_aspect_index)
            aspect.append(current_aspect)
        if current_opinion_index:
            opinion_indices.append(current_opinion_index)
            opinion.append(current_opinion)
        for x in range(len(aspect_indices)):
            for y in range(len(opinion_indices)):
                pair_sent.append(tokenized[i])
                m = np.zeros(shape=(T1), dtype=bool)
                m[aspect_indices[x] + opinion_indices[y]] = True
                mask.append(m)
                aspects_i.append(aspect_indices[x])
                opinions_i.append(opinion_indices[y])
                aspects.append(aspect[x])
                opinions.append(opinion[y])
    if not pair_sent:
        return pair_sent
    pair_sent = np.array(pair_sent, dtype=int)
    mask = np.array(mask, dtype=bool)
    pair_pred = pair_classfier.predict([pair_sent, mask])
    aspects_i = [aspects_i[x] for x in range(len(aspects_i)) if pair_pred[x][0] >= 0.5]
    opinions_i = [
        opinions_i[x] for x in range(len(opinions_i)) if pair_pred[x][0] >= 0.5
    ]
    aspects = [aspects[x] for x in range(len(aspects)) if pair_pred[x][0] >= 0.5]
    opinions = [opinions[x] for x in range(len(opinions)) if pair_pred[x][0] >= 0.5]
    sentences = [x + y for x, y in zip(aspects, opinions)]
    tokenized_sentence = pad_sequences(
        tokenizer.texts_to_sequences(np.array(sentences)), maxlen=T2, padding="post"
    )
    y_pred = polarity_classifier.predict(tokenized_sentence)
    y_pred = [np.argmax(x) for x in y_pred]
    triplets = []
    for i in range(len(y_pred)):
        sentiment = "NEG"
        if y_pred[i] == 1:
            sentiment = "NEU"
        elif y_pred[i] == 2:
            sentiment = "POS"
        triplets.append((aspects[i], opinions[i], sentiment))
    return triplets
