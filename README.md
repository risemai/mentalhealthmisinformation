---
title: Misinformation Detection and Publich Engagement 
emoji: 🔍
colorFrom: green
colorTo: indigo
sdk: docker
pinned: false
license: mit
---
# 
# Misinformation Detection and Publich Engagement 

A professional-grade Streamlit application for detecting health misinformation in YouTube videos using a multimodal AI pipeline.

## Features

- **Home Dashboard** — Architecture overview, model stats, and mission statement
- **Dataset Analysis** — Interactive metric progress bars, epoch progression, confusion matrix, and training convergence charts for the MHMisinfo benchmark
- **Custom Dataset** — Real-time YouTube video analysis with:
  - Video metadata cards (Views, Likes, Comments, Duration)
  - Misinfo detection with gauge chart and per-stream scores
  - VADER / DistilBERT sentiment analysis of comments
  - Keyword extraction and diverging comparison chart

## Model

Built on [rocky250/MHMisinfo](https://huggingface.co/rocky250/MHMisinfo):
- **Encoder**: BiGRU with attention
- **Base LM**: DistilRoBERTa
- **Accuracy**: 85.9% | **ROC-AUC**: 78.8%

## Usage

1. Open the **Video Lab** page
2. Paste a YouTube URL
3. Enter your [YouTube Data API v3 key](https://console.cloud.google.com/)
4. Click **Analyse**

## Local Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```
