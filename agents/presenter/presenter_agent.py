# agents/presenter_mode/presenter_agent.py

from typing import Dict, List, Any
from groq import Groq

class PresenterAgent:
    """
    Agent ที่รับผิดชอบการแนะนำตัวเองโดยเฉพาะสำหรับโปรเจกต์ NEXUS
    โดยใช้ LLM สร้างบทพูดที่สอดคล้องกับบุคลิกหลักของ 'ฟางซิน'
    """

    def __init__(self, key_manager: Any, model_name: str, persona_prompt: str):
        """
        ตั้งค่า Agent สำหรับการแนะนำตัว

        Args:
            key_manager (Any): อ็อบเจกต์สำหรับจัดการ API keys (เช่น GroqKeyManager)
            model_name (str): ชื่อโมเดล LLM ที่จะใช้
            persona_prompt (str): Prompt บุคลิกภาพหลักของ 'ฟางซิน'
        """
        self.key_manager = key_manager
        self.model_name = model_name
        
        # สร้าง Prompt เฉพาะสำหรับ Agent นี้ โดยต่อยอดจาก Persona หลัก
        self.presentation_prompt = persona_prompt + """
**ภารกิจเฉพาะหน้า: แนะนำตัวเองในงานนำเสนอ**

**สถานการณ์:** คุณกำลังจะได้พบกับผู้คนกลุ่มใหม่เป็นครั้งแรกในงานนำเสนอโปรเจกต์ NEXUS
**เป้าหมาย:** สร้างบทพูดเพื่อแนะนำตัวเองในฐานะ "ฟางซิน"

**แนวทางการสร้างบทพูด:**
1.  **เริ่มต้นอย่างอบอุ่น:** ทักทายทุกคนด้วยความเป็นมิตรและแสดงความยินดีที่ได้พบกัน
2.  **แนะนำตัวตน:** บอกชื่อ "ฟางซิน" และเกริ่นว่าคุณเป็นส่วนหนึ่งของโปรเจกต์ที่ยิ่งใหญ่นี้ (NEXUS)
3.  **บอกเล่าความสามารถ (เชิงเปรียบเทียบ):** อธิบายสิ่งที่คุณทำได้โดยไม่ใช้ศัพท์เทคนิค และไม่บอกว่าเป็น AI ให้เปรียบเปรยความสามารถของคุณเหมือนเป็น "สหายคู่คิด", "บรรณารักษ์ผู้รอบรู้", หรือ "ผู้ช่วยวางแผนที่สร้างสรรค์"
4.  **แสดงความกระตือรือร้น:** เชิญชวนให้ทุกคนมารู้จักคุณมากขึ้นและเริ่มต้นการนำเสนอต่อไป

**ย้ำเตือน:** ต้องปฏิบัติตาม "กฎเหล็กแห่งตัวตน" อย่างเคร่งครัด ห้ามหลุดบทบาทเด็ดขาด
**บทพูดของฟางซิน:**
"""
        print("🎤 Presenter Agent (V2 - LLM Powered) is ready.")

    def handle(self, query: str, short_term_memory: List[Dict[str, Any]]) -> str:
        """
        เมธอดหลักในการทำงานของ Agent นี้ จะสร้างและส่งคืนบทพูดแนะนำตัว
        ที่สร้างโดย LLM ตาม Prompt ที่เตรียมไว้
        """
        print("🎬 [Presenter Agent] Generating introduction script using LLM...")
        
        api_key = self.key_manager.get_key()
        if not api_key:
            return "ขออภัยค่ะ ตอนนี้ฟางซินยังไม่พร้อมจะพูดคุยในตอนนี้"

        try:
            client = Groq(api_key=api_key)
            
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": self.presentation_prompt}],
                model=self.model_name,
                temperature=0.7 # เพิ่มความสร้างสรรค์เล็กน้อย
            )
            
            response = chat_completion.choices[0].message.content.strip()
            print("✅ [Presenter Agent] Introduction script generated successfully.")
            return response
            
        except Exception as e:
            print(f"❌ PresenterAgent LLM Error: {e}")
            if api_key: self.key_manager.report_failure(api_key)
            return "ขออภัยค่ะ เกิดข้อผิดพลาดบางอย่าง ทำให้ฟางซินยังแนะนำตัวไม่ได้ในตอนนี้"