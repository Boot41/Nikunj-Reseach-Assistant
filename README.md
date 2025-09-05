# Research-CLI

Research-CLI is a powerful set of researching tools designed to help researchers collect, summarize, and write research papers, articles, and much more. tag

#Video link 
https://www.loom.com/share/dcffe2f8d02c482093a27df0318a5057?sid=9691f8ce-c169-4da3-85f0-e36e2dfb8033
## User Stories

-   **Fetch Research Papers:** As a user, I want to fetch research papers directly from the CLI to avoid manual searching.
-   **Paper Breakdowns:** As a user, I want to get a thorough breakdown of research papers within the CLI to save time.
-   **Cross-Question Ideas:** As a user, I want to cross-question ideas to save time.
-   **Comprehensive Search:** As a user, whenever I search for new topics, I want to get papers that started the innovation, breakthrough papers with the most citations, and recent studies to understand the research topic thoroughly.
-   **Flexible Information Retrieval:** As a user, I want to have choices to ask for a summary, a review, or more details regarding the topic to understand it better.
-   **Persistent Chat History:** As a user, I want the application to remember my previous chats/prompts so I can continue my research even after closing it.
-   **Conversation Continuity:** As a user, I want the application to remember my previous chats/prompts and give me an option to continue that conversation.
-   **Paper Storage:** As a user, I want to store all the selected research papers for quick navigation and access.
-   **Combined Summaries:** As a user, I want the AI to summarize the papers and provide me with a combined summary to save time.
-   **Literature Review Generation:** As a user, I want the AI to write a detailed Literature review so I can understand the trends and shortcomings.
-   **Reputable Sources:** As a user, I want the AI to fetch papers from reputed journals (IEEE, SPRINGER, ELESVIER, etc.) and arXiv for proper search results.

## Tech Stack

-   **CLI Framework:** Typer (for commands), prompt_toolkit (for REPL), Rich (for output), InquirerPy (for quick selection menus).
-   **AI/LLM:** OpenAI SDK (or Anthropic, Gemini, etc.), LlamaIndex, LangChain, MCP, Memory Layer (Redis, SQLite, or LangChain Memory).
-   **Tools & Integrations:** Fetch from sources like IEEE, SPRINGER, ARXIV, and other important sites, write and save summaries to desktop, read from desktop.
-   **Memory:** LangChain Memory, Vector database.

## Nice to Have Features

-   Map `Ctrl+C` to cancel the current operation but not exit the app.
-   Offer `:quit` / `:help` meta-commands inside the REPL.
-   Map `Ctrl+C` to be pressed twice to exit the app.