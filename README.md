# AI-Powered-Avatar
AI-Power Avatar pratical workshop for the BTU AI Camp on XR and Emerging Technologies

Project architecture :
  - index.html => Client side (3D Avatar, Text input prompt...)
  - ai_assistant.py => Server Side (OpenAI API, process text & audio...)

/!\ REQUIREMENTS /!\
- You are required to get an OPEN AI API KEY which is a PAID METHOD. Can't use model in a free way... :(
  - Go to the openai api website
  - Login
  - Add a minimum credit
     
- Code IDE like Visual Studio Code...
- an .env file to store your OpenAI api key
    - Create en ".env" file.
    - Add the variable OPENAI_API_KEY=COPY-YOUR-KEY
- Python
- Pip
- Packages :Install via pip or conda the following packages names
    - openai
    - flask
    - flask_cors
    - flask_socketio
    - asyncio
    - httpx
    - json
    - base64
    - os
    - dotenv
    - pathlib
      
How to start the demo ?

Open a terminal located in the root of the repository

Client : 
> python -m http.server
Started on http://localhost:8000
Server :
> python ai_assistant.py
Started on http://localhost:5000
