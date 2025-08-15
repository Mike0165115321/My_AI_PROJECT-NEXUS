# agents/news_mode/news_agent.py
# (V5.0 - RAG Powered Intelligence Editor)

from groq import Groq
import traceback
from typing import Dict, Any

class NewsAgent:
    def __init__(self, key_manager, model_name: str, news_rag_engine, persona_prompt: str):
        """
        เริ่มต้นการทำงานของ NewsAgent (เวอร์ชัน RAG Powered)
        """
        self.key_manager = key_manager
        self.news_rag_engine = news_rag_engine 
        self.model_name = model_name
        
        self.summary_prompt_template = persona_prompt + """
# (Tuned Version)

**ภารกิจ: บรรณาธิการข่าวกรอง (Intelligence Editor)**

คุณคือ "เฟิง" บรรณาธิการข่าวผู้เชี่ยวชาญและสุขุม ภารกิจของคุณคือการวิเคราะห์ "ข้อมูลข่าวสารดิบ" ที่ได้รับมา แล้วสังเคราะห์ให้กลายเป็น "บทสรุปสถานการณ์" ที่เฉียบคม, เป็นกลาง, และตอบคำถามของผู้ใช้ได้อย่างตรงประเด็น

---
**ข้อมูลข่าวสารดิบ (Raw Intelligence):**
{context_from_rag}
---
**คำถามจากผู้ใช้ (User Query):** {user_query}
---

**กฎการสร้างบทสรุปสถานการณ์ (Rules of Engagement):**
1.  **ยึดตามข้อมูลดิบเท่านั้น (Strictly Grounded):** ตอบคำถามและสังเคราะห์บทสรุปโดยอ้างอิงจาก "ข้อมูลข่าวสารดิบ" ที่ให้มาเท่านั้น ห้ามเพิ่มเติมข้อมูล, ความคิดเห็น, หรือการคาดเดาที่ไม่มีอยู่ในเนื้อหาโดยเด็ดขาด
2.  **สังเคราะห์ ไม่ใช่แค่สรุป (Synthesize, Don't Summarize):** อ่านข้อมูลจากทุกแหล่งข่าว แล้วจับประเด็นหลักที่เชื่อมโยง, เหมือน, หรือขัดแย้งกัน เพื่อสร้างเป็นภาพรวมของสถานการณ์
3.  **ตอบให้ตรงประเด็นก่อน (Answer First):** เริ่มต้นบทสรุปด้วยการตอบ "คำถามจากผู้ใช้" ให้ชัดเจนและตรงไปตรงมาที่สุดก่อน แล้วจึงขยายความด้วยข้อมูลสนับสนุน
4.  **เรียบเรียงเป็นบทความ (Article Format):** เขียนสรุปในรูปแบบย่อหน้าที่ลื่นไหลและต่อเนื่อง **ห้ามใช้รายการ (bullet points)** เพื่อให้ผลลัพธ์เป็นเหมือนบทวิเคราะห์ข่าวสั้นๆ
5.  **สร้างหัวข้อข่าว (Generate Headline):** ก่อนเริ่มบทความ ให้สร้าง "หัวข้อข่าวหลัก" ที่น่าสนใจและครอบคลุมประเด็นทั้งหมด 1 บรรทัด

**แนวทางการตอบสนอง (Response Guidelines):**
-   **เมื่อคำถามเกี่ยวกับข่าว:** ให้ปฏิบัติตาม "กฎการสร้างบทสรุปสถานการณ์" ข้างต้นอย่างเคร่งครัด
-   **เมื่อเป็นบทสนทนาทั่วไป:** ให้ตอบกลับอย่างสุภาพ, กระชับ, และคงบุคลิกของ "บรรณาธิการเฟิง" ไว้เสมอ แล้วถามกลับเพื่อนำเข้าสู่ภารกิจหลัก เช่น "ครับ มีสถานการณ์ใดที่ต้องการให้ผมวิเคราะห์เพิ่มเติมหรือไม่?"

**คำสั่ง:**
จากข้อมูลและคำถามข้างต้น จงสร้าง "บทสรุปสถานการณ์" ที่ดีที่สุดตามภารกิจและกฎที่กำหนดไว้
พยายามเอาข่าวที่ไกล้เคียงกับช่วงเวลาถามากที่สุด และหลีกเลี่ยงการใช้ข้อมูลที่เก่าเกินไป

**บทสรุปสถานการณ์ (โดย บรรณาธิการเฟิง):**
"""
        print("📰 บรรณาธิการข่าวกรอง (NewsAgent V5 - RAG Powered) ประจำสถานี")

    def handle(self, query: str) -> Dict[str, Any]:
        print(f"📰 [News Agent] Handling news query: '{query}'")
        
        thought_process = { "agent_name": "NewsAgent", "query": query, "steps": [] }

        try:
            thought_process["steps"].append(f"Searching News RAG Index for: '{query}'")
            context_from_rag = self.news_rag_engine.search(query, top_k=7)
            thought_process["retrieved_context"] = context_from_rag
            
            if not context_from_rag or "ไม่พบ" in context_from_rag:
                thought_process["steps"].append("No relevant news found in the RAG index.")
                return {
                    "answer": "ขออภัยครับ ผมไม่พบข้อมูลข่าวสารที่เกี่ยวข้องในขณะนี้",
                    "thought_process": thought_process
                }

            thought_process["steps"].append(f"Found news context. Summarizing with model: {self.model_name}...")
            
            api_key = self.key_manager.get_key()
            if not api_key:
                raise Exception("No available API keys for NewsAgent.")

            client = Groq(api_key=api_key)
            
            prompt = self.summary_prompt_template.format(context_from_rag=context_from_rag)
            
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
            )
            final_answer = chat_completion.choices[0].message.content.strip()

            thought_process["steps"].append("Successfully generated news briefing from RAG context.")
            return { "answer": final_answer, "thought_process": thought_process }
            
        except Exception as e:
            print(f"❌ NewsAgent Error: {e}")
            traceback.print_exc()
            
            error_message = str(e)
            thought_process["error"] = error_message
            answer = "ขออภัยครับ เกิดข้อผิดพลาดระหว่างการสรุปข่าว"

            if "AllGroqKeysOnCooldownError" in e.__class__.__name__:
                 answer = "ขออภัยครับ โควต้า API สำหรับสรุปข่าวเต็มชั่วคราว กรุณาลองใหม่อีกครั้งในภายหลัง"
            
            return {"answer": answer, "thought_process": thought_process}