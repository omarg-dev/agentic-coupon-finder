import os
import asyncio
# from browser_use.llm.google import ChatGoogle
from browser_use.llm import ChatGroq
from browser_use.llm.groq import chat as groq_chat

# Patch: Enable tool calling for Llama 3.3
if "llama-3.3-70b-versatile" not in groq_chat.ToolCallingModels:
    groq_chat.ToolCallingModels.append("llama-3.3-70b-versatile")

class CustomChatGroq(ChatGroq):
    async def _invoke_with_tool_calling(self, groq_messages, output_format, schema):
        response = await super()._invoke_with_tool_calling(groq_messages, output_format, schema)
        choice = response.choices[0]
        message = choice.message
        # Fix: Extract tool call arguments into content if content is empty (Groq standard behavior)
        if not message.content and message.tool_calls:
            message.content = message.tool_calls[0].function.arguments
        return response

from browser_use import Agent, Controller
from src.data.database import SessionLocal
from src.data.models import Coupon, Website, TestLog

# Initialize LLM 
llm = CustomChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.0
)
# llm = ChatGoogle(
#     model="gemini-2.5-flash-lite",
#     api_key=os.getenv("GEMINI_API_KEY"),
#     temperature=0.0
# )


class CouponValidator:
    def __init__(self):
        self.controller = Controller()

    async def validate_domain(self, domain: str):
        print(f"🤖 Agent: Starting validation for {domain}...")
        
        # fetch coupons from DB
        session = SessionLocal()
        website = session.query(Website).filter_by(domain=domain).first()
        
        if not website or not website.coupons:
            print("❌ No coupons found in Vault to test.")
            session.close()
            return
            
        coupons_to_test = [c.code for c in website.coupons]
        print(f"📋 Testing codes: {coupons_to_test}")

        # Define the Mission
        # We give the LLM a clear, step-by-step "Job Description"
        task = f"""
        Go to https://{domain}.
        Your goal is to test if these coupon codes work: {coupons_to_test}.
        
        STEPS:
        1. Add any cheap item to the shopping cart. (Ignore pre-orders).
        2. Go to the Checkout or Cart page.
        3. Look for a "Promo Code", "Discount", or "Coupon" input field.
            - If you CANNOT find the input field (or if it requires login), STOP and report 'NO_INPUT_FIELD'.
            - If you find it, try the codes one by one.
            - If you don't find any valid items, check the menu or categories for sale items.
        4. For each code:
            a. Enter the code into the input field.
            b. Apply the code.
            c. Observe if the total price changes or if a success message appears.
        5. Record which codes worked and which didn't.
        6. If none of the codes work, report 'NO_CODES_WORKED'.
        """

        # initialize Agent
        agent = Agent(
            task=task,
            llm=llm,
            controller=self.controller,
            use_vision=False, # change depending on model capabilities
            max_steps=20       # safety limit: don't click forever
        )

        try:
            # run the browser (headless=False so you can watch it work locally)
            history = await agent.run()
            
            # analyze Result (Simplified)
            # In a real app, we'd parse 'history' deeply. For now, we trust the final output.
            result_summary = history.final_result() 
            print(f"✅ Agent Finished. Summary: {result_summary}")
            
            # log success
            self._log_result(session, website.id, "SUCCESS", str(result_summary))
            
            # (optional) here you would update the 'is_working' column in DB 
            # based on the agent's findings.
            
        except Exception as e:
            print(f"🔥 Agent Crashed: {e}")
            self._log_result(session, website.id, "FAILED", str(e))
        
        finally:
            session.close()

    def _log_result(self, session, website_id, status, msg):
        log = TestLog(
            website_id=website_id,
            status=status,
            message=msg[:500] # truncate long messages
        )
        session.add(log)
        session.commit()
        print(f"📝 Logged result: {status}")

# wrapper to run async code synchronously (for easy testing)
def run_validator(domain):
    validator = CouponValidator()
    asyncio.run(validator.validate_domain(domain))