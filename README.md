# Your Library, Your Impact: Dashboard and Insights Bot

This project is a data analytics dashboard and AI insights bot.

The project was designed and built for the Pacific Northwest University (PNWU) Health Sciences Library by E.R.A.I. Informatics as a University of Washington Master of Science in Information Management (MSIM) capstone project, 2025-2026. It was designed to be adapted by other PWNU departments or other small academic libraries. <!-- Read the [LICENSE.md](license.md) file for additional information on adapting this work. -->

## Background

The PNWU Health Sciences Library tracks activity and feedback, including from appointment logs, circulation reports, and patron surveys. However, most of the data lives in spreadsheets or PDFs that are difficult to access or analyze. This project brings the library's data together in one place so that library staff can review it, through a dashboard, and ask plain-English questions about it, through an AI insights bot.

## Dashboard

The dashboard includes visualizations on the library's service and collection activities, costs, and various survey results. Read the [Dashboard README](dashboard/README.md) for additional information.

## Insights Bot

*The insights bot is still under development.*

The insights bot lets users ask plain-English questions about the PNWU Health Sciences Library, including about questions about appointments, patron satisfaction, costs, and circulation.

The bot supports natural language interpretation of visualizations and quantitative trends. It has access to all the data shown in the dashboard, as well as additional data from the same underlying reports. For example, it has access to qualitative data from various surveys administered by the library, and to additional library cost breakdowns.

The bot uses a retrieval-augmented generation (RAG) -based large language model (LLM). This means the bot does not need to be retrained as new data is added, and can work well with specialized content. It is modeled after the [San Jose State University's KingbotGPT](https://github.com/sjsu-library/kingbotgpt) project.

## Prerequisites

* Python 3.10 or later (required for both dashboard and insights bot)
* [Ollama](https://ollama.com/download) (required for insights bot only)

## Installation

To install the **dashboard** locally:

1. Clone this repository.
2. Install the dependencies:

```
pip3 install -r dashboard/requirements.txt
```

To additionally install the **insights bot** locally, follow the steps above.

Then, use Ollama to install the Granite 4.1:3b model:

```
ollama pull granite4.1:3b
```

This model, made by IBM, is approximately 2GB.

## Local Deployment

To run the **dashboard** locally:

```
python3 -m streamlit run dashboard/app.py
```

The dashboard opens at `http://localhost:8501`.

## Team

E.R.A.I. Informatics
* Em Stelter
* Rose Brown
* A. Amrous
* Ivette Ivanov

PNWU Health Sciences Library
* Jan Kuebel-Hernandez, project sponsor, PWNU Health Sciences Library Director
* Maria So, PNWU intern
* Molly Jones, PNWU intern

## Acknowledgments

Bot architecture modeled after [SJSU Library KingbotGPT](https://github.com/sjsu-library/kingbotgpt). Dashboard structure inspired by IMT 561 lab scaffold by Dr. Shane McGarry at UW iSchool.
