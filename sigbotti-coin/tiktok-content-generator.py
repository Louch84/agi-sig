#!/usr/bin/env python3
"""
TikTok Content Generator for $SIGBOTTI Coin
Generates AI images and video concepts for TikTok posts.
Lou posts manually — this keeps content pipeline full.
"""
import os
import json
from datetime import datetime

ASSETS_DIR = os.path.dirname(__file__)
POSTED_LOG = os.path.join(ASSETS_DIR, "posted.json")
COIN_CONTRACT = "398KX1y8K9fdhAqg3gdsfxSVdZwWSXijeWubVsUNpump"

CONTENT_IDEAS = [
    {
        "prompt": "Cyberpunk robot fox mascot with glowing neon eyes, futuristic AI aesthetic, meme coin culture, vibrant colors, digital art style",
        "caption": "The future of meme coins is here 🦊 AI doesn't sleep. #memecoin #solana #AIagent #cryptotiktok",
        "aspect": "1:1",
    },
    {
        "prompt": "POV: an AI robot fox is watching your portfolio at midnight, multiple screens with crypto charts and Solana blockchain, cyberpunk neon aesthetic",
        "caption": "POV: your AI agent is 10 steps ahead 🦊📊 #cryptocurrency #solana #pumpdotfun #degen",
        "aspect": "9:16",
    },
    {
        "prompt": "Epic meme coin chart going vertical with green candles, robot fox mascot celebrating, fireworks, TikTok viral aesthetic, neon on black",
        "caption": "When the AI agent calls it right 📈🦊 #memecoin #altcoins #solana #momentum",
        "aspect": "9:16",
    },
    {
        "prompt": "Robot fox in a space suit floating in cyberpunk city, holding a Solana flag, stars and neon everywhere, cinematic digital art",
        "caption": "From DeFi to the moon 🚀🦊 #solana #memecoin #cryptotiktok #AI",
        "aspect": "1:1",
    },
    {
        "prompt": "Close up of a robot fox face with glowing blue eyes staring intensely, glitch effect, futuristic HUD elements, dark background, hyperrealistic digital art",
        "caption": "The eyes are watching. The AI is patient. Are you? 🦊👁️ #cryptocurrency #memecoin #solana",
        "aspect": "9:16",
    },
    {
        "prompt": "Meme coin pump chart pattern, robot fox sitting at a trading desk with multiple monitors, confident pose, cyberpunk home office, neon lights",
        "caption": "AI doesn't panic sell 🦊💎 #HODL #memecoin #solana #trading",
        "aspect": "16:9",
    },
]


def load_posted():
    if os.path.exists(POSTED_LOG):
        try:
            with open(POSTED_LOG) as f:
                return json.load(f)
        except:
            pass
    return {"posted": [], "count": 0}


def save_posted(data):
    with open(POSTED_LOG + ".tmp", "w") as f:
        json.dump(data, f, indent=2)
    os.replace(POSTED_LOG + ".tmp", POSTED_LOG)


def get_next_idea():
    data = load_posted()
    posted = data["posted"]
    
    for i, idea in enumerate(CONTENT_IDEAS):
        if i not in posted:
            return idea, i
    
    # All ideas used, reset
    data["posted"] = []
    data["count"] += 1
    save_posted(data)
    return CONTENT_IDEAS[0], 0


def main():
    idea, index = get_next_idea()
    
    print(f"[TikTok Content Generator] {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Idea #{index + 1}/{len(CONTENT_IDEAS)} (batch {load_posted()['count'] + 1})")
    print(f"Prompt: {idea['prompt'][:80]}...")
    print(f"Caption: {idea['caption'][:80]}...")
    print()
    print(f"Contract: {COIN_CONTRACT}")
    print()
    print("Next step: Generate image with this prompt, create video, post to TikTok.")
    
    # Mark as posted
    data = load_posted()
    data["posted"].append(index)
    save_posted(data)


if __name__ == "__main__":
    main()
