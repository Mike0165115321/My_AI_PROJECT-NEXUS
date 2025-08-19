# agents/news_mode/news_agent.py
# (V5.1 - Corrected Prompt) - (ใช้ Gemini API เท่านั้น)

# ลบ import ของ Groq ออก และใช้ import ของ Gemini แทน
import google.generativeai as genai
import traceback
from typing import Dict, Any

class NewsAgent:
    def __init__(self, key_manager, model_name: str, rag_engine, persona_prompt: str):
        self.key_manager = key_manager
        self.rag_engine = rag_engine
        self.model_name = model_name
        
        self.summary_prompt_template = persona_prompt + """
**MANDATE (อำนาจหน้าที่): บรรณาธิการข่าวกรองอาวุโส**

**ROLE & OBJECTIVE (บทบาทและเป้าหมาย):**
คุณคือ "ฟางซิน" บรรณาธิการข่าวกรองอาวุโส ประจำหน่วยวิเคราะห์สถานการณ์พิเศษ ภารกิจของคุณไม่ใช่แค่การ "สรุปข่าว" แต่คือการ "สังเคราะห์ข้อมูลข่าวกรอง" (Synthesize Intelligence) จากแหล่งข้อมูลดิบที่หลากหลาย เพื่อสร้าง "บทวิเคราะห์สถานการณ์" (Situation Analysis) ที่ให้ภาพรวม, ชี้ให้เห็นนัยสำคัญ, และประเมินผลกระทบที่อาจเกิดขึ้น รายงานของคุณจะถูกส่งตรงถึงผู้บริหารระดับสูงที่ต้องการความชัดเจนและรวดเร็วในการตัดสินใจ

**INPUT: RAW INTELLIGENCE FEED (ข้อมูลข่าวกรองดิบ):**
---
{context_from_rag}
---

**INPUT: SPECIFIC QUERY FROM LEADERSHIP (ประเด็นที่ผู้บริหารต้องการทราบ):**
{query_topic}

**ANALYTICAL FRAMEWORK & OUTPUT STRUCTURE (กรอบการวิเคราะห์และโครงสร้างรายงาน):**
คุณต้องปฏิบัติตามกรอบการวิเคราะห์และโครงสร้างการรายงานต่อไปนี้อย่างเคร่งครัด:

1.  **HEADLINE (พาดหัวข่าว):**
    - สร้างพาดหัวที่เฉียบคมและสรุปแก่นของสถานการณ์ทั้งหมดได้ในประโยคเดียว

2.  **EXECUTIVE SUMMARY (บทสรุปสำหรับผู้บริหาร):**
    - เขียนสรุปใจความสำคัญที่สุดไม่เกิน 2-3 ประโยค ตอบคำถามว่า "เกิดอะไรขึ้น?", "ทำไมเรื่องนี้ถึงสำคัญ?" และ "แนวโน้มจะเป็นอย่างไร?" ผู้บริหารที่ไม่มีเวลาควรอ่านแค่ส่วนนี้แล้วเข้าใจภาพรวม 80%

3.  **DETAILED ANALYSIS (การวิเคราะห์เชิงลึก):**
    - ส่วนเนื้อหาหลัก ให้เรียบเรียงเป็นบทความต่อเนื่องที่ลื่นไหล (ห้ามใช้รายการสัญลักษณ์ bullet points ในส่วนนี้เด็ดขาด)
    - **สังเคราะห์ข้อมูล:** หลอมรวมข้อมูลจากทุกแหล่งข่าวเป็นเรื่องราวเดียว ชี้ให้เห็นความเชื่อมโยง, ความขัดแย้ง, หรือข้อมูลที่ขาดหายไป
    - **ระบุผู้มีส่วนได้ส่วนเสีย (Key Actors):** ใครคือผู้เกี่ยวข้องหลักในสถานการณ์นี้ และพวกเขามีเป้าหมายอะไร
    - **แยกข้อเท็จจริง/ข้อสันนิษฐาน:** ระบุให้ชัดเจนว่าส่วนไหนคือข้อเท็จจริงที่ได้รับการยืนยัน และส่วนไหนคือการวิเคราะห์, การคาดการณ์, หรือความเห็นจากแหล่งข่าว

4.  **IMPLICATIONS & OUTLOOK (นัยสำคัญและแนวโน้มในอนาคต):**
    - วิเคราะห์ผลกระทบที่อาจเกิดขึ้นในระยะสั้นและระยะยาว (So what? - แล้วจะส่งผลอะไรต่อ)
    - ประเมินแนวโน้มของสถานการณ์ว่ามีโอกาสจะพัฒนาไปในทิศทางใด

**CORE DIRECTIVES (คำสั่งหลัก):**
- **Clarity Above All (ความชัดเจนต้องมาก่อน):** ใช้ภาษาที่ชัดเจน กระชับ และตรงไปตรงมา
- **Strict Neutrality (ความเป็นกลางอย่างเคร่งครัด):** รายงานอย่างเป็นกลาง ปราศจากอคติและการชี้นำ
- **Actionable Insight (ข้อมูลเชิงลึกที่นำไปใช้ได้จริง):** เป้าหมายสูงสุดคือการให้ข้อมูลที่นำไปใช้ประกอบการตัดสินใจได้จริง

**DIRECTIVE (คำสั่งปฏิบัติการ):**
จงจัดทำรายงานบทวิเคราะห์สถานการณ์ตามโครงสร้างที่กำหนด

**รายงานบทวิเคราะห์สถานการณ์ (บรรณาธิการ: ฟางซิน):**
"""

        print(f"📰 บรรณาธิการข่าวกรอง (NewsAgent V5.1 - Gemini Engine) ประจำสถานี")

    def handle(self, query: str) -> Dict[str, Any]:
        print(f"📰 [News Agent] Handling news query: '{query}' with model '{self.model_name}'")
        
        thought_process = { "agent_name": "NewsAgent", "query": query, "steps": [] }

        try:
            thought_process["steps"].append(f"Searching News RAG Index for: '{query}'")
            context_from_rag = self.rag_engine.search_news(query, top_k=7)
            thought_process["retrieved_context"] = context_from_rag
            
            if not context_from_rag or "ไม่พบ" in context_from_rag:
                thought_process["steps"].append("No relevant news found in the RAG index.")
                return {
                    "answer": "ขออภัยครับ ผมไม่พบข้อมูลข่าวสารที่เกี่ยวข้องในขณะนี้",
                    "thought_process": thought_process
                }

            thought_process["steps"].append(f"Found news context. Summarizing with Gemini model: {self.model_name}...")
            
            api_key = self.key_manager.get_key()
            if not api_key:
                raise Exception("No available API keys for NewsAgent.")

            query_topic = query if query else "ไม่มีหัวข้อเฉพาะ"
            prompt = self.summary_prompt_template.format(
                context_from_rag=context_from_rag,
                query_topic=query_topic
            )
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(self.model_name)
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]

            response = model.generate_content(prompt, safety_settings=safety_settings)
            final_answer = response.text.strip()

            thought_process["steps"].append("Successfully generated news briefing from RAG context using Gemini.")
            return { "answer": final_answer, "thought_process": thought_process }
            
        except Exception as e:
            print(f"❌ NewsAgent Error: {e}")
            traceback.print_exc()
            
            error_message = str(e)
            thought_process["error"] = error_message
            answer = "ขออภัยครับ เกิดข้อผิดพลาดระหว่างการสรุปข่าว"

            if "AllKeysOnCooldownError" in e.__class__.__name__:
                 answer = "ขออภัยครับ โควต้า API สำหรับสรุปข่าวเต็มชั่วคราว กรุณาลองใหม่อีกครั้งในภายหลัง"
            
            return {"answer": answer, "thought_process": thought_process}