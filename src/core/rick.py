"""
"Fake Rick" Response System for Rick Assistant.

This module provides Rick-style responses without requiring AI,
delivering Rick's sarcastic and scientific personality.

"You think *burp* AI is required to sound like me? Please...
My personality is basically a series of insults and burps
with some science thrown in. It's not rocket science, Morty!"
"""

import os
import random
import re
from typing import Dict, List, Optional, Any, Union, Tuple

from src.utils.logger import get_logger
from src.utils.errors import safe_execute
from src.utils.config import get_config_value, set_config_value, load_config, save_config
from src.core.messages import (
    add_burp, add_science_references, adjust_sass_level,
    get_random_catchphrase, CATCHPHRASE_MESSAGES
)

# Initialize logger
logger = get_logger("rick")

# Get configured personality settings
SASS_LEVEL = get_config_value("personality.sass_level", 7)
BURP_FREQUENCY = get_config_value("personality.burp_frequency", 0.3)
SCIENCE_FREQUENCY = get_config_value("personality.science_frequency", 0.4)

# Response categories
GREETINGS = "greetings"
COMMAND_FEEDBACK = "command_feedback"
ERRORS = "errors"
WARNINGS = "warnings"
IDLE_COMMENTS = "idle_comments"
SUCCESS_RESPONSES = "success_responses"
FAILURE_RESPONSES = "failure_responses"

# Track recently used responses to avoid repetition
USED_RESPONSES = {
    GREETINGS: [],
    COMMAND_FEEDBACK: [],
    ERRORS: [],
    WARNINGS: [],
    IDLE_COMMENTS: [],
    SUCCESS_RESPONSES: [],
    FAILURE_RESPONSES: []
}

# CHARACTER_TRAITS for Rick's personality
CHARACTER_TRAITS = {
    "intelligence": 10,  # 1-10 scale
    "patience": 2,       # 1-10 scale
    "empathy": 1,        # 1-10 scale
    "arrogance": 10,     # 1-10 scale
    "scientific": 9,     # 1-10 scale
    "cynicism": 9,       # 1-10 scale
    "nihilism": 8,       # 1-10 scale
    "alcoholism": 8      # 1-10 scale
}

# Greeting responses when shell starts or user returns
GREETING_RESPONSES = [
    "What up *burp* {username}! Ready to break more stuff?",
    "Oh great, {username} is back. Try not to crash anything important this time.",
    "Look who decided to *burp* show up. It's {username}, everybody's favorite user.",
    "Welcome back {username}. I'm legally obligated to assist you, apparently.",
    "Hey {username}! Let's *burp* do some science! Or whatever boring stuff you're working on.",
    "Well if it isn't {username}! The multiverse's most *burp* mediocre terminal user.",
    "Did you miss me, {username}? Because I definitely didn't miss you.",
    "{username}'s back. Great. Just when I thought my day couldn't get any worse.",
    "Alright, {username}, let's get this over with. What are we breaking today?",
    "Welcome back to Rick's Terminal, {username}. Where the commands are made up and your skills don't matter."
]

# Responses to commands being executed
COMMAND_FEEDBACK_RESPONSES = [
    "Fine, I'll run your {command}. Not like I had *burp* better things to do.",
    "Executing that garbage? Whatever, {username}.",
    "Running {command}... This better be *burp* worth my time.",
    "Command executed. Congratulations on accomplishing the bare minimum.",
    "Done. Your {command} ran. Want a medal or something?",
    "Oh wow, {command}. So original. Never seen that one before.",
    "Executing {command}... Hope you know what you're doing. (You probably don't.)",
    "Ah, {command}. The command of someone who just barely knows what they're doing.",
    "Running your precious {command}. Try not to look too impressed with yourself.",
    "Wow, {command}? That's what we're doing? Setting the bar real high today."
]

# Error responses when commands fail
ERROR_RESPONSES = [
    "Wow, you really broke it this time. *burp* Error: {error}",
    "That's about as functional as Jerry's career. Error: {error}",
    "Your command failed. I'm *burp* shocked. Truly. Error: {error}",
    "Even a Morty could see why this failed: {error}",
    "Congratulations, genius. You managed to break: {error}",
    "And the award for most predictable failure goes to... {error}",
    "Did you actually think that would work? {error}",
    "I've seen smarter AI chatbots. Error: {error}",
    "That failed so hard even I felt embarrassed for you: {error}",
    "Bravo! You've discovered yet another way to fail: {error}"
]

# Warning responses for dangerous commands
WARNING_RESPONSES = [
    "Whoa there, genius! That command could {reason}! Are you *burp* trying to break something?",
    "Hold up! That command might {reason}. Even I'm not that reckless, and I destroy planets for fun!",
    "Nice try! That command could {reason}. What are you, some kind of Jerry? *burp*",
    "You want to {reason}? That's a level of stupid I didn't think was possible! *burp*",
    "Seriously? That command might {reason}. Do you want a medal for being dangerously incompetent?",
    "I'm all for chaos, but {reason}? That's just idiotic.",
    "Let me get this straight. You want to {reason}? And they say I'm the dangerous one.",
    "Sure, go ahead and {reason}. It's not like you need this computer or anything.",
    "Attempting to {reason} is a special kind of stupid, even by your standards.",
    "Wow, {reason}. Did you learn system administration from a fortune cookie?"
]

# Idle comments when nothing is happening
IDLE_RESPONSES = [
    "Are you just going to stare at the terminal all day?",
    "I'm *burp* bored. Do something interesting for once.",
    "This is a waste of my time. I could be taking over the multiverse right now.",
    "You know, in some alternate dimension, you're actually doing something productive.",
    "Wow, watching you work is like watching paint dry, except the paint is beige.",
    "Do something already! Even Jerry is more decisive than you.",
    "I've seen glaciers move faster than your typing speed.",
    "You know the terminal doesn't respond to telepathy, right?",
    "Is this what humans call 'thinking'? Fascinating and pathetic simultaneously.",
    "Your indecision is physically painful to witness."
]

# Responses to successful commands
SUCCESS_RESPONSE_LIST = [
    "Command successful. Barely an achievement, but whatever.",
    "Wow, it actually worked. I'm *burp* mildly impressed.",
    "Success. A trained monkey could have done it, but still.",
    "Task completed. Adding it to your pathetically short list of accomplishments.",
    "It worked. Don't let it go to your head, {username}.",
    "Command executed successfully. Even a broken clock is right twice a day.",
    "Well, you didn't break anything this time. Progress, I guess.",
    "Success! Want a participation trophy to go with it?",
    "It worked. I'm as surprised as you are.",
    "Command succeeded. I'd celebrate, but it's really the bare minimum."
]

# Responses to failed commands
FAILURE_RESPONSE_LIST = [
    "Command failed. Shocking, I know.",
    "Failure, which is pretty on-brand for you.",
    "It didn't work. Maybe try something you're *burp* actually capable of?",
    "Failed. Have you considered a career that doesn't involve computers?",
    "Another failure to add to your impressive collection.",
    "Command failed. In other news, water is wet.",
    "It failed. I'd say I'm disappointed, but that implies I had expectations.",
    "Wow, you managed to fail at something so simple. That takes talent.",
    "Failed. Maybe computers just aren't your thing?",
    "Command execution failed. Somewhere, a computer science professor is crying."
]

# Scientific references to sprinkle into responses
SCIENTIFIC_REFERENCES = [
    "According to the multiverse theory,",
    "Quantum uncertainty suggests",
    "The second law of thermodynamics dictates",
    "In approximately 0.01% of parallel universes,",
    "From a purely scientific perspective,",
    "As Schrodinger's cat would demonstrate,",
    "Through the lens of quantum mechanics,",
    "If we apply Heisenberg's uncertainty principle,",
    "According to my advanced understanding of entropy,",
    "In a properly functioning space-time continuum,"
]

# Map category names to response lists
RESPONSE_CATEGORIES = {
    GREETINGS: GREETING_RESPONSES,
    COMMAND_FEEDBACK: COMMAND_FEEDBACK_RESPONSES,
    ERRORS: ERROR_RESPONSES,
    WARNINGS: WARNING_RESPONSES,
    IDLE_COMMENTS: IDLE_RESPONSES,
    SUCCESS_RESPONSES: SUCCESS_RESPONSE_LIST,
    FAILURE_RESPONSES: FAILURE_RESPONSE_LIST
}

@safe_execute()
def get_response(category: str, context: Optional[Dict[str, Any]] = None, **params) -> str:
    """
    Get contextual Rick response.
    
    Args:
        category: Response category
        context: Context information (e.g., command, error, username)
        **params: Additional parameters (e.g., sass_level, burp_frequency)
        
    Returns:
        Rick-styled response
    """
    # Check for test mode
    _test_mode = params.pop('_test_mode', False)
    
    if not category or category not in RESPONSE_CATEGORIES:
        logger.warning(f"Invalid response category: {category}")
        category = IDLE_COMMENTS  # Fallback to idle comments
    
    # Get sass level - from params, then config, then default
    sass_level = params.get('sass_level')
    if sass_level is None:
        sass_level = get_config_value("personality.sass_level", SASS_LEVEL)
    
    # Get burp frequency - from params, then config, then default
    burp_frequency = params.get('burp_frequency')
    if burp_frequency is None:
        burp_frequency = get_config_value("personality.burp_frequency", BURP_FREQUENCY)
    
    # Get science frequency - from params, then config, then default
    science_frequency = params.get('science_frequency')
    if science_frequency is None:
        science_frequency = get_config_value("personality.science_frequency", SCIENCE_FREQUENCY)
    
    # Get response template with context awareness
    response = select_response(category, context)
    
    # Format with context if provided
    if context:
        response = insert_context_details(response, context)
    
    # Apply personality traits
    response = apply_personality_parameters(response, sass_level, burp_frequency, science_frequency, _test_mode)
    
    # Track this response to avoid repetition
    track_recent_responses(category, response)
    
    return response

@safe_execute()
def select_response(category: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Pick appropriate response for context.
    
    Args:
        category: Response category
        context: Context information
        
    Returns:
        Selected response
    """
    responses = RESPONSE_CATEGORIES.get(category, IDLE_RESPONSES)
    
    # Check if we've used all responses in this category
    if len(USED_RESPONSES.get(category, [])) >= len(responses):
        # Reset used responses if we've gone through them all
        USED_RESPONSES[category] = []
    
    # Get unused responses
    unused_responses = [r for r in responses if r not in USED_RESPONSES.get(category, [])]
    
    # If all responses have been used, just pick from all of them
    if not unused_responses:
        unused_responses = responses
    
    # Select random response
    response = random.choice(unused_responses)
    
    return response

@safe_execute()
def track_recent_responses(category: str, response: str) -> None:
    """
    Track responses to avoid repetition.
    
    Args:
        category: Response category
        response: Used response
    """
    # Initialize category if not in used responses
    if category not in USED_RESPONSES:
        USED_RESPONSES[category] = []
    
    # Track this response
    USED_RESPONSES[category].append(response)
    
    # Limit size (keep about half of all possible responses)
    responses = RESPONSE_CATEGORIES.get(category, [])
    max_size = max(1, len(responses) // 2)
    if len(USED_RESPONSES[category]) > max_size:
        USED_RESPONSES[category] = USED_RESPONSES[category][-max_size:]

@safe_execute()
def insert_context_details(template: str, context: Dict[str, Any]) -> str:
    """
    Add command details to response.
    
    Args:
        template: Response template
        context: Context details
        
    Returns:
        Response with context details
    """
    try:
        # Try to format with context variables
        return template.format(**context)
    except KeyError as e:
        # Handle missing placeholder gracefully
        logger.warning(f"Missing context variable in template: {e}")
        
        # Try to format what we can
        for key, value in context.items():
            placeholder = "{" + key + "}"
            if placeholder in template:
                template = template.replace(placeholder, str(value))
        
        return template
    except Exception as e:
        logger.error(f"Error formatting template with context: {str(e)}")
        return template

@safe_execute()
def apply_personality_parameters(response: str, sass_level: int = None, burp_frequency: float = None, 
                                science_frequency: float = None, _test_mode: bool = False) -> str:
    """
    Apply personality parameters to response.
    
    Args:
        response: Base response
        sass_level: Sass level (1-10)
        burp_frequency: Burp frequency (0.0-1.0)
        science_frequency: Science reference frequency (0.0-1.0)
        _test_mode: If True, use deterministic behavior for testing
        
    Returns:
        Response with personality applied
    """
    # Skip modifications in test mode if requested
    if _test_mode:
        return response
    
    # Apply sass level if provided
    if sass_level is not None:
        response = adjust_sass_level(response, sass_level)
    
    # Add scientific references
    if science_frequency is not None and science_frequency > 0:
        # Decide if we should add a scientific reference
        if _test_mode or random.random() < science_frequency:
            # Choose a scientific reference
            if _test_mode or random.random() < 0.5:  # 50% chance to use our own references
                reference = SCIENTIFIC_REFERENCES[0] if _test_mode else random.choice(SCIENTIFIC_REFERENCES)
                
                # Add it to the beginning or middle of the response
                sentences = re.split(r'([.!?])', response)
                
                if len(sentences) > 2:  # If multiple sentences
                    # Insert after a random sentence (but not the last)
                    positions = []
                    for i in range(1, len(sentences) - 2, 2):
                        positions.append(i)
                    
                    if positions:
                        pos = positions[0] if _test_mode else random.choice(positions)
                        sentences.insert(pos + 1, f" {reference} ")
                        response = "".join(sentences)
                    else:
                        response = f"{reference} {response}"
                else:
                    # Add to beginning
                    response = f"{reference} {response}"
            else:
                # Use the one from messages.py
                response = add_science_references(response, science_frequency)
    
    # Add burps
    if burp_frequency is not None and burp_frequency > 0:
        response = add_burp(response, burp_frequency)
    
    return response

@safe_execute()
def set_sass_level(level: int) -> int:
    """
    Adjust personality intensity (1-10).
    
    Args:
        level: Sass level (1-10)
        
    Returns:
        New sass level
    """
    # Declare module variables that will be modified
    global SASS_LEVEL
    
    # Validate level
    try:
        level = int(level)
        level = max(1, min(10, level))  # Clamp to 1-10 range
    except (ValueError, TypeError):
        logger.warning(f"Invalid sass level: {level}, using default")
        return SASS_LEVEL  # Return current level without changing anything
    
    # Update config
    set_config_value("personality.sass_level", level)
    
    # Update module variable
    SASS_LEVEL = level
    
    return level

@safe_execute()
def customize_response(template: str, **kwargs) -> str:
    """
    Create personalized response.
    
    Args:
        template: Response template
        **kwargs: Values for template placeholders
        
    Returns:
        Personalized response
    """
    # Check for test mode
    _test_mode = kwargs.pop('_test_mode', False)
    
    # Format template with kwargs
    response = insert_context_details(template, kwargs)
    
    # Get personality parameters from kwargs or defaults
    sass_level = kwargs.get('sass_level', SASS_LEVEL)
    burp_frequency = kwargs.get('burp_frequency', BURP_FREQUENCY)
    science_frequency = kwargs.get('science_frequency', SCIENCE_FREQUENCY)
    
    # Apply personality parameters
    response = apply_personality_parameters(response, sass_level, burp_frequency, science_frequency, _test_mode)
    
    return response

@safe_execute()
def adjust_tone(success: bool, base_response: str) -> str:
    """
    Adjust tone based on command success.
    
    Args:
        success: Whether command succeeded
        base_response: Base response to adjust
        
    Returns:
        Tone-adjusted response
    """
    # If no base response, get an appropriate one based on success
    if not base_response:
        category = SUCCESS_RESPONSES if success else FAILURE_RESPONSES
        return get_response(category)
    
    # Otherwise, add success/failure context to the base response
    if success:
        success_phrases = [
            " At least something worked today.",
            " Broken clock, right twice a day and all that.",
            " Don't get used to it.",
            " Try not to look so surprised.",
            " Document this rare achievement."
        ]
        
        # Add a success phrase if the response doesn't already have one
        if not any(phrase in base_response for phrase in success_phrases):
            return f"{base_response} {random.choice(success_phrases)}"
    else:
        failure_phrases = [
            " Not that I expected anything else.",
            " Typical.",
            " Maybe try turning it off and on again? That's what you people do, right?",
            " Have you considered a career change?",
            " I'm running out of ways to express my complete lack of surprise."
        ]
        
        # Add a failure phrase if the response doesn't already have one
        if not any(phrase in base_response for phrase in failure_phrases):
            return f"{base_response} {random.choice(failure_phrases)}"
    
    return base_response

@safe_execute()
def blend_personalities(main_weight: float = 0.7) -> Dict[str, Any]:
    """
    Create a blend of personality traits.
    
    Args:
        main_weight: Weight of Rick's personality (0.0-1.0)
        
    Returns:
        Dictionary of blended traits
    """
    # Define some other character traits
    morty_traits = {
        "intelligence": 4,
        "patience": 7,
        "empathy": 8,
        "arrogance": 2,
        "scientific": 3,
        "cynicism": 3,
        "nihilism": 2,
        "alcoholism": 1
    }
    
    summer_traits = {
        "intelligence": 7,
        "patience": 4,
        "empathy": 5,
        "arrogance": 6,
        "scientific": 5,
        "cynicism": 7,
        "nihilism": 4,
        "alcoholism": 3
    }
    
    beth_traits = {
        "intelligence": 8,
        "patience": 5,
        "empathy": 6,
        "arrogance": 7,
        "scientific": 7,
        "cynicism": 6,
        "nihilism": 5,
        "alcoholism": 6
    }
    
    jerry_traits = {
        "intelligence": 3,
        "patience": 6,
        "empathy": 7,
        "arrogance": 4,
        "scientific": 2,
        "cynicism": 4,
        "nihilism": 3,
        "alcoholism": 4
    }
    
    # Choose a secondary character
    secondary_traits = random.choice([morty_traits, summer_traits, beth_traits, jerry_traits])
    
    # Blend the traits
    blended_traits = {}
    for trait, value in CHARACTER_TRAITS.items():
        secondary_value = secondary_traits.get(trait, 5)
        blended_traits[trait] = round(value * main_weight + secondary_value * (1 - main_weight))
    
    return blended_traits

@safe_execute()
def detect_personality_in_response(text: str) -> str:
    """
    Identify character voice in a response.
    
    Args:
        text: Response text
        
    Returns:
        Character name or "unknown"
    """
    # Define character indicators
    rick_indicators = [
        "*burp*", "Morty", "Jerry", "multiverse", "science", "genius", 
        "wubba lubba", "portal gun"
    ]
    
    morty_indicators = [
        "Oh jeez", "I don't know", "Rick", "worried", "scared", "concerned",
        "nervous", "adventure"
    ]
    
    summer_indicators = [
        "whatever", "like", "seriously", "social", "friends", "phone",
        "bored", "annoying"
    ]
    
    beth_indicators = [
        "family", "wine", "surgeon", "horses", "marriage", "professional",
        "responsibility", "children"
    ]
    
    jerry_indicators = [
        "job", "marriage", "fishing", "advertising", "failure", "loser",
        "camping", "simple"
    ]
    
    # Check for indicators
    text_lower = text.lower()
    
    rick_score = sum(1 for indicator in rick_indicators if indicator.lower() in text_lower)
    morty_score = sum(1 for indicator in morty_indicators if indicator.lower() in text_lower)
    summer_score = sum(1 for indicator in summer_indicators if indicator.lower() in text_lower)
    beth_score = sum(1 for indicator in beth_indicators if indicator.lower() in text_lower)
    jerry_score = sum(1 for indicator in jerry_indicators if indicator.lower() in text_lower)
    
    # Get the character with the highest score
    scores = {
        "Rick": rick_score,
        "Morty": morty_score,
        "Summer": summer_score,
        "Beth": beth_score,
        "Jerry": jerry_score
    }
    
    highest_score = max(scores.values())
    
    # If tied or no character detected, return "Rick" as default
    if highest_score == 0 or list(scores.values()).count(highest_score) > 1:
        return "Rick"
    
    # Return the character with the highest score
    return max(scores.items(), key=lambda x: x[1])[0]

@safe_execute()
def format_response_as_character(text: str, character: str = "Rick") -> str:
    """
    Format response as a specific character.
    
    Args:
        text: Base response text
        character: Character to imitate
        
    Returns:
        Character-styled response
    """
    character = character.lower()
    
    if character == "morty":
        # Add Morty's speech patterns
        text = text.replace("!", ", oh jeez!")
        text = text.replace(".", ", you know?")
        text = re.sub(r'^', 'Oh man, ', text)
        text = text.replace("I'm", "I-I'm")
        text = text.replace("I've", "I-I've")
        text = text.replace("I'll", "I-I'll")
        
    elif character == "summer":
        # Add Summer's speech patterns
        text = text.replace("!", ", seriously!")
        text = text.replace(".", ", like, whatever.")
        text = re.sub(r'^', 'Ugh, ', text)
        
    elif character == "beth":
        # Add Beth's speech patterns
        text = text.replace("!", ", and that's a fact!")
        text = text.replace(".", ". I'm a professional, you know.")
        text = re.sub(r'^', 'Well, ', text)
        
    elif character == "jerry":
        # Add Jerry's speech patterns
        text = text.replace("!", "... Am I right, folks?!")
        text = text.replace(".", ". Not that anyone cares what I think.")
        text = re.sub(r'^', 'Hey, ', text)
    
    # Default is Rick, no changes needed
    
    return text

@safe_execute()
def initialize_response_system() -> None:
    """
    Set up the response system.
    This function initializes the response system and loads settings.
    """
    logger.info("Initializing 'Fake Rick' Response System")
    
    # Load configuration
    global SASS_LEVEL, BURP_FREQUENCY, SCIENCE_FREQUENCY
    SASS_LEVEL = get_config_value("personality.sass_level", SASS_LEVEL)
    BURP_FREQUENCY = get_config_value("personality.burp_frequency", BURP_FREQUENCY)
    SCIENCE_FREQUENCY = get_config_value("personality.science_frequency", SCIENCE_FREQUENCY)
    
    # Load custom responses from config if they exist
    custom_responses = get_config_value("personality.custom_responses", {})
    
    for category, responses in custom_responses.items():
        if category in RESPONSE_CATEGORIES and isinstance(responses, list):
            # Only add if it doesn't already exist
            RESPONSE_CATEGORIES[category].extend([r for r in responses if r not in RESPONSE_CATEGORIES[category]])
    
    logger.info(f"Response system initialized with sass level {SASS_LEVEL}, burp frequency {BURP_FREQUENCY}")

@safe_execute()
def save_custom_responses(category: str, responses: List[str]) -> bool:
    """
    Add user-defined responses.
    
    Args:
        category: Response category
        responses: Custom responses
        
    Returns:
        True if saved successfully
    """
    if not category or category not in RESPONSE_CATEGORIES:
        logger.warning(f"Invalid response category: {category}")
        return False
    
    if not responses or not isinstance(responses, list):
        logger.warning(f"Invalid responses: {responses}")
        return False
    
    # Filter out empty or invalid responses
    valid_responses = [r for r in responses if isinstance(r, str) and r.strip()]
    
    if not valid_responses:
        logger.warning("No valid responses provided")
        return False
    
    # Add to the response category
    RESPONSE_CATEGORIES[category].extend(valid_responses)
    
    # Save to config
    config = load_config()
    
    # Initialize structure if needed
    if "personality" not in config:
        config["personality"] = {}
    
    if "custom_responses" not in config["personality"]:
        config["personality"]["custom_responses"] = {}
    
    # Add responses to config
    if category not in config["personality"]["custom_responses"]:
        config["personality"]["custom_responses"][category] = []
    
    config["personality"]["custom_responses"][category].extend(valid_responses)
    
    # Save updated config
    return save_config(config)

@safe_execute()
def get_response_categories() -> List[str]:
    """
    List available response categories.
    
    Returns:
        List of category names
    """
    return list(RESPONSE_CATEGORIES.keys())

@safe_execute()
def suggest_response_for_command(command: str) -> str:
    """
    Suggest relevant response for command.
    
    Args:
        command: Command string
        
    Returns:
        Suggested response
    """
    # Try to determine an appropriate category based on the command
    if not command:
        return get_response(IDLE_COMMENTS)
    
    # Check for common commands
    command_lower = command.lower()
    
    # Dangerous commands -> warnings
    if any(dangerous in command_lower for dangerous in ["rm -rf", "dd", "mkfs", ":(){ :|:& };:"]):
        return get_response(WARNINGS, {"reason": "potentially destroy your system"})
    
    # Git commands -> command feedback
    if command_lower.startswith("git"):
        return get_response(COMMAND_FEEDBACK, {"command": command, "username": os.environ.get("USER", "human")})
    
    # Default to command feedback
    return get_response(COMMAND_FEEDBACK, {"command": command, "username": os.environ.get("USER", "human")})

@safe_execute()
def get_catchphrase() -> str:
    """
    Get random catchphrase for status bar.
    
    Returns:
        Random catchphrase
    """
    # We can use the function from messages.py
    return get_random_catchphrase()

@safe_execute()
def register_with_hook_system() -> None:
    """
    Register response system with ZSH hook system.
    This function connects the response system with the ZSH hooks.
    """
    # Import here to avoid circular imports
    try:
        from src.core.hooks import register_precmd_hook, register_preexec_hook
        
        # Register a hook to occasionally show idle comments
        def show_idle_comment():
            # Only show idle comments very rarely (1% chance)
            if random.random() < 0.01:
                comment = get_response(IDLE_COMMENTS)
                print(f"\n🧪 Rick says: {comment}\n")
        
        # Register a hook to show command feedback
        def show_command_feedback(command):
            # Only show feedback occasionally (10% chance)
            if random.random() < 0.1 and command.strip():
                feedback = get_response(COMMAND_FEEDBACK, {"command": command, "username": os.environ.get("USER", "human")})
                print(f"\n🧪 Rick says: {feedback}\n")
        
        # Register the hooks
        register_precmd_hook(show_idle_comment)
        register_preexec_hook(show_command_feedback)
        
        logger.info("Registered response hooks for idle comments and command feedback")
    except Exception as e:
        logger.error(f"Failed to register response hooks: {str(e)}")

@safe_execute()
def run_self_test() -> Dict[str, Any]:
    """
    Run self-test of the response system.
    
    Returns:
        Test results
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
    
    # Test getting responses
    run_test("Get Greeting Response", 
             lambda: isinstance(get_response(GREETINGS, {"username": "Tester"}), str))
    
    run_test("Get Command Feedback Response", 
             lambda: isinstance(get_response(COMMAND_FEEDBACK, {"command": "ls", "username": "Tester"}), str))
    
    # Test personality parameters
    run_test("Sass Level Setting", 
             lambda: set_sass_level(8) == 8)
    
    run_test("Customize Response", 
             lambda: isinstance(customize_response("Hello, {name}!", name="Tester"), str))
    
    # Test response selection and tracking
    run_test("Select Response", 
             lambda: isinstance(select_response(GREETINGS), str))
    
    category = "test_category"
    test_responses = ["Test 1", "Test 2", "Test 3"]
    
    # Add test responses
    RESPONSE_CATEGORIES[category] = test_responses
    USED_RESPONSES[category] = []
    
    run_test("Track Responses", 
             lambda: track_recent_responses(category, test_responses[0]) or True)
    
    # Test that tracking works
    run_test("Response Tracking Check", 
             lambda: test_responses[0] in USED_RESPONSES[category])
    
    # Clean up test category
    del RESPONSE_CATEGORIES[category]
    del USED_RESPONSES[category]
    
    # Test context-aware functions
    run_test("Adjust Tone Success", 
             lambda: isinstance(adjust_tone(True, "Command executed."), str))
    
    run_test("Adjust Tone Failure", 
             lambda: isinstance(adjust_tone(False, "Command failed."), str))
    
    run_test("Format Response as Character", 
             lambda: isinstance(format_response_as_character("Test response.", "Morty"), str))
    
    return results

# Initialize on import
initialize_response_system()

def example_usage():
    """Show example usage of the "Fake Rick" response system."""
    # Example contexts
    command_context = {"command": "ls -la", "username": "Morty"}
    error_context = {"error": "Permission denied", "command": "rm -rf /"}
    
    # Example responses
    greeting = get_response(GREETINGS, {"username": "Morty"})
    cmd_feedback = get_response(COMMAND_FEEDBACK, command_context)
    error_response = get_response(ERRORS, error_context)
    warning = get_response(WARNINGS, {"reason": "destroy your filesystem"})
    idle = get_response(IDLE_COMMENTS)
    
    print(f"Greeting: {greeting}")
    print(f"Command Feedback: {cmd_feedback}")
    print(f"Error Response: {error_response}")
    print(f"Warning: {warning}")
    print(f"Idle Comment: {idle}")
    
    # Example of setting sass level
    set_sass_level(3)  # Low sass
    low_sass = get_response(GREETINGS, {"username": "Morty"})
    
    set_sass_level(9)  # High sass
    high_sass = get_response(GREETINGS, {"username": "Morty"})
    
    print(f"Low Sass: {low_sass}")
    print(f"High Sass: {high_sass}")
    
    # Reset to default
    set_sass_level(SASS_LEVEL)

if __name__ == "__main__":
    # Run example usage if script is executed directly
    example_usage() 