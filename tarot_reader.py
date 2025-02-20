import random
import boto3
import json
import sys

# Initialize Bedrock Client with the correct region
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-west-2")

# Use Claude 3.5 Sonnet for Tarot Readings
MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Tarot deck: Major & Minor Arcana
TAROT_DECK = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun",
    "Judgment", "The World"
] + [f"{suit} {rank}" for suit in ["Cups", "Wands", "Swords", "Pentacles"]
     for rank in ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Page", "Knight", "Queen", "King"]]

# 🔮 Call Amazon Bedrock (Claude 3.5 Sonnet)
def call_bedrock(prompt):
    """Calls Amazon Bedrock's Claude 3.5 model with properly formatted chat-style input."""

    body = {
        "anthropic_version": "bedrock-2023-05-31",  # Required for Claude
        "messages": [
            {"role": "user", "content": prompt}  # Proper Claude format
        ],
        "max_tokens": 700,
        "temperature": 0.7
    }

    response = bedrock_runtime.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body)
    )

    result = json.loads(response["body"].read().decode("utf-8"))

    # Ensure we extract the response text properly
    if isinstance(result["content"], list):  # If Claude returns a list
        return "\n".join([msg["text"] for msg in result["content"]]).strip()
    elif isinstance(result["content"], str):  # If Claude returns a single string
        return result["content"].strip()
    else:
        return "⚠️ Error: Unexpected response format from Claude."

# Step 1: Determine the best tarot spread (Claude responds with only "3" or "5")
def determine_spread(user_question):
    """Uses Claude AI to determine whether a 3-card or 5-card spread is needed."""

    prompt = (
        f"The user asked: '{user_question}'. "
        "Based on the complexity of the question, respond ONLY with the number 3 or 5. "
        "Use 3 for simple, past-present-future questions. "
        "Use 5 for complex, multi-layered concerns that need extra insight. "
        "Do NOT provide any explanation. Just return 3 or 5."
    )

    response = call_bedrock(prompt).strip()

    # Ensure the response is either "3" or "5" (fallback to 3 if invalid)
    return 3 if response == "3" else 5

# Step 2: Draw Tarot Cards
def draw_tarot_cards(num_cards):
    """Draws a given number of tarot cards randomly."""
    random.shuffle(TAROT_DECK)
    return TAROT_DECK[:num_cards]

# Step 3: Generate Tarot Reading (Now includes embedded spread reasoning)
def tarot_reading(cards, user_question, spread_size):
    """Uses Claude AI to interpret the tarot cards in relation to the user's concern, embedding spread reasoning."""
    
    # Ask for spread reasoning and embed it naturally into the reading prompt
    spread_reasoning_prompt = (
        f"The user asked: '{user_question}'. "
        f"You determined that a {spread_size}-card spread is best. "
        "Briefly explain why this is the best choice, in a way that flows naturally into the tarot reading."
    )
    spread_reasoning = call_bedrock(spread_reasoning_prompt)

    # Full tarot reading prompt including the embedded spread reasoning
    prompt = (
        f"The user asked: '{user_question}'. They drew these tarot cards: {', '.join(cards)}. "
        f"{spread_reasoning} Now, provide a detailed interpretation of each card and how it relates to their question. "
        "Then, summarize the overall reading with key takeaways."
    )

    return call_bedrock(prompt)

# Main Function
def ask_tarot(user_question):
    """Runs the tarot reading workflow based on user intention."""
    print("\n🔮 Determining the best tarot spread for your question...")
    spread_size = determine_spread(user_question)

    print(f"\n📜 Spread chosen: {spread_size}-card spread")

    print("🔀 Drawing your tarot cards...")
    drawn_cards = draw_tarot_cards(spread_size)
    print(f"🃏 Cards drawn: {', '.join(drawn_cards)}\n")

    print("📖 Interpreting your reading...\n")
    reading = tarot_reading(drawn_cards, user_question, spread_size)

    # Print the final formatted response clearly
    print("\n🔮 Interpretation:\n")
    print(reading)
    
    print("\n🌟 Thank you for consulting the tarot. May clarity be with you! 🌟\n")

# CLI Support
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Error: Please provide your concern as a command-line argument.")
        print("Usage: python tarot_reader.py \"Should I change my career?\"")
        sys.exit(1)

    user_input = " ".join(sys.argv[1:])
    ask_tarot(user_input)
