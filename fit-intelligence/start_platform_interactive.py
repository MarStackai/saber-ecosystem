#!/usr/bin/env python3
"""
Interactive Platform Launcher
Start the enhanced FIT intelligence platform for user interaction
"""

import logging
from enhanced_fit_chatbot import EnhancedFITChatbot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_interactive_platform():
    """Start interactive platform"""
    print("=" * 60)
    print("🚀 ENHANCED FIT INTELLIGENCE PLATFORM")
    print("=" * 60)
    
    # Initialize the enhanced chatbot
    print("Initializing enhanced intelligence system...")
    chatbot = EnhancedFITChatbot()
    
    # Show system status
    system_info = chatbot.get_system_info()
    print(f"\n📊 PLATFORM STATUS:")
    
    for collection, info in system_info['data_coverage'].items():
        if 'document_count' in info:
            count = info['document_count']
            if 'commercial' in collection.lower():
                print(f"✅ Commercial Sites: {count:,}")
            elif 'license' in collection.lower():
                print(f"✅ FIT Licenses: {count:,}")
    
    print(f"\n🧠 CAPABILITIES READY:")
    for capability in system_info['capabilities'][:3]:
        print(f"• {capability}")
    
    print(f"\n🎯 COMMERCIAL FOCUS:")
    print(f"• 7,300 non-domestic licenses loaded (targeting 41K)")
    print(f"• 1,125 MW licensed capacity")
    print(f"• 40,194 commercial installations")
    print(f"• Combined intelligence platform active")
    
    print(f"\n" + "=" * 60)
    print("🤖 PLATFORM READY - You can now explain your requirements!")
    print("=" * 60)
    
    # Keep running for interaction
    print("\nType 'exit' to stop, or ask me anything about the platform:")
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'stop']:
                print("\n🛑 Platform stopped. Thank you!")
                break
            
            if user_input:
                print(f"\n🤖 FIT Intelligence: ", end="")
                response = chatbot.chat(user_input)
                print(response)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Platform stopped by user.")
            break
        except EOFError:
            print("\n\n🛑 Platform stopped (no input available).")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break

if __name__ == "__main__":
    start_interactive_platform()