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

    def _build_init(self, section: str, section_description: str) -> str:
        text = f"""
Manuale di Frascati - Sezione: {section}
Definizione: {section_description}
Compito: Compila la sezione "{section}" per un progetto di ricerca e sviluppo seguendo il Manuale di Frascati. Enfatizza gli aspetti innovativi e di R&S, dimostrando come i risultati ottenuti siano nuovi o significativamente migliorati rispetto allo stato dell'arte."""
        return text

    def _build_positive_examples(self, positive_context: str, positive_answer: str) -> str:
        text = f"""
Esempio:
Contesto: {positive_context}
Risposta: {positive_answer}"""
        return text

    def _build_context(self, context, section, positive_answer) -> str:
        len_pos_ans = int(np.mean([len(pa) for pa in positive_answer]))
        text = f"""
Istruzioni:
1. Basati principalmente sul contesto fornito.
2. Se necessario, integra con informazioni verosimili e pertinenti.
3. Evidenzia in MAIUSCOLO le parti non presenti nel contesto.
4. Mantieni una lunghezza che sta tra {len_pos_ans} e {int(len_pos_ans * 1.5)} caratteri.
5. Rispondi con {section}: risposta, nient'altro.

Contesto attuale: {context}

Risposta:
        """
        return text

    def _build_prompt(self,
                      section: str,
                      section_description: str,
                      positive_context: list[str],
                      positive_answer: list[str],
                      context: str) -> str:
        prompt = ""

        prompt += self._build_init(section, section_description).strip() + "\n\n"

        for el in zip(positive_context, positive_answer):
            prompt += self._build_positive_examples(el[0], el[1]).strip() + "\n\n"

        prompt += self._build_context(context=context,
                                      section=section,
                                      positive_answer=positive_answer).strip()



        return prompt


    def __build_prompt(self,
                      section: str,
                      section_description: str,
                      positive_context: list[str],
                      positive_answer: list[str],
                      context: str
                      ) -> str:

        prompt = str()

        prompt += self._build_init(section,
                                   section_description)
        for el in zip(positive_context, positive_answer):
            prompt += self._build_positive_examples(el[0], el[1])

        prompt += self._build_context(context=context,
                                      section=section,
                                      positive_answer=positive_answer)

        prompt = prompt.strip()

        return prompt

    def generate_prompt(self,
                        section: str,
                        positive_columns: Union[str, list[str]],
                        positive_context: Union[str, list[str]],
                        context: str) -> str:

        if section not in self.frascati_dict:
            raise ValueError(f"Section '{section}' not found. Please add it using add_section().")

        section_description = self.frascati_dict[section]

        if type(positive_columns) == str:
            positive_columns = [positive_columns]

        for col in positive_columns:

            self.positive_examples[positive_columns.index(col)] = dict(self.frascati_file[[self.frascati_section_col,
                                                                                           col]].values)
        positive_answers = [self.positive_examples[positive_columns.index(col)][section] for col in positive_columns]

        return self._build_prompt(section,
                                  section_description,
                                  positive_context,
                                  positive_answers,
                                  context)

    def add_positive_example(self, column_name, positive_context) -> None:
        self.positive_examples[column_name] = {
            'examples': dict(self.frascati_file[[self.frascati_section_col, column_name]].values),
            'context': positive_context
        }


if __name__ == '__main__':
    fpg = FrascatiPromptGenerator(
        excel_file=r"C:\Users\ManuelP\OneDrive - Vodafone Group\Desktop\DocumentiPaoloPNRR\Note da Integrare_rev 13.xlsx",
        sheet_name="FRASCATI")

    fpg.generate_prompt(section="ABSTRACT",
                        positive_columns='Topic- Review\nprogramma 1 - \nDEVICE INTEGRATION PRODUCT  - MCD30',
                        positive_context="ciaociao",
                        context="contesto")
