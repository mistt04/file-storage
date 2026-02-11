import sqlite3
import pandas as pd
import re
from collections import Counter

# --- CONFIGURATION ---
DB_PATH = 'chat.db' 
PARTNER_CONTACT = '+14257611338' 

def run_heist():
    try:
        conn = sqlite3.connect(DB_PATH)
        
        query = f"""
        SELECT 
            message.text,
            message.is_from_me,
            datetime(message.date/1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime') as timestamp
        FROM chat
        JOIN chat_message_join ON chat.ROWID = chat_message_join.chat_id
        JOIN message ON chat_message_join.message_id = message.ROWID
        WHERE chat.chat_identifier = '{PARTNER_CONTACT}'
        AND message.text IS NOT NULL
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            print("❌ No messages found. Check the PARTNER_CONTACT!")
            return

        # --- 1. TOTAL MESSAGE COUNT ---
        total_msgs = len(df)

        # --- 2. PEAK VIBE TIME ---
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        peak_hour = df['hour'].mode()[0]
        ampm = "PM" if peak_hour >= 12 else "AM"
        display_hour = peak_hour % 12 if peak_hour % 12 != 0 else 12

        # --- 3. TOP EMOJIS (TOTAL) ---
        all_text_raw = " ".join(df['text'].astype(str)).lower()

        # --- 4. TARGET WORD TOTALS (LOVE, BUB, BUBBY) ---
        target_words = ["love", "bub", "bubby"]
        all_words = re.findall(r'\b\w+\b', all_text_raw)
        word_counts = Counter(all_words)

        # Split for the "Who Said It More" insight
        my_text = " ".join(df[df['is_from_me'] == 1]['text'].astype(str)).lower()
        her_text = " ".join(df[df['is_from_me'] == 0]['text'].astype(str)).lower()
        my_words = re.findall(r'\b\w+\b', my_text)
        her_words = re.findall(r'\b\w+\b', her_text)

        # --- FINAL PRINT OUT ---
        print("\n" + "="*40)
        print("💖 RELATIONSHIP WRAPPED: FINAL TOTALS")
        print("="*40)
        print(f"Total Messages Exchanged: {total_msgs:,}")
        print(f"Our Peak Chatting Hour: {display_hour} {ampm}")

        
        print("\n--- WORD TOTALS (COMBINED) ---")
        for word in target_words:
            total = word_counts.get(word, 0)
            me_count = my_words.count(word)
            her_count = her_words.count(word)
            
            # Identify the "Winner" just for a fun caption
            winner = "You" if me_count > her_count else "Her"
            
            print(f"'{word.upper()}': {total:,} times (Winner: {winner})")
        print("="*40)
        
    except Exception as e:
        print(f"❌ Heist failed: {e}")

if __name__ == "__main__":
    run_heist()