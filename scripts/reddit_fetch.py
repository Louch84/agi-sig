#!/usr/bin/env python3
"""Fetch recent posts from a subreddit using PRAW."""
import praw
import sys
import os
from datetime import datetime, timedelta

def main():
    subreddits = ["MachineLearning", "LocalLLaMA", "artificial", "artificialintelligence"]
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    # Check for env vars
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "SigBotti/1.0 (AI agent)")
    
    if not client_id or not client_secret:
        print("ERROR: Reddit API credentials not set.")
        print("Set these env vars to enable Reddit monitoring:")
        print("  REDDIT_CLIENT_ID     — your Reddit app client ID")
        print("  REDDIT_CLIENT_SECRET — your Reddit app client secret")
        print("\nTo create an app: https://www.reddit.com/prefs/apps")
        print("  Choose 'script' type, set redirect URI to http://localhost:8080")
        return 1
    
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )
    
    cutoff = datetime.now() - timedelta(hours=24)
    
    for sub in subreddits:
        print(f"\n=== r/{sub} (last {limit} posts) ===")
        try:
            subreddit = reddit.subreddit(sub)
            for i, post in enumerate(subreddit.new(limit=limit)):
                age = datetime.fromtimestamp(post.created_utc)
                age_str = "NEW" if age > cutoff else age.strftime("%m-%d %H:%M")
                print(f"  [{age_str}] {post.score:>6}pts | {post.title[:100]}")
                if i >= limit - 1:
                    break
        except Exception as e:
            print(f"  ERROR: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
