# Svelte library

Everything you need to build a Svelte library, powered by [`sv`](https://npmjs.com/package/sv).

Read more about creating a library [in the docs](https://svelte.dev/docs/kit/packaging).

## Creating a project

If you're seeing this, you've probably already done this step. Congrats!

```sh
# create a new project in the current directory
npx sv create

# create a new project in my-app
npx sv create my-app
```

To recreate this project with the same configuration:

```sh
# recreate this project
npx sv@0.14.0 create --template library --types ts --install npm frontend
```

## Developing

Once you've created a project and installed dependencies with `npm install` (or `pnpm install` or `yarn`), start a development server:

```sh
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

Everything inside `src/lib` is part of your library, everything inside `src/routes` can be used as a showcase or preview app.

## Building

To build your library:

```sh
npm pack
```

To create a production version of your showcase app:

```sh
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.

## Publishing

Go into the `package.json` and give your package the desired name through the `"name"` option. Also consider adding a `"license"` field and point it to a `LICENSE` file which you can create from a template (one popular option is the [MIT license](https://opensource.org/license/mit/)).

To publish your library to [npm](https://www.npmjs.com):

```sh
npm publish
```

## Running Without Docker (For Local Model Testing)

The local fine-tuned model (TinyLlama + LoRA) requires significant CPU resources and may timeout in Docker. To test the local model, run the application directly:

### Prerequisites

- Python 3.10+
- Node.js 18+
- 8GB RAM minimum

### Step 1: Update .env for Local Running
```bash
# Change LORA_ADAPTER_PATH to local path (not Docker path)
LORA_ADAPTER_PATH=C:/Users/Dell/Downloads/Op-ai/nordic-bank-model
```

### Step 2: Start Backend
```bash
cd C:\Users\Dell\Downloads\Op-ai

# Create virtual environment (first time only)
python -m venv venv
venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start backend
python -m uvicorn app.main:app --reload
```

### Step 3: Start Frontend

Open a new terminal:
```bash
cd C:\Users\Dell\Downloads\Op-ai\frontend
npm install
npm run dev
```

### Step 4: Access Application

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

### Model Selection Guide

| Model | Speed | Best For |
|-------|-------|----------|
| Groq | 2-5 seconds | Demo, daily use |
| Local LoRA | 1-10 minutes (CPU) | Privacy, offline use |
| OpenAI | 2-5 seconds | High quality (paid) |

**Note:** First request to local model takes longer as it loads the model into memory. Subsequent requests use cached model.