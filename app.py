import streamlit as st
import pandas as pd

from main import FrascatiPromptGenerator

def main():
    # Titolo dell'applicazione
    st.title('Frascati Prompt Generator')

    # Carica e visualizza il logo
    logo = "Frascati.jpg"  # Sostituisci con il percorso del tuo logo
    st.image(logo, width=500)  # Mostra il logo con una larghezza specificata

    # Caricamento del file Excel dall'utente
    st.info("Carica un file Excel che contiene i dati da utilizzare per generare i prompt. Seleziona il foglio e le colonne appropriate per personalizzare la generazione dei prompt.")
    uploaded_file = st.file_uploader("Carica un file Excel", type=["xlsx"])
    if uploaded_file is not None:
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names
        selected_sheet = st.selectbox("Scegli il foglio da importare", sheet_names)
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

        # Mostra le prime righe del DataFrame per una panoramica dei dati
        st.write("Visualizza i dati del foglio selezionato:")
        st.dataframe(df.head())

        # Trova la colonna del dominio predefinita
        domain_columns = [col for col in df.columns if 'dominio' in col.lower()]
        default_domain_col = domain_columns[0] if domain_columns else df.columns[0]
        domain_col = st.selectbox("Seleziona la colonna del dominio", df.columns, index=df.columns.get_loc(default_domain_col))
        st.info("Seleziona la colonna che contiene le sezioni del Manuale di Frascati.")

        # Trova la colonna di testo Frascati predefinita
        text_columns = [col for col in df.columns if 'testo' in col.lower()]
        default_text_col = text_columns[0] if text_columns else df.columns[0]
        text_col = st.selectbox("Seleziona la colonna di testo Frascati", df.columns, index=df.columns.get_loc(default_text_col))
        st.info("Seleziona la colonna che contiene il testo di ciascuna sezione del Manuale di Frascati.")

        # Selezione delle colonne di esempio positivo
        positive_cols = st.multiselect("Seleziona le colonne di esempio positivo", df.columns)
        st.info("Seleziona una o più colonne che contengono esempi positivi. Questi esempi sono utilizzati per migliorare la qualità dei prompt generati.")

        if domain_col and text_col and positive_cols:
            # Selezione delle sezioni disponibili nella colonna del dominio
            sections = df[domain_col].unique()
            selected_sections = st.multiselect("Scegli le sezioni del Manuale di Frascati", sections)
            st.info("Seleziona una o più sezioni del Manuale di Frascati a cui il prompt generato dovrebbe rispondere. Le sezioni selezionate saranno utilizzate per personalizzare il prompt.")

            if selected_sections:
                st.write(f"Hai selezionato le sezioni: {', '.join(selected_sections)}")
                st.write("Nota: Queste sono le sezioni a cui il prompt darà risposta.")

                # Instanzia la classe FrascatiPromptGenerator con il DataFrame e le colonne selezionate
                prompt_generator = FrascatiPromptGenerator(df, domain_col, text_col)

                # Input per i contesti positivi
                st.write("Inserisci i contesti positivi per ciascuna colonna selezionata:")
                positive_contexts = {}
                for col in positive_cols:
                    # Permette all'utente di inserire un contesto positivo per ciascuna colonna
                    context = st.text_area(f"Inserisci il contesto positivo per la colonna '{col}'", "")
                    st.info("Inserisci un contesto o una descrizione che rappresenta un esempio positivo per la colonna selezionata. Questo aiuta a migliorare la qualità dei prompt generati.")
                    if context:
                        positive_contexts[col] = context

                # Input per il contesto della risposta
                st.write("Inserisci il contesto che dovrebbe essere usato nella risposta:")
                response_context = st.text_area("Inserisci il contesto per la risposta", "")
                st.info("Inserisci un contesto generale che dovrebbe essere utilizzato per guidare la generazione della risposta. Questo contesto è utilizzato per migliorare la rilevanza del prompt.")

                if st.button("Genera i prompt"):
                    try:
                        # Genera un prompt per ciascuna sezione selezionata
                        for section in selected_sections:
                            prompt = prompt_generator.generate_prompt(
                                section=section,
                                positive_columns=positive_cols,
                                positive_context=[positive_contexts[col] for col in positive_cols],
                                context=response_context
                            )

                            # Mostra il prompt generato per la sezione corrente
                            st.write(f"**Prompt per la sezione '{section}':**")
                            st.code(prompt, language='text')

                            # JavaScript per copiare il testo del prompt negli appunti
                            st.markdown("""
                            <script>
                            function copyToClipboard() {
                                const promptText = document.getElementById('prompt-text').innerText;
                                navigator.clipboard.writeText(promptText).then(() => {
                                    alert('Prompt copiato negli appunti!');
                                }, (err) => {
                                    alert('Errore nella copia: ' + err);
                                });
                            }
                            </script>
                            """, unsafe_allow_html=True)
                            #st.markdown(f"<pre id='prompt-text'>{prompt}</pre>", unsafe_allow_html=True)

                    except ValueError as e:
                        st.error(f"Errore: {e}")

if __name__ == "__main__":
    main()
