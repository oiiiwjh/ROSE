---
title: "Attention Is All You Need"
authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Lukasz Kaiser", "Illia Polosukhin"]
date: "2017-06-12"
arxiv_id: "1706.03762"
url: "https://arxiv.org/abs/1706.03762"
tags: [transformer, attention, sequence-to-sequence, machine-translation]
status: analyzed
rating: 5
---

## 概要总结

本文提出了 Transformer 架构，完全基于注意力机制（Self-Attention）构建序列到序列模型，彻底摒弃了循环和卷积结构。Transformer 在机器翻译任务上取得了当时的 SOTA 结果（WMT 2014 英德 28.4 BLEU、英法 41.8 BLEU），同时训练速度显著提升。这一架构后来成为 NLP 乃至整个深度学习领域的基础范式。

## Abstract

The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.

## 摘要翻译

主流的序列转换模型基于复杂的循环或卷积神经网络，采用编码器-解码器架构。性能最优的模型还通过注意力机制连接编码器和解码器。我们提出了一种全新的简洁网络架构——Transformer，完全基于注意力机制，彻底摒弃了循环和卷积结构。在两个机器翻译任务上的实验表明，该模型在翻译质量上更优，同时具有更好的并行性，所需训练时间显著减少。我们的模型在 WMT 2014 英德翻译任务上达到 28.4 BLEU，比已有最佳结果（包括集成模型）提升超过 2 个 BLEU。在 WMT 2014 英法翻译任务上，模型仅在 8 块 GPU 上训练 3.5 天即建立了 41.8 BLEU 的新单模型 SOTA，训练成本仅为文献中最佳模型的一小部分。我们还展示了 Transformer 良好的泛化能力，将其成功应用于英语成分句法分析任务。
