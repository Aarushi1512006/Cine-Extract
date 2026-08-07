# MOOD.AI

An AI chatbot that switches personality — **Funny**, **Angry**, or **Sad** — with a fully themed UI that changes color, animation, and tone to match. Built with [LangChain](https://www.langchain.com/), [Mistral](https://mistral.ai/), and [Streamlit](https://streamlit.io/).

![MOOD.AI mode select screen](docs/screenshot-landing.png)
![MOOD.AI chat screen](docs/screenshot-chat.png)

## Features

- **Three personalities** — pick a mood before you start chatting, and the system prompt, color palette, and UI animation all shift to match:
  | Mode | Personality | Accent |
  |------|-------------|--------|
  | 🟡 Funny | Jokes, puns, humour | `#FFC145` |
  | 🔴 Angry | Aggressive, impatient | `#FF3B30` |
  | 🔵 Sad | Melancholy, wistful | `#6C8EFF` |
- **Living "mood orb"** — a small animated shape in the header that bounces, jitters, or droops depending on the active mode.
- **Themed chat bubbles** — assistant replies are styled per mode (color, glow, corner shape).
- **Conversation memory** — full chat history is sent back to the model on every turn, so it stays in character across the conversation.
- **Two versions included**:
  - `mood_ai_streamlit.py` — full themed web UI (recommended)
  - `mood_ai_cli.py` — original terminal-based version

## Tech stack

- **[Streamlit](https://streamlit.io/)** — UI framework
- **[LangChain](https://www.langchain.com/)** (`langchain-mistralai`, `langchain-core`) — model orchestration
- **[Mistral AI](https://mistral.ai/)** (`mistral-small-2506`) — language model
- **python-dotenv** — environment variable management

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/mood-ai.git
cd mood-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API key

Create a `.env` file in the project root:

```
MISTRAL_API_KEY=your_mistral_api_key_here
```

Get a key from [console.mistral.ai](https://console.mistral.ai/).

### 4. Run the app

```bash
streamlit run mood_ai_streamlit.py
```

The app will open at `http://localhost:8501`.

To run the original terminal version instead:

```bash
python mood_ai_cli.py
```

## Project structure

```
mood-ai/
├── mood_ai_streamlit.py   # Themed Streamlit web app
├── mood_ai_cli.py         # Original CLI chatbot
├── requirements.txt
├── .env                   # Not committed — holds your API key
└── README.md
```

## How it works

1. On launch, you're shown a mood-select screen with three cards (Funny, Angry, Sad).
2. Choosing a mode sets a `SystemMessage` that defines the AI's personality and injects a matching CSS theme (colors, fonts, orb animation) into the UI.
3. Each message you send is appended to the conversation history and sent to the Mistral model via LangChain, along with the system prompt, so replies stay consistent with the chosen personality.
4. You can switch moods at any time with the **change mood** button, which resets the conversation.

## Customization

- **Add a new mood**: add an entry to the `MODES` dictionary in `mood_ai_streamlit.py` with a `label`, `tag`, `system` prompt, and color values (`accent`, `accent2`, `bg_tint`, `bubble`).
- **Swap the model**: change the `model` argument in `get_model()` to any model supported by `langchain-mistralai`.
- **Change the animation**: mood orb keyframes live in the `inject_css()` function — each mode maps to an `orb-bounce` / `orb-shake` / `orb-droop` class.

## License

MIT — feel free to fork and adapt.
