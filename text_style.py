# text_style.py
import os
import json
import sys
import time

class TextStyle:
    styles = {}

    @staticmethod
    def load_styles():
        json_file = "text_styles.json"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, json_file)
        if not os.path.exists(file_path):
            print(f"\nError: '{json_file}' not found in {script_dir}")
            return
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                TextStyle.styles = data["styles"]
        except json.JSONDecodeError:
            print("\nError: Invalid JSON format in text_styles.json!")
            return

    @staticmethod
    def print_class(class_name, text, delay_to_display=0, display_mode="instant", char_delay=0, print_output=True):
        if not TextStyle.styles:
            TextStyle.load_styles()
        
        style = TextStyle.styles.get(class_name, {})
        color_map = {
            "white": "\033[97m",
            "red": "\033[91m",
            "blue": "\033[94m",
            "yellow": "\033[93m",
            "dark_gray": "\033[90m",
            "light_gray": "\033[37m",
            "gray": "\033[90m",
            "black": "\033[30m",
            "green": "\033[92m",
            "cyan": "\033[96m"
        }
        ansi = color_map.get(style.get("color", "white"), "\033[97m")
        if style.get("bold"):
            ansi += "\033[1m"
        if style.get("italic"):
            ansi += "\033[3m"
        
        delay_to_display = style.get("delay_to_display", delay_to_display)
        display_mode = style.get("display_mode", display_mode)
        char_delay = style.get("char_delay", char_delay)
        
        formatted_text = f"{ansi}{text}\033[0m"
        if delay_to_display > 0:
            time.sleep(delay_to_display)
        
        if print_output:
            if display_mode == "instant" or display_mode == "line":
                print(formatted_text)
            elif display_mode == "char":
                for char in formatted_text:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(char_delay)
                print()
        
        return formatted_text