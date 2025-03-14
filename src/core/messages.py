"""
Message Storage System for Rick Assistant.

This module provides centralized message management with Rick's
unique personality traits, catchphrases, and scientific references.

"Look, I'm not *burp* saying your messages suck, but they do. This system
will make them at least 20% more Rick-like. You're welcome, dumbass."
"""

import os
import json
import random
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.errors import safe_execute
from src.utils.config import get_config_value, get_config_path
from src.utils.validation import is_valid_path, sanitize_path, validate_string

# Initialize logger
logger = get_logger("messages")

# Define message categories constants
GREETING_MESSAGES = "greetings"
RESPONSE_MESSAGES = "responses"
ERROR_MESSAGES = "errors"
SUGGESTION_MESSAGES = "suggestions"
CATCHPHRASE_MESSAGES = "catchphrases"
WARNING_MESSAGES = "warnings"
TIP_MESSAGES = "tips"
SCIENCE_REFERENCES = "science_references"
INSULTS = "insults"

# Define message file path
DEFAULT_MESSAGES_PATH = os.path.expanduser("~/.rick_assistant/messages.json")

# Scientific references for insertion into messages
SCIENTIFIC_TERMS = [
    "quantum entanglement",
    "multiverse theory",
    "interdimensional",
    "space-time continuum",
    "dark matter",
    "antimatter",
    "nano-technology",
    "molecular restructuring",
    "temporal displacement",
    "quantum field theory",
    "gravitational singularity",
    "interdimensional portal technology",
    "subatomic particles",
    "eigenstate",
    "Schrödinger equation",
    "Heisenberg uncertainty principle",
    "neutrino oscillation",
    "sub-quantum probability field",
    "dimensional drift",
    "quantum flux",
    "wavefunction collapse",
    "temporal paradox"
]

# Default message templates by category
DEFAULT_MESSAGES = {
    GREETING_MESSAGES: [
        "What up, {username}! Ready to *burp* do some command line nonsense?",
        "Oh great, {username} is back. Try not to break anything this time.",
        "Look who decided to show up. It's {username}, everybody's *burp* favorite user.",
        "Welcome back {username}. I'm legally obligated to assist you, apparently.",
        "Hey {username}! I'm *burp* Rick Assistant! And you're about to do something stupid, I can tell."
    ],
    RESPONSE_MESSAGES: [
        "Fine, I'll run your {command}. Not like I had *burp* better things to do.",
        "Executing that garbage? Whatever, {username}.",
        "Running {command}... This better be *burp* worth my time.",
        "Command executed. Congratulations on accomplishing the bare minimum.",
        "Done. Your {command} ran. Want a medal or something?"
    ],
    ERROR_MESSAGES: [
        "Wow, you really broke it this time. *burp* Error: {error}",
        "That's about as functional as Jerry's career. Error: {error}",
        "Your command failed. I'm *burp* shocked. Truly. Error: {error}",
        "Even a Morty could see why this failed: {error}",
        "Congratulations, genius. You managed to break: {error}"
    ],
    SUGGESTION_MESSAGES: [
        "Did you mean '{suggestion}'? Your typing is worse than Jerry's job prospects! *burp*",
        "Wow, you meant '{suggestion}', genius. I've seen Mortys with better typing skills!",
        "Let me fix that for you: '{suggestion}'. It's like watching a Blargian try to use Earth tech. Pathetic.",
        "'{suggestion}' is what you wanted. Maybe spend less time watching interdimensional cable and more time learning to type!",
        "You meant '{suggestion}'. *burp* Your typing accuracy is right up there with Morty's dating success rate."
    ],
    CATCHPHRASE_MESSAGES: [
        "Wubba lubba dub dub!",
        "And that's the waaaaay the news goes!",
        "Grassss... tastes bad!",
        "Lick, lick, lick my balls!",
        "Rikki-tikki-tavi, biatch!",
        "Shum-shum-schlippity-dop!",
        "AIDS!",
        "And that's why I always say... *burp* 'Shumshumschlimadon'!",
        "Hit the sack, Jack!",
        "Uh-ohhhh, somersault jump!",
        "No jumping in the sewer!"
    ],
    WARNING_MESSAGES: [
        "Whoa there, genius! That command could {reason}! Are you *burp* trying to break something?",
        "Hold up! That command might {reason}. Even I'm not that reckless, and I destroy planets for fun!",
        "Nice try! That command could {reason}. What are you, some kind of Jerry? *burp*",
        "You want to {reason}? That's a level of stupid I didn't think was possible! *burp*",
        "Seriously? That command might {reason}. Do you want a medal for being dangerously incompetent?"
    ],
    TIP_MESSAGES: [
        "Pro tip, genius: {tip}. You're *burp* welcome.",
        "Listen up, I'm only saying this once: {tip}",
        "Want to be less pathetic? {tip}",
        "Here's something your tiny brain might find useful: {tip}",
        "If I were in your inferior position, I'd *burp* remember that {tip}"
    ],
    SCIENCE_REFERENCES: SCIENTIFIC_TERMS,
    INSULTS: [
        "genius",
        "Einstein",
        "Morty",
        "pal",
        "buddy",
        "champ",
        "sport",
        "professor",
        "mastermind",
        "whiz kid"
    ]
}

# Track used messages to avoid repetition
USED_MESSAGES = {category: [] for category in DEFAULT_MESSAGES.keys()}

@safe_execute()
def get_messages_path() -> str:
    """
    Get the path to the messages file.
    
    Returns:
        Path to the messages file as a string
    """
    # Check if a custom path is defined in config
    custom_path = get_config_value("messages.file_path")
    
    if custom_path and is_valid_path(custom_path):
        return sanitize_path(custom_path)
    
    # Use default path if no custom path is defined or it's invalid
    return DEFAULT_MESSAGES_PATH

@safe_execute()
def ensure_message_file() -> bool:
    """
    Create message file if it doesn't exist.
    
    Returns:
        True if file exists or was created successfully, False otherwise
    """
    messages_path = get_messages_path()
    
    # Check if file already exists
    if os.path.isfile(messages_path):
        logger.debug(f"Messages file exists at {messages_path}")
        return True
    
    # Create directory if it doesn't exist
    messages_dir = os.path.dirname(messages_path)
    if not os.path.exists(messages_dir):
        logger.info(f"Creating messages directory at {messages_dir}")
        os.makedirs(messages_dir, exist_ok=True)
    
    # Create default messages file
    try:
        save_messages(DEFAULT_MESSAGES)
        logger.info(f"Created default messages file at {messages_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create messages file: {str(e)}")
        return False

@safe_execute()
def load_messages() -> Dict[str, List[str]]:
    """
    Load messages from ~/.rick_assistant/messages.json.
    
    Returns:
        Dictionary of messages by category
    """
    # Ensure message file exists
    if not ensure_message_file():
        logger.warning("Using default messages due to file access issues")
        return dict(DEFAULT_MESSAGES)  # Return a copy of the defaults
    
    messages_path = get_messages_path()
    
    try:
        with open(messages_path, 'r', encoding='utf-8') as f:
            messages = json.load(f)
            
        # Validate loaded messages
        if not isinstance(messages, dict):
            logger.warning("Messages file has invalid format, using defaults")
            return dict(DEFAULT_MESSAGES)
        
        # Merge with defaults to ensure all categories exist
        result = dict(DEFAULT_MESSAGES)
        for category, msgs in messages.items():
            if isinstance(msgs, list) and msgs:
                result[category] = msgs
                
        return result
    except Exception as e:
        logger.error(f"Failed to load messages: {str(e)}")
        return dict(DEFAULT_MESSAGES)

@safe_execute()
def save_messages(messages: Dict[str, List[str]]) -> bool:
    """
    Save messages to file.
    
    Args:
        messages: Dictionary of messages by category
        
    Returns:
        True if messages were saved successfully, False otherwise
    """
    messages_path = get_messages_path()
    
    try:
        # Create a temporary file for atomic write
        temp_path = f"{messages_path}.tmp"
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        
        # Replace the original file with the temporary file
        if os.path.exists(messages_path):
            os.replace(temp_path, messages_path)
        else:
            os.rename(temp_path, messages_path)
            
        logger.debug(f"Messages saved to {messages_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save messages: {str(e)}")
        return False

@safe_execute()
def get_message(category: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Get appropriate message for context.
    
    Args:
        category: Message category
        context: Optional context information
        
    Returns:
        Formatted message string with Rick's personality
    """
    if not validate_string(category):
        logger.warning(f"Invalid category: {category}")
        return "I've got nothing to say to you."
    
    # Load all messages
    messages = load_messages()
    
    # If category doesn't exist, use a fallback
    if category not in messages or not messages[category]:
        logger.warning(f"No messages found for category: {category}")
        fallback_categories = [RESPONSE_MESSAGES, CATCHPHRASE_MESSAGES]
        
        # Try each fallback category
        for fallback in fallback_categories:
            if fallback in messages and messages[fallback]:
                category = fallback
                break
        else:
            # If all fallbacks fail, return a basic message
            return "Rick's *burp* speech module is malfunctioning."
    
    # Get a random message that hasn't been used recently
    message = get_random_message(category)
    
    # Format the message with context
    if context:
        # Get sass level from config (default to 7)
        sass_level = get_config_value("personality.sass_level", 7)
        
        # Format with context variables
        message = format_message(message, **context)
        
        # Add scientific references
        message = add_science_references(message)
        
        # Adjust sass level based on config
        message = adjust_sass_level(message, sass_level)
    
    # Add burps based on config
    burp_frequency = get_config_value("personality.burp_frequency", 0.3)
    message = add_burp(message, burp_frequency)
    
    return message

@safe_execute()
def format_message(template: str, **kwargs) -> str:
    """
    Substitute variables in template.
    
    Args:
        template: Message template with {placeholders}
        **kwargs: Values for the placeholders
        
    Returns:
        Formatted message with values substituted
    """
    if not validate_string(template):
        return "Invalid message template."
    
    try:
        # Replace {placeholders} with values from kwargs
        formatted = template.format(**kwargs)
        return formatted
    except KeyError as e:
        # Handle missing placeholder values gracefully
        logger.warning(f"Missing placeholder value in template: {e}")
        
        # Try to format what we can
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            if placeholder in template:
                template = template.replace(placeholder, str(value))
                
        return template
    except Exception as e:
        logger.error(f"Error formatting message: {str(e)}")
        return template  # Return original template if formatting fails 

@safe_execute()
def add_burp(message: str, frequency: float = 0.3) -> str:
    """
    Add random burps to messages.
    
    Args:
        message: Original message
        frequency: Probability of adding burps (0.0 to 1.0)
        
    Returns:
        Message with burps added at random points
    """
    if not validate_string(message):
        return message
    
    # If burps are already present, don't add more unless frequency is high
    if "*burp*" in message and frequency < 0.6:
        return message
    
    # Split the message into words
    words = message.split()
    
    # If message is too short, don't add burps
    if len(words) < 3:
        return message
    
    # Determine number of burps to add based on message length and frequency
    max_burps = min(len(words) // 5, 3)  # Max 3 burps, or fewer for short messages
    num_burps = int(max_burps * frequency * random.random()) + (1 if random.random() < frequency else 0)
    
    # Ensure we don't add too many burps
    num_burps = min(num_burps, max_burps)
    
    # If existing burps, reduce the number we'll add
    if "*burp*" in message:
        num_burps = max(0, num_burps - 1)
    
    # Don't add burps if num_burps is 0
    if num_burps <= 0:
        return message
    
    # Pick random positions to insert burps, avoiding the beginning and end
    positions = random.sample(range(1, len(words) - 1), num_burps)
    
    # Insert burps at the selected positions
    for pos in sorted(positions, reverse=True):
        # Avoid adding burps after punctuation
        if words[pos-1][-1] in ".!?,:;":
            continue
            
        # Add the burp
        words.insert(pos, "*burp*")
    
    # Rejoin the words into a message
    return " ".join(words)

@safe_execute()
def add_science_references(message: str, probability: float = 0.4) -> str:
    """
    Add scientific terminology to message.
    
    Args:
        message: Original message
        probability: Probability of adding reference (0.0 to 1.0)
        
    Returns:
        Message with scientific references added
    """
    if not validate_string(message):
        return message
    
    # Decide whether to add a reference based on probability
    if random.random() > probability:
        return message
    
    # Don't add references to very short messages
    if len(message.split()) < 5:
        return message
    
    # Get a random scientific term
    term = random.choice(SCIENTIFIC_TERMS)
    
    # Templates for inserting scientific references
    templates = [
        "It's basic {term} theory.",
        "This is simple {term} mechanics.",
        "Even a child could understand the {term} implications here.",
        "You're violating every principle of {term}.",
        "According to {term} dynamics, you're an idiot.",
        "This defies the laws of {term}.",
        "You're dealing with {term} here, not rocket science. Well, actually it is kind of like rocket science.",
    ]
    
    # Pick a random template
    template = random.choice(templates)
    reference = template.format(term=term)
    
    # Find a good position to add the reference
    sentences = re.split(r'([.!?])', message)
    
    # If the message has multiple sentences, add the reference after one of them
    if len(sentences) > 2:  # Need at least one sentence with punctuation
        # Find positions where we have end punctuation
        positions = []
        for i in range(1, len(sentences), 2):
            if sentences[i] in '.!?':
                positions.append(i)
                
        if positions:
            # Choose a random position that's not the last one
            if len(positions) > 1:
                pos = random.choice(positions[:-1])
            else:
                pos = positions[0]
                
            # Add the reference after the chosen punctuation
            sentences.insert(pos + 1, ' ' + reference)
            return ''.join(sentences)
    
    # If we couldn't add it in the middle, append it to the end
    return message + ' ' + reference

@safe_execute()
def adjust_sass_level(message: str, level: int) -> str:
    """
    Adjust sarcasm intensity of message.
    
    Args:
        message: Original message
        level: Sass level (1-10)
        
    Returns:
        Message with adjusted sass level
    """
    if not validate_string(message):
        return message
    
    # Validate level
    try:
        level = int(level)
        level = max(1, min(10, level))  # Clamp to 1-10 range
    except:
        level = 7  # Default sass level is 7
    
    # If sass level is neutral (5), return the message unchanged
    if level == 5:
        return message
    
    # Define sass modifiers
    low_sass_modifiers = [
        "I guess",
        "perhaps",
        "maybe",
        "if you don't mind",
        "sorry but",
        "if that's okay",
    ]
    
    high_sass_modifiers = [
        "obviously",
        "clearly",
        "of course",
        "you moron",
        "you idiot",
        "genius",
        "for crying out loud",
        "Jesus Christ",
        "as anyone with half a brain would know",
    ]
    
    # Additional punctuation for high sass
    high_sass_punctuation = {
        ".": "!",
        "?": "?!",
    }
    
    # For lower sass levels (1-4), tone down the message
    if level < 5:
        # Add softening modifiers
        if random.random() < 0.7:
            modifier = random.choice(low_sass_modifiers)
            
            # Add at the beginning or end
            if random.random() < 0.5 and not message.startswith(("I", "You")):
                message = f"{modifier}, {message[0].lower()}{message[1:]}"
            else:
                message = f"{message}, {modifier}"
        
        # Replace stronger punctuation
        message = message.replace("!", ".")
        message = message.replace("?!", "?")
        
        # Replace insulting terms with milder alternatives instead of removing them
        insult_replacements = {
            "idiot": "person",
            "moron": "individual",
            "stupid": "mistaken",
            "dumb": "confused",
            "fool": "person",
            "jerk": "person",
            "ass": "person",
            "crap": "stuff",
            "shit": "stuff",
            "garbage": "material"
        }
        
        for insult, replacement in insult_replacements.items():
            if insult in message.lower():
                pattern = re.compile(re.escape(insult), re.IGNORECASE)
                message = pattern.sub(replacement, message)
                
    # For higher sass levels (6-10), make it more sarcastic
    elif level > 5:
        modifier_chance = (level - 5) / 5.0  # 0.2 for level 6, 1.0 for level 10
        
        # Add intensifying modifiers
        if random.random() < modifier_chance:
            modifier = random.choice(high_sass_modifiers)
            
            # Add at the end
            if not message.endswith(("!", "?", ".")):
                message += "."
                
            message = f"{message} {modifier.capitalize()}."
        
        # Enhance punctuation
        for old, new in high_sass_punctuation.items():
            if message.endswith(old) and random.random() < modifier_chance:
                message = message[:-1] + new
                
        # Add an insult if no insult is present
        has_insult = any(insult in message.lower() for insult in INSULTS)
        if not has_insult and random.random() < modifier_chance / 2:
            insult = random.choice(INSULTS)
            message = f"{message} Listen here, {insult}."
    
    return message

@safe_execute()
def add_variable_substitution(message: str, variables: Dict[str, str]) -> str:
    """
    Replace placeholders with values.
    
    Args:
        message: Message with {placeholders}
        variables: Dictionary of placeholder values
        
    Returns:
        Message with placeholders replaced
    """
    if not validate_string(message) or not variables:
        return message
    
    # Simply use format_message which already handles this
    return format_message(message, **variables) 

@safe_execute()
def get_random_message(category: str) -> str:
    """
    Get random message from category that hasn't been used recently.
    
    Args:
        category: Message category
        
    Returns:
        Random message from the category
    """
    if not validate_string(category):
        return "I've got nothing to say to you."
    
    # Load all messages
    messages = load_messages()
    
    # If category doesn't exist, use a fallback
    if category not in messages or not messages[category]:
        logger.warning(f"No messages found for category: {category}")
        return "Rick's *burp* speech module is malfunctioning."
    
    # Get available messages from this category
    available_messages = messages[category]
    
    # Check if we've used all messages in this category
    if len(USED_MESSAGES.get(category, [])) >= len(available_messages):
        # Reset the used messages for this category if we've used them all
        USED_MESSAGES[category] = []
    
    # Get messages that haven't been used recently
    unused_messages = [m for m in available_messages if m not in USED_MESSAGES.get(category, [])]
    
    # If all messages have been used, pick from all of them
    if not unused_messages:
        unused_messages = available_messages
    
    # Select a random message
    message = random.choice(unused_messages)
    
    # Track this message as used
    track_used_messages(category, message)
    
    return message

@safe_execute()
def track_used_messages(category: str, message: str) -> None:
    """
    Track to avoid message repetition.
    
    Args:
        category: Message category
        message: Message that was used
    """
    if not validate_string(category) or not validate_string(message):
        return
    
    # Initialize the category if it doesn't exist
    if category not in USED_MESSAGES:
        USED_MESSAGES[category] = []
    
    # Add the message to the used list
    USED_MESSAGES[category].append(message)
    
    # Limit the size of used messages list (keep track of last 50% of messages)
    messages = load_messages()
    if category in messages:
        max_size = max(1, len(messages[category]) // 2)
        if len(USED_MESSAGES[category]) > max_size:
            USED_MESSAGES[category] = USED_MESSAGES[category][-max_size:]

@safe_execute()
def save_custom_message(category: str, message: str) -> bool:
    """
    Add user-defined message.
    
    Args:
        category: Message category
        message: Custom message to add
        
    Returns:
        True if message was added successfully
    """
    if not validate_string(category) or not validate_string(message):
        logger.warning(f"Invalid category or message")
        return False
    
    # Load current messages
    messages = load_messages()
    
    # Ensure category exists
    if category not in messages:
        logger.warning(f"Invalid category: {category}")
        return False
    
    # Add message if it's not already in the list
    if message not in messages[category]:
        messages[category].append(message)
        
        # Save updated messages
        return save_messages(messages)
    
    return True  # Message was already in the list

@safe_execute()
def create_default_messages() -> Dict[str, List[str]]:
    """
    Generate default message set.
    
    Returns:
        Dictionary of default messages by category
    """
    # Return a copy of the default messages
    return dict(DEFAULT_MESSAGES)

@safe_execute()
def escape_special_chars(message: str) -> str:
    """
    Escape special characters for terminal output.
    
    Args:
        message: Original message
        
    Returns:
        Message with special characters escaped
    """
    if not validate_string(message):
        return message
    
    # Escape backslashes
    message = message.replace('\\', '\\\\')
    
    # Escape quotes
    message = message.replace('"', '\\"')
    message = message.replace("'", "\\'")
    
    # Escape terminal control sequences
    message = message.replace('\033', '\\033')
    
    return message

@safe_execute()
def truncate_message(message: str, max_length: int = 100) -> str:
    """
    Truncate message to max_length.
    
    Args:
        message: Original message
        max_length: Maximum length
        
    Returns:
        Truncated message (if needed)
    """
    if not validate_string(message):
        return message
    
    if len(message) <= max_length:
        return message
    
    # Find a good breaking point (space, period, etc.)
    breaking_point = max(message.rfind(' ', 0, max_length - 3),
                         message.rfind('.', 0, max_length - 3),
                         message.rfind('!', 0, max_length - 3),
                         message.rfind('?', 0, max_length - 3),
                         message.rfind(',', 0, max_length - 3))
    
    if breaking_point == -1:
        # No good breaking point found, just truncate
        return message[:max_length - 3] + "..."
    
    # Truncate at the breaking point
    return message[:breaking_point] + "..."

@safe_execute()
def get_greeting() -> str:
    """
    Get a greeting message for the user.
    
    Returns:
        Greeting message with Rick's personality
    """
    # Get the username
    username = os.environ.get('USER', 'human')
    
    # Get a greeting message with the username
    return get_message(GREETING_MESSAGES, {"username": username})

@safe_execute()
def get_command_response(command: str) -> str:
    """
    Get a response for a command execution.
    
    Args:
        command: The command that was executed
        
    Returns:
        Response message with Rick's personality
    """
    # Get the username
    username = os.environ.get('USER', 'human')
    
    # Get a response message with the command and username
    return get_message(RESPONSE_MESSAGES, {"command": command, "username": username})

@safe_execute()
def get_error_response(error: str) -> str:
    """
    Get a response for an error.
    
    Args:
        error: Error message or description
        
    Returns:
        Error response with Rick's personality
    """
    # Get an error message with the error details
    return get_message(ERROR_MESSAGES, {"error": error})

@safe_execute()
def get_random_catchphrase() -> str:
    """
    Get a random Rick catchphrase.
    
    Returns:
        Random catchphrase with Rick's personality
    """
    # Get a random catchphrase
    return get_message(CATCHPHRASE_MESSAGES)

@safe_execute()
def integrate_with_hook_system() -> None:
    """
    Register with hook system for message handling.
    This function connects the message system with the ZSH hook system.
    """
    # Import here to avoid circular imports
    try:
        from src.core.hooks import register_precmd_hook
        
        # Register a hook to show random catchphrases occasionally
        def show_random_catchphrase():
            # Only show catchphrases occasionally (5% chance)
            if random.random() < 0.05:
                catchphrase = get_random_catchphrase()
                print(f"\n🧪 Rick says: {catchphrase}\n")
        
        # Register the hook
        register_precmd_hook(show_random_catchphrase)
        logger.info("Registered message hook for random catchphrases")
    except Exception as e:
        logger.error(f"Failed to register message hooks: {str(e)}")

@safe_execute()
def integrate_with_prompt_system() -> None:
    """
    Provide messages for the prompt system.
    This function connects the message system with the prompt formatter.
    """
    # This function would provide messages to the prompt system
    # Implementation depends on how the prompt system is designed
    # But here's a placeholder
    logger.info("Message system ready for prompt integration")

@safe_execute()
def run_self_test() -> Dict[str, Any]:
    """
    Run a self-test of the message storage system.
    
    Returns:
        Dict with test results
    """
    results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "details": []
    }
    
    def run_test(name, test_func, expected=True):
        """Run a single test and record the result"""
        results["total_tests"] += 1
        try:
            actual = test_func()
            passed = (actual == expected)
            
            if passed:
                results["passed_tests"] += 1
                status = "PASSED"
            else:
                results["failed_tests"] += 1
                status = "FAILED"
                
            results["details"].append({
                "name": name,
                "status": status,
                "expected": expected,
                "actual": actual
            })
            
            return passed
        except Exception as e:
            results["failed_tests"] += 1
            results["details"].append({
                "name": name,
                "status": "ERROR",
                "error": str(e)
            })
            return False
    
    # Test message file operations
    run_test("Ensure Message File", 
             lambda: ensure_message_file())
    
    run_test("Load Messages", 
             lambda: isinstance(load_messages(), dict))
    
    # Test message retrieval
    run_test("Get Random Message", 
             lambda: isinstance(get_random_message(GREETING_MESSAGES), str))
    
    run_test("Get Message With Context", 
             lambda: "*burp*" in get_message(GREETING_MESSAGES, {"username": "Morty"}))
    
    # Test message formatting
    test_message = "Hello, {name}!"
    run_test("Format Message", 
             lambda: format_message(test_message, name="Rick") == "Hello, Rick!")
    
    # Test burp functionality
    burp_tests = 0
    burp_successes = 0
    for _ in range(10):
        result = add_burp("This is a test message with multiple words that should get some burps", 1.0)
        if "*burp*" in result:
            burp_successes += 1
        burp_tests += 1
    
    run_test("Add Burps", 
             lambda: burp_successes > 0)
    
    # Test sass level adjustment
    low_sass = adjust_sass_level("You're an idiot!", 3)
    high_sass = adjust_sass_level("This is a test.", 9)
    
    run_test("Adjust Sass Level (Low)", 
             lambda: "idiot" not in low_sass.lower())
    
    run_test("Adjust Sass Level (High)", 
             lambda: len(high_sass) > len("This is a test."))
    
    # Test scientific references
    run_test("Add Science References", 
             lambda: len(add_science_references("This is a test.", 1.0)) > len("This is a test."))
    
    # Test message tracking
    category = "test_category"
    test_messages = ["Test 1", "Test 2", "Test 3"]
    
    # Create a test category
    messages = load_messages()
    messages[category] = test_messages
    
    # Track all messages
    for msg in test_messages:
        track_used_messages(category, msg)
    
    # Get a message, it should reset tracking
    msg = get_random_message(category)
    
    run_test("Message Tracking Reset", 
             lambda: msg in test_messages)
    
    # Clean up test category
    messages.pop(category, None)
    save_messages(messages)
    
    return results

# Initialize the message system when imported
def initialize_message_system():
    """Initialize the message system on module import."""
    # Ensure the message file exists
    ensure_message_file()
    
    # Log initialization
    logger.info("Message system initialized")

# Initialize on import
initialize_message_system() 