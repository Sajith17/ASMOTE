# ASMOTE

## Overview

**Aspect Sentiment Multiple Opinion Triplet Extraction (ASMOTE)** aims to find triplets that include aspects, sentiments, and various opinions. When the model extracts a triplet, it gives us a complete picture of all the opinions related to a specific aspect, helping us understand exactly why that aspect has a particular sentiment.

I utilized **TensorFlow 2** for its robust deep learning capabilities, enabling efficient development, training, and deployment of the sentiment analysis model. Additionally, **Flask** was chosen to showcase ASMOTE due to its lightweight, modular framework, ensuring an intuitive and user-friendly web interface.

Some challenges I faced included **extracting multi-word aspects and opinions**. To address this, I employed named entity recognition. Another challenge was **ensuring valid pairings of aspect and opinion**, which I tackled by training a dedicated classifier.

Features I hope to implement in the future:

- **Implement an attention-based model or transformer model for aspect opinion extraction to improve accuracy over named entity recognition (NER)**
- **Manually augment sentences with negation and modifiers to handle negation and modifiers and increase accuracy over them.**
