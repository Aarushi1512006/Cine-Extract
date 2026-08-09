# cine-extract

AI-powered movie info extractor — paste a paragraph, get structured movie data (cast, director, genre, rating) via LangChain + Mistral AI, rendered in a sleek Streamlit UI.

## Features

- **Structured extraction** — Pulls title, release year, genre(s), director, cast, rating, and summary from any free-text movie description using a Pydantic schema and `PydanticOutputParser`.
- **Themed UI** — Dark, Netflix-inspired interface (deep charcoal background, slate surfaces, popcorn-red accents).
- **Hero header** — Large title, release year, and color-coded genre pills.
- **Synopsis panel** — Clean readable summary with auto-generated theme tags (e.g. Ambition, Friendship, Betrayal).
- **Director banner** and **cast grid** with initials-based avatars.
- **Ratings** — Displays the extracted rating, or lets users be "the first to rate" if none was found.
- **Review box** — Lightweight, in-session review submission.

## Tech stack

- [Streamlit](https://streamlit.io/) — UI
- [LangChain](https://python.langchain.com/) — prompt orchestration
- [langchain-mistralai](https://pypi.org/project/langchain-mistralai/) — Mistral AI integration (`mistral-small-2506`)
- [Pydantic](https://docs.pydantic.dev/) — schema validation and structured output parsing

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/<your-username>/cine-extract.git
   cd cine-extract
   ```

2. Install dependencies:
   ```bash
   pip install streamlit langchain langchain-mistralai pydantic python-dotenv
   ```

3. Add your Mistral API key to a `.env` file in the project root:
   ```
   MISTRAL_API_KEY=your_api_key_here
   ```

4. Run the app:
   ```bash
   streamlit run UIStructureOp.py
   ```

## Usage

Paste a paragraph describing a movie (cast, director, plot, genre, etc.) into the text box and click **Extract**. The app calls Mistral AI to parse the text into structured fields and renders a full movie profile page.

## License

MIT
