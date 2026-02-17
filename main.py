from agent import run_agent

def main():
    print("🤖 AI Assistant (Email + Web Search)")
    print("="*40)
    print("Examples:")
    print("• Send an email to john@example.com about the meeting")
    print("• What's the latest news about AI?")
    print("• Send reminder to team@company.com")
    print("• Tell me about Python programming")
    print("\nType 'exit' to quit\n")
    
    while True:
        query = input("Ask me anything: ")
        if query.lower() == 'exit':
            break
        
        if query.strip():
            try:
                run_agent(query)
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("Please enter a valid request.")

if __name__ == "__main__":
    main()