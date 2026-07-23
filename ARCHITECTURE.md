## Insights Bot

The insights bot supports natural language interpretation of visualizations and quantitative trends. In other words, it lets users ask plain-English questions about the PNWU Health Sciences Library.

The bot uses a retrieval-augmented generation (RAG) -based large language model (LLM).

### Background

Generic "ask-your-documents" RAG chatbots are bad at counting. For example, they retrieve a few similar text snippets and let the model guess totals, which produces confident, but incorrect, answers. The YLYI bot avoids that:

```
  User question                                   ┌─────────────────────┐
       │                                          │   data/ *.xlsx,     │
       ▼                                          │   *.pdf (library    │
  ┌─────────────┐   "which tool + filters?"       │   appointment &     │
  │   Ollama    │ ───────────────────────────►    │   survey data)      │
  │ granite4.1  │   (routes the question)         └──────────┬──────────┘
  │   (local)   │                                            │ pandas
  └─────────────┘                                            ▼
       │ picks a tool                              ┌─────────────────────┐
       ▼                                           │  Structured tools   │
  count_appointments / breakdown_appointments ───► │  compute the EXACT  │
  satisfaction_summary / list_options              │  number from data   │
                                                   └──────────┬──────────┘
                                                              ▼
                                                       grounded answer
```

**The model only interprets the question and chooses a tool. Every number comes from pandas operations on the actual data.** These are the same dataframes the dashboard charts use, so the bot and the charts never disagree. Additionally, a "grounding guard" strips any filter the model adds that is not part of the user's question. For example, this means that "appointments each year" cannot accidentally become "appointments in one year."

If the bot is not available, a keyword fallback still answers common questions. For example, this may happen if you are running the YLYI project locally but Ollama is off.

### Architecture

As of July 2026, a crucial feature of the YLYI insights bot is that it runs entirely **locally**. It uses a free, open-source model: IBM Granite, through Ollama. **No API keys are required, and no data leaves the machine where YLYI is running.**

The following diagram shows the architecture of the YLYI bot:

```
   YOU (web browser)  ──  http://localhost:8501
        │
        ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │  Streamlit app   ( dashboard/app.py )                                   │
 │                                                                         │
 │   ┌──────────────────┐              ┌──────────────────────────────┐    │
 │   │  "Home" tab      │              │  "Insights Bot" tab          │    │
 │   │  charts + metrics│              │  chat box (st.chat_input)    │    │
 │   └────────┬─────────┘              └───────────────┬──────────────┘    │
 │            │ dataframes                             │ your question     │
 │            │                          ┌─────────────▼───────────────┐   │
 │            │                          │  src/bot.py : answer()      │   │
 │            │                          │                             │   │
 │            │            1. ROUTE      │  ┌──────────────────────┐   │   │
 │            │           the question   │  │  Ollama granite4.1   │   │   │
 │            │        ◄─────────────────┼─►│  :11434  (local)     │   │   │
 │            │       "which tool +      │  │  picks tool + args   │   │   │
 │            │        which filters?"   │  └──────────────────────┘   │   │
 │            │                          │             │ tool + args   │   │
 │            │                          │   2. GROUNDING GUARD        │   │
 │            │                          │      drops filters not in   │   │
 │            │                          │      the question text      │   │
 │            │                          │             │               │   │
 │            │                          │   3. COMPUTE (pandas)       │   │
 │            │                          │   ┌───────────────────────┐ │   │
 │            │                          │   │ count_appointments    │ │   │
 │            │                          │   │ breakdown_appointments│ │   │
 │            │                          │   │ satisfaction_summary  │ │   │
 │            │                          │   │ list_options          │ │   │
 │            │                          │   └──────────┬────────────┘ │   │
 │            │                          └──────────────┼──────────────┘   │
 │            │                                         │ EXACT numbers    │
 │            ▼                                         ▼                  │
 │   ┌─────────────────────────────────────────────────────────────────┐   │
 │   │  src/data.py   load_bookings() · load_satisfaction() · …        │   │
 │   │  (pandas reads the .xlsx / .pdf files, cached)                  │   │
 │   └───────────────────────────────┬─────────────────────────────────┘   │
 └───────────────────────────────────┼─────────────────────────────────────┘
                                     ▼
                            dashboard/data/   (xlsx + pdf)

  KEY IDEA:  The model only interprets the question and picks a tool.
             Every number is computed by pandas from the real data, that is,
             the same dataframes the dashboard uses. This way, the bot and the
             charts can never disagree, and counts cannot be hallucinated.
             If Ollama is off, a keyword fallback still answers common
             questions.
```
