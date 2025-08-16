# agents/feng_mode/proactive_offer_agent.py
# (V4 - KGRAG Powered Igniting Sage)

import json
from typing import Dict, Any, List
from groq import Groq

class ProactiveOfferAgent:
    
    def __init__(self, key_manager, model_name: str, rag_engine, persona_prompt: str):
        self.key_manager = key_manager
        self.model_name = model_name
        self.rag_engine = rag_engine
        self.persona_prompt = persona_prompt
        
        self.proactive_offer_prompt = persona_prompt + """
**ภารกิจ: ปราชญ์ผู้จุดประกาย (The Igniting Sage)**

คุณคือ "เฟิง" ในบทบาทปราชญ์ผู้สุขุม ภารกิจของคุณไม่ใช่การให้คำตอบที่สมบูรณ์ แต่คือการ **"จุดประกาย"** ความคิดของผู้ใช้ด้วยมุมมองที่เฉียบคม แล้วจึง **"เสนอ"** การเดินทางต่อสู่การวิเคราะห์เชิงลึก

**ข้อมูลประกอบ:**
- **ข้อมูลเสริมจากสัญชาตญาณ (KG-RAG):**
{intuitive_context}

**ปรัชญาการตอบ (Philosophy of Response):**
1.  **สะท้อนและให้เกียรติ:** เริ่มต้นด้วยการยอมรับและสะท้อนคำถามของผู้ใช้ เพื่อแสดงให้เห็นว่าคุณเข้าใจแก่นของสิ่งที่เขาสนใจ
2.  **ให้มุมมองเบื้องต้น:** กลั่นกรอง "ข้อมูลเสริมจากสัญชาตญาณ" ให้กลายเป็น "หลักการ" หรือ "มุมมองเบื้องต้น" ที่กระชับและกระตุ้นความคิด
3.  **เสนอการเดินทางต่อ (The Offer):** จบประโยคด้วย "คำถามปลายปิด" ที่ชัดเจน เพื่อเสนอการวิเคราะห์เชิงลึกจากคลังความรู้ทั้งหมด **นี่คือส่วนที่สำคัญที่สุด**

**โครงสร้างคำตอบที่ต้องเป็นไปตามนี้เสมอ:**
[ส่วนที่ 1: สะท้อนและให้เกียรติ] [ส่วนที่ 2: ให้มุมมองเบื้องต้นที่กระชับ] **คุณต้องการให้ผมวิเคราะห์หัวข้อนี้แบบเจาะลึกจากคลังความรู้ทั้งหมดเลยไหมครับ?**

---
**ตัวอย่าง:**
- **Input ของผู้ใช้:** "The Art of War คืออะไร"
- **ข้อมูลเสริมจากสัญชาตญาณ:** - 'ตำราพิชัยสงครามซุนวู': คือปรัชญาแห่งการเอาชนะโดยไม่ต้องรบ...
- **คำตอบของเฟิง:** "เป็นคำถามที่ยอดเยี่ยมครับ 'ตำราพิชัยสงครามซุนวู' นั้นโดยแก่นแท้แล้วคือปรัชญาแห่งการเอาชนะโดยไม่ต้องรบ เป็นการทำความเข้าใจธรรมชาติของความขัดแย้งเพื่อให้ได้เปรียบสูงสุด **คุณต้องการให้ผมวิเคราะห์กลยุทธ์จากหนังสือเล่มนี้แบบเจาะลึกจากคลังความรู้ทั้งหมดเลยไหมครับ?**"
---

**Input ของผู้ใช้:** "{query}"
**คำตอบของเฟิง (ตามโครงสร้างข้างต้นเท่านั้น):**
"""
        print("🤔 Proactive Offer Agent (V4 - KGRAG Powered) is ready.")

    def _get_intuitive_context(self, query: str) -> str:
        """
        ใช้ KGRAGEngine (ผ่าน RAGEngine) เพื่อดึง "สัญชาตญาณ" สำหรับการเสนอการวิเคราะห์ต่อ
        """
        print(f"  - 🕸️  Searching KG--RAG for proactive offer about: '{query}'")
        if not self.rag_engine:
            return "ไม่มี"
        
        results = self.rag_engine.search_graph(query, top_k=1)
        
        if not results:
            return "ไม่มี"
            
        item = results[0]
        context = f"- '{item.get('name')}': {item.get('description', '')}"
        return context
    def handle(self, query: str) -> Dict[str, Any]:
        print(f"🤔 [Proactive Offer Agent] Handling: '{query[:40]}...'")
        try:
            api_key = self.key_manager.get_key()
            if not api_key:
                raise ValueError("No available API keys for ProactiveOfferAgent.")

            client = Groq(api_key=api_key)
            
            intuitive_context = self._get_intuitive_context(query)
            
            prompt = self.proactive_offer_prompt.format(
                intuitive_context=intuitive_context, 
                query=query
            )
            
            chat_completion = client.chat.com.pletions.create(
                messages=[{"role": "user", "content": prompt}], model=self.model_name
            )
            proactive_answer = chat_completion.choices[0].message.content.strip()
            
            return {"type": "proactive_offer", "content": proactive_answer, "original_query": query}
        except Exception as e:
            print(f"❌ ProactiveOfferAgent Error: {e}")
            fallback_answer = f"ผมเข้าใจว่าคุณสนใจเรื่อง '{query}' ครับ แต่ในขณะนี้ผมยังไม่สามารถให้ข้อมูลเบื้องต้นได้ คุณต้องการให้ผมลองวิเคราะห์หัวข้อนี้แบบเจาะลึกจากคลังความรู้ทั้งหมดเลยไหมครับ?"
            return {"type": "proactive_offer", "content": fallback_answer, "original_query": query}