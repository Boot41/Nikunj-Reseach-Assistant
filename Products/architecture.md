# Research-CLI Architecture

This document outlines the architecture of the Research-CLI tool, detailing its components and the flow of data between them.

## 1. High-Level Architecture

The Research-CLI tool is designed with a layered architecture to ensure a clear separation of concerns, making it easier to maintain and extend. The architecture consists of three main layers:

*   **Presentation Layer (CLI):** This is the user-facing layer, responsible for handling user input and displaying output. It is built using Typer, prompt_toolkit, Rich, and InquirerPy.
*   **Application Layer (Core Logic):** This layer contains the core business logic of the application. It orchestrates the various tasks, such as fetching data, processing it with the LLM, and managing user sessions. It is built using LangChain and custom Python modules.
*   **Data Access Layer:** This layer is responsible for all interactions with external data sources. This includes fetching data from academic APIs (IEEE, arXiv, etc.), querying the vector database, and managing the local cache and conversation history.

**Diagram Description:**

The diagram shows the three layers, with the Presentation Layer at the top, the Application Layer in the middle, and the Data Access Layer at the bottom. Arrows indicate the flow of control and data between the layers. The user interacts with the Presentation Layer, which sends commands to the Application Layer. The Application Layer then uses the Data Access Layer to retrieve or store data, and processes the data using the LLM. The results are then passed back up to the Presentation Layer to be displayed to the user.

## 2. Component Breakdown

### 2.1. Presentation Layer (CLI)

*   **`main.py`:** The entry point of the application. It will use Typer to define the CLI commands and subcommands.
*   **`repl.py`:** This module will implement the interactive REPL using `prompt_toolkit`. It will handle user input, command history, and auto-completion.
*   **`ui.py`:** This module will contain functions for displaying formatted output to the user, using the Rich library. It will also handle interactive prompts using `InquirerPy`.

### 2.2. Application Layer (Core Logic)

*   **`app.py`:** This module will contain the core application logic. It will be responsible for initializing the application, managing the main loop of the REPL, and coordinating the other components.
*   **`chains.py`:** This module will define the LangChain chains used for processing data. This will include chains for summarization, question-answering, and literature review generation.
*   **`memory.py`:** This module will manage the conversation history. It will use a LangChain memory backend, such as Redis or SQLite, to store and retrieve conversation data.

### 2.3. Data Access Layer

*   **`retrievers.py`:** This module will contain the logic for fetching data from external sources. It will include functions for interacting with the APIs of academic databases like IEEE and arXiv.
*   **`vector_store.py`:** This module will manage the vector database. It will be responsible for creating, updating, and querying the vector index.
*   **`file_manager.py`:** This module will handle all interactions with the local file system, such as reading and writing saved papers and summaries.

## 3. Data Flow Example: Fetching and Summarizing a Paper

To illustrate how the components work together, here is a step-by-step data flow for a typical use case: fetching and summarizing a research paper.

1.  **User Input:** The user enters a command in the REPL to search for a paper, for example: `search "The impact of AI on software development" --source arXiv`.
2.  **Presentation Layer:** The `repl.py` module captures the input and passes it to the `main.py` module. Typer parses the command and its arguments.
3.  **Application Layer:** The `app.py` module receives the parsed command. It calls the appropriate function in the `chains.py` module, in this case, the "search and summarize" chain.
4.  **Data Access Layer:** The chain in `chains.py` first interacts with the `retrievers.py` module. The `retrievers.py` module makes a call to the arXiv API to fetch the paper.
5.  **LLM Interaction:** The retrieved paper is then passed back to the `chains.py` module. The chain sends the paper's content to the LLM for summarization.
6.  **Vector Store:** The summarized paper, along with its metadata, is then sent to the `vector_store.py` module to be indexed in the vector database for future reference.
7.  **Presentation Layer:** The summary is passed back up to the `app.py` module, which then uses the `ui.py` module to display the formatted summary to the user in the CLI.
8.  **Memory:** The conversation, including the user's query and the generated summary, is saved to the conversation history via the `memory.py` module.