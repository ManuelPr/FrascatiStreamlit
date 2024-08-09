from typing import Union

import pandas as pd
import numpy as np

class FrascatiPromptGenerator:
    def __init__(self, frascati_df: pd.DataFrame,
                 frascati_domain_col: str, frascati_text_column: str):
        self.frascati_section_col = frascati_domain_col
        self.frascati_text_col = frascati_text_column
        self.frascati_file = frascati_df
        self.frascati_dict = dict(self.frascati_file[[self.frascati_section_col,
                                                      self.frascati_text_col]].values)
        self.positive_examples = dict()
        self.input_section = None
        self.section = None
        self.risposta = None
        self.lenghts = {'ABSTRACT': 150,
                        'DESCRIZIONE DEL PROGETTO\nObiettivi generali': 1793,
                        'STATO DELL’ARTE DEL PROGETTO': 1131,
                        'ELEMENTI DI NOVITÀ': 1323,
                        'CREATIVITÀ / OSTACOLO TECNOLOGICO': 2146,
                        'ELEMENTI DI INCERTEZZA': 1512}
        self.baseline_len = 1000

    def _build_init(self, section: str, section_description: str) -> str:
        self.baseline_len = len(section_description)
        text = f"""
Manuale di Frascati - Sezione: {section}
Definizione: {section_description}
Compito: Compila la sezione "{section}" per un progetto di ricerca e sviluppo seguendo il Manuale di Frascati. Enfatizza gli aspetti innovativi e di R&S, dimostrando come i risultati ottenuti siano nuovi o significativamente migliorati rispetto allo stato dell'arte."""
        return text

    def _build_context(self, context, section) -> str:
        try:
            len_ans = self.lenghts[section]
        except:
            len_ans = self.baseline_len*2
        text = f"""
Istruzioni:
1. Basati sul contesto attuale fornito.
2. Se necessario, integra con informazioni verosimili e pertinenti.
3. Evidenzia in MAIUSCOLO le parti non presenti nel contesto.
4. Mantieni una lunghezza che sta tra {int(len_ans*0.75)} e {int(len_ans * 1.25)} caratteri.
5. Rispondi con {section}: risposta, nient'altro.

Contesto attuale: {context}

Risposta:
        """
        return text

    def _build_prompt(self,
                      section: str,
                      section_description: str,
                      context: str) -> str:
        prompt = ""

        prompt += self._build_init(section, section_description).strip() + "\n\n"

        prompt += self._build_context(context=context,
                                      section=section).strip()

        return prompt


    def __build_prompt(self,
                      section: str,
                      section_description: str,
                      context: str
                      ) -> str:

        prompt = str()

        prompt += self._build_init(section,
                                   section_description)

        prompt += self._build_context(context=context,
                                      section=section)

        prompt = prompt.strip()

        return prompt

    def generate_prompt(self,
                        section: str,
                        context: str) -> str:

        if section not in self.frascati_dict:
            raise ValueError(f"Section '{section}' not found. Please add it using add_section().")

        section_description = self.frascati_dict[section]
        return self._build_prompt(section,
                                  section_description,
                                  context)

    def add_positive_example(self, column_name, positive_context) -> None:
        self.positive_examples[column_name] = {
            'examples': dict(self.frascati_file[[self.frascati_section_col, column_name]].values),
            'context': positive_context
        }
