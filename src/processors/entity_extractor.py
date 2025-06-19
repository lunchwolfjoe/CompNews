import spacy
from typing import Dict, List
import logging
import json

class EntityExtractor:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.enabled = True
        except Exception as e:
            self.logger.warning(f"Could not load spaCy model: {e}. Entity extraction will be disabled.")
            self.enabled = False

    def extract(self, article: Dict) -> Dict:
        if not self.enabled:
            # If spaCy is not available, skip entity extraction
            article["entities"] = json.dumps({})
            return article
            
        try:
            content = article.get("content", "")
            if not content:
                article["entities"] = json.dumps({})
                return article
                
            doc = self.nlp(content)
            
            # Extract named entities
            entities = {}
            for ent in doc.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                if ent.text not in entities[ent.label_]:
                    entities[ent.label_].append(ent.text)
            
            # Store as JSON string for SQLite compatibility
            article["entities"] = json.dumps(entities)
            return article
            
        except Exception as e:
            self.logger.error(f"Error during entity extraction: {e}")
            article["entities"] = json.dumps({})
            return article 