# commands.py
from functions.os_ops import open_notepad, open_discord, open_cmd, open_camera, open_calculator

def handle_command(query):
    if 'open notepad' in query:
        open_notepad()
        return "Opening Notepad..."
    elif 'open discord' in query:
        open_discord()
        return "Opening Discord..."
    elif 'open command prompt' in query or 'open cmd' in query:
        open_cmd()
        return "Opening Command Prompt..."
    elif 'open camera' in query:
        open_camera()
        return "Opening Camera..."
    elif 'open calculator' in query:
        open_calculator()
        return "Opening Calculator..."
    else:
        # Handle other commands or generate a default response
        return "Sorry, I don't understand that command."
