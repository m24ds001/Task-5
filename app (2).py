import gradio as gr
from transformers import pipeline
import random

# Initialize sentiment analysis model
print("Loading sentiment analysis model...")
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)
print("Model loaded successfully!")

class SentimentAwareChatbot:
    def __init__(self):
        self.conversation_history = []
        self.sentiment_history = []
        
    def analyze_sentiment(self, text):
        """Analyze sentiment of user input"""
        result = sentiment_analyzer(text)[0]
        label = result['label']
        score = result['score']
        
        # Map to standardized labels
        if label == "POSITIVE":
            sentiment = "positive"
        elif label == "NEGATIVE":
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        return sentiment, score
    
    def get_sentiment_response_prefix(self, sentiment, score):
        """Generate appropriate response based on sentiment"""
        if sentiment == "positive" and score > 0.8:
            prefixes = [
                "I'm glad to hear that! 😊 ",
                "That's wonderful! ",
                "Great to hear! ",
                "I'm happy you feel that way! ",
                "Excellent! "
            ]
        elif sentiment == "negative" and score > 0.7:
            prefixes = [
                "I understand your frustration. Let me help you with that. ",
                "I'm sorry to hear that. I'm here to assist you. ",
                "I apologize for any inconvenience. ",
                "I can see this is concerning. Let me help resolve this. ",
                "I understand this is frustrating. "
            ]
        elif sentiment == "negative" and score > 0.5:
            prefixes = [
                "I understand. ",
                "Let me help you with that. ",
                "I'm here to assist. "
            ]
        else:
            prefixes = [""]
        
        return random.choice(prefixes)
    
    def generate_response(self, user_message):
        """Generate chatbot response with sentiment awareness"""
        # Analyze sentiment
        sentiment, score = self.analyze_sentiment(user_message)
        self.sentiment_history.append({
            "message": user_message,
            "sentiment": sentiment,
            "score": score
        })
        
        # Get sentiment-appropriate prefix
        response_prefix = self.get_sentiment_response_prefix(sentiment, score)
        
        # Generate base response
        base_response = self.generate_base_response(user_message, sentiment)
        
        # Combine prefix with response
        full_response = response_prefix + base_response
        
        self.conversation_history.append({
            "user": user_message,
            "bot": full_response,
            "sentiment": sentiment,
            "score": score
        })
        
        return full_response, sentiment, score
    
    def generate_base_response(self, message, sentiment):
        """Generate base response (rule-based system)"""
        message_lower = message.lower()
        
        # Greeting patterns
        if any(word in message_lower for word in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]):
            return "Hello! How can I assist you today?"
        
        # Thank you patterns
        elif any(word in message_lower for word in ["thank", "thanks", "appreciate", "grateful"]):
            return "You're welcome! Is there anything else I can help you with?"
        
        # Problem/issue patterns
        elif any(word in message_lower for word in ["problem", "issue", "error", "wrong", "not working", "broken", "bug"]):
            return "I'd be happy to help you resolve this issue. Could you please provide more details about what's happening?"
        
        # Product inquiry
        elif any(word in message_lower for word in ["product", "item", "purchase", "buy", "price", "cost"]):
            return "I can help you with product information. What would you like to know?"
        
        # Refund/return
        elif any(word in message_lower for word in ["refund", "return", "money back", "cancel order"]):
            return "I understand you'd like to discuss a refund or return. Let me help you with the process. Do you have your order number?"
        
        # Delivery/shipping
        elif any(word in message_lower for word in ["delivery", "shipping", "track", "order", "package", "arrive"]):
            return "I can help you track your order. Please provide your order number or tracking ID, and I'll check the status for you."
        
        # Account issues
        elif any(word in message_lower for word in ["account", "login", "password", "sign in", "access"]):
            return "I can help you with account-related issues. What specific problem are you experiencing?"
        
        # Payment issues
        elif any(word in message_lower for word in ["payment", "credit card", "charge", "billing"]):
            return "I'll help you resolve the payment issue. Can you describe what happened with your payment?"
        
        # Complaint patterns
        elif any(word in message_lower for word in ["complaint", "disappointed", "angry", "terrible", "horrible", "worst"]):
            return "I sincerely apologize for your negative experience. Your feedback is important to us. Please share the details so I can help make this right."
        
        # Compliment patterns
        elif any(word in message_lower for word in ["love", "amazing", "excellent", "perfect", "best", "awesome"]):
            return "Thank you so much for your positive feedback! It means a lot to us. Is there anything else you'd like to know?"
        
        # Help patterns
        elif any(word in message_lower for word in ["help", "assist", "support", "question"]):
            return "Of course! I'm here to help. What do you need assistance with?"
        
        # Goodbye patterns
        elif any(word in message_lower for word in ["bye", "goodbye", "see you", "take care"]):
            return "Goodbye! Feel free to reach out if you need any further assistance. Have a great day!"
        
        # Default response based on sentiment
        else:
            if sentiment == "negative":
                return "I want to make sure I address your concerns properly. Could you please tell me more about what you need help with?"
            elif sentiment == "positive":
                return "I'm here to help! What can I assist you with today?"
            else:
                return "I'm here to assist you. Could you please provide more details about what you need?"
    
    def get_sentiment_summary(self):
        """Get summary of conversation sentiments"""
        if not self.sentiment_history:
            return "No conversation history yet."
        
        positive = sum(1 for s in self.sentiment_history if s['sentiment'] == 'positive')
        negative = sum(1 for s in self.sentiment_history if s['sentiment'] == 'negative')
        neutral = sum(1 for s in self.sentiment_history if s['sentiment'] == 'neutral')
        total = len(self.sentiment_history)
        
        avg_positive_score = sum(s['score'] for s in self.sentiment_history if s['sentiment'] == 'positive') / positive if positive > 0 else 0
        avg_negative_score = sum(s['score'] for s in self.sentiment_history if s['sentiment'] == 'negative') / negative if negative > 0 else 0
        
        summary = f"""📊 Conversation Sentiment Summary
        
📈 Total Messages: {total}
        
Sentiment Distribution:
• Positive: {positive} messages ({positive/total*100:.1f}%)
• Negative: {negative} messages ({negative/total*100:.1f}%)
• Neutral: {neutral} messages ({neutral/total*100:.1f}%)

Average Confidence Scores:
• Positive: {avg_positive_score:.3f}
• Negative: {avg_negative_score:.3f}

Customer Satisfaction Indicator:
{"🟢 High (Mostly Positive)" if positive > negative else "🔴 Low (Needs Attention)" if negative > positive else "🟡 Neutral"}
        """
        return summary
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.sentiment_history = []
        return "Conversation history cleared!"

# Initialize chatbot
chatbot = SentimentAwareChatbot()

def chat_interface(message, history):
    """Gradio chat interface"""
    response, sentiment, score = chatbot.generate_response(message)
    
    # Format sentiment info
    sentiment_emoji = "😊" if sentiment == "positive" else "😟" if sentiment == "negative" else "😐"
    sentiment_info = f"\n\n*[Sentiment: {sentiment.title()} {sentiment_emoji} | Confidence: {score:.2%}]*"
    
    return response + sentiment_info

def get_summary():
    """Get conversation summary"""
    return chatbot.get_sentiment_summary()

def reset_chat():
    """Reset the conversation"""
    return chatbot.reset_conversation()

# Create Gradio interface
with gr.Blocks(title="Sentiment-Aware Chatbot", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 Sentiment-Aware Customer Service Chatbot
    
    This AI chatbot detects customer emotions in real-time and adapts its responses accordingly to provide better customer service.
    
    **Features:**
    - 🎯 Real-time sentiment analysis
    - 💬 Context-aware responses
    - 📊 Conversation analytics
    - 😊 Emotion-based tone adjustment
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot_ui = gr.ChatInterface(
                chat_interface,
                examples=[
                    "Hello! I need help with my order",
                    "I'm very disappointed with the product quality",
                    "Thank you so much! You've been really helpful",
                    "This is frustrating! My order hasn't arrived yet",
                    "I love this product! It's amazing!",
                    "Can you help me track my package?",
                    "I want to return this item",
                    "Your service is terrible!"
                ],
                title="💬 Chat",
                description="Start chatting below. The bot will detect your sentiment and respond accordingly.",
                retry_btn=None,
                undo_btn=None,
                clear_btn="🗑️ Clear Chat"
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Analytics Dashboard")
            
            with gr.Group():
                summary_btn = gr.Button("📈 Get Conversation Summary", variant="primary")
                summary_output = gr.Textbox(
                    label="Sentiment Analysis Summary",
                    lines=12,
                    interactive=False,
                    placeholder="Click the button above to see conversation analytics..."
                )
                
                summary_btn.click(get_summary, outputs=summary_output)
            
            gr.Markdown("""
            ### 🎯 How Sentiment Detection Works
            
            The chatbot uses advanced NLP to detect:
            
            - ✅ **Positive Sentiment**
              - Enthusiastic responses
              - Encouraging tone
              - Friendly language
            
            - ❌ **Negative Sentiment**
              - Empathetic responses
              - Apologetic tone
              - Solution-focused approach
            
            - ➖ **Neutral Sentiment**
              - Professional responses
              - Helpful guidance
              - Clear information
            
            ### 📈 Evaluation Metrics
            
            - Sentiment detection accuracy: **90%+**
            - Response adaptation: Real-time
            - Customer satisfaction tracking
            - Conversation flow analysis
            """)
    
    gr.Markdown("""
    ---
    ### 💡 About This Chatbot
    
    This sentiment-aware chatbot demonstrates how AI can improve customer service by:
    1. **Understanding emotions** in customer messages
    2. **Adapting responses** based on detected sentiment
    3. **Tracking satisfaction** throughout the conversation
    4. **Providing insights** for service improvement
    
    **Model:** DistilBERT fine-tuned on SST-2 dataset
    **Framework:** Hugging Face Transformers + Gradio
    """)

# Launch the app
if __name__ == "__main__":
    demo.launch()