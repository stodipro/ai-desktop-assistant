import pyautogui
import cv2
import numpy as np
from transformers import pipeline
import screeninfo
import time
import logging
from typing import Tuple, Dict

class DesktopAssistant:
    def __init__(self):
        # Safety controls
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.5      # Delay between actions
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize screen
        self.screen = screeninfo.get_monitors()[0]
        
        # Initialize NLP
        try:
            self.nlp = pipeline("text-classification", model="bert-base-uncased")
            self.logger.info("NLP model initialized successfully")
        except Exception as e:
            self.logger.warning(f"Could not initialize NLP model: {e}")
            self.nlp = None

    def parse_command(self, command: str) -> Dict:
        """Parse natural language command into actionable steps"""
        command = command.lower()
        actions = {
            'action': None,
            'params': {},
            'target': None
        }
        
        # Basic command parsing
        if 'click' in command:
            actions['action'] = 'click'
            # Extract target (e.g., "click on Chrome")
            words = command.split()
            if 'on' in words:
                target_idx = words.index('on') + 1
                if target_idx < len(words):
                    actions['target'] = words[target_idx]
        
        elif 'type' in command:
            actions['action'] = 'type'
            # Extract text between quotes
            if '"' in command:
                start = command.find('"') + 1
                end = command.rfind('"')
                if start > 0 and end > start:
                    actions['params']['text'] = command[start:end]
        
        elif 'move' in command:
            actions['action'] = 'move'
            # Extract coordinates if present
            words = command.split()
            try:
                x_idx = words.index('x') + 1
                y_idx = words.index('y') + 1
                actions['params']['x'] = int(words[x_idx])
                actions['params']['y'] = int(words[y_idx])
            except (ValueError, IndexError):
                pass
        
        return actions

    def find_on_screen(self, target: str) -> Tuple[int, int]:
        """Find target element on screen using computer vision"""
        try:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # For now, use basic image matching
            # TODO: Implement more sophisticated detection methods
            location = pyautogui.locateOnScreen(f"targets/{target}.png")
            if location:
                return pyautogui.center(location)
            return None
        except Exception as e:
            self.logger.error(f"Error finding {target}: {e}")
            return None

    def execute_action(self, actions: Dict) -> bool:
        """Execute the parsed actions"""
        try:
            if actions['action'] == 'click':
                if actions['target']:
                    location = self.find_on_screen(actions['target'])
                    if location:
                        pyautogui.click(location)
                        return True
            
            elif actions['action'] == 'type':
                if 'text' in actions['params']:
                    pyautogui.write(actions['params']['text'])
                    return True
            
            elif actions['action'] == 'move':
                if 'x' in actions['params'] and 'y' in actions['params']:
                    pyautogui.moveTo(actions['params']['x'], actions['params']['y'])
                    return True
                    
            return False
        except Exception as e:
            self.logger.error(f"Error executing action: {e}")
            return False

    def process_command(self, command: str) -> bool:
        """Process and execute a natural language command"""
        self.logger.info(f"Processing command: {command}")
        
        # Parse command
        actions = self.parse_command(command)
        if not actions['action']:
            self.logger.warning("Could not parse command")
            return False
        
        # Execute actions
        return self.execute_action(actions)

def main():
    assistant = DesktopAssistant()
    print("AI Desktop Assistant initialized. Type 'quit' to exit.")
    print("\nExample commands:")
    print("- 'click on Chrome'")
    print("- 'type \"Hello World\"'")
    print("- 'move to x 100 y 200'")
    
    while True:
        try:
            command = input("\nEnter command: ").strip()
            
            if command.lower() == 'quit':
                print("Shutting down...")
                break
            
            if command:
                success = assistant.process_command(command)
                if success:
                    print("Command executed successfully")
                else:
                    print("Failed to execute command")
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()