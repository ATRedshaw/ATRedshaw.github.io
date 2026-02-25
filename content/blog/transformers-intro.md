# Introduction to Transformers in NLP

The Transformer architecture, introduced in the paper "Attention Is All You Need" (2017), has become the standard for modern NLP tasks. Unlike previous RNN-based models, Transformers process input data in parallel, allowing for significantly faster training and better handling of long-range dependencies.

## The Attention Mechanism

At the core of the Transformer is the **Self-Attention** mechanism. This allows the model to weigh the importance of different words in a sentence relative to each other.

> "The animal didn't cross the street because it was too tired."

In the sentence above, "it" refers to "the animal". Self-attention helps the model understand this relationship.

## Architecture

The Transformer consists of an Encoder and a Decoder stack.

1. **Encoder**: Processes the input sequence into a continuous representation.
2. **Decoder**: Generates the output sequence one element at a time, consuming the previous output and the encoder's representation.

## Code Example: Using Hugging Face Transformers

You can easily use pre-trained Transformer models with the `transformers` library:

```python
from transformers import pipeline

classifier = pipeline('sentiment-analysis')
result = classifier('I love using Transformers for NLP!')
print(result)
# Output: [{'label': 'POSITIVE', 'score': 0.999}]
```

## Conclusion

Transformers have paved the way for models like BERT, GPT, and T5, enabling state-of-the-art results in translation, summarization, and question answering.
