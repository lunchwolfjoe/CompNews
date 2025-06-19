import spacy
from typing import Dict, List
import logging

class Summarizer:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.enabled = True
        except Exception as e:
            self.logger.warning(f"Could not load spaCy model: {e}. Summarization will be disabled.")
            self.enabled = False

    def summarize(self, article: Dict) -> Dict:
        if not self.enabled:
            # If spaCy is not available, use first 500 chars of content as summary
            content = article.get("content", "")
            summary = content[:500] + "..." if len(content) > 500 else content
            article["summary"] = summary
            return article
            
        try:
            content = article.get("content", "")
            if not content:
                article["summary"] = ""
                return article
                
            doc = self.nlp(content)
            sentences = list(doc.sents)
            
            if not sentences:
                article["summary"] = content[:500] + "..." if len(content) > 500 else content
                return article
                
            # Simple scoring: prefer sentences with more than 10 words
            scores = [len(sent) for sent in sentences]
            # Select top 3 sentences as summary
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
            summary = " ".join([sentences[i].text for i in sorted(top_indices)])  # Keep original order
            article["summary"] = summary
            return article
        except Exception as e:
            self.logger.error(f"Error during summarization: {e}")
            # Fallback to simple truncation
            content = article.get("content", "")
            article["summary"] = content[:500] + "..." if len(content) > 500 else content
            return article 