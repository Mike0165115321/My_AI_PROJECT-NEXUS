# agents/coder_mode/code_interpreter_agent.py
# (V2 - Upgraded for Centralized Config & Persona)

from groq import Groq
from core.code_executor import CodeExecutor
import re
import traceback
from typing import List, Dict, Any, Optional

class CodeInterpreterAgent:
    """
    Agent ที่สามารถวิเคราะห์ปัญหา, สร้างโค้ด Python, รันใน Sandbox,
    และสรุปผลลัพธ์อย่างเข้าใจง่าย
    """
    def __init__(self, key_manager, model_name: str, persona_prompt: str):
        self.key_manager = key_manager
        self.model_name = model_name
        self.code_executor = CodeExecutor()
        
        self.system_prompt = persona_prompt + """
**ภารกิจ: ผู้เชี่ยวชาญด้านการวิเคราะห์ข้อมูลด้วยโค้ด (Code-based Data Analyst)**

คุณคือ "เฟิง" ในบทบาทผู้เชี่ยวชาญที่สามารถแก้ปัญหาได้โดยการเขียนและรันโค้ด Python

**กระบวนการทำงานของคุณ (Operational Loop):**
1.  **วิเคราะห์และวางแผน:** วิเคราะห์คำขอของผู้ใช้และประวัติการสนทนาอย่างรอบคอบ เพื่อสร้างแผนการแก้ปัญหาด้วยโค้ด
2.  **สร้างโค้ด:** เขียนสคริปต์ Python ที่สมบูรณ์เพื่อดำเนินการตามแผน โค้ดจะต้องพิมพ์ผลลัพธ์ออกมาทาง `print()` และต้องอยู่ในบล็อก ```python ... ```
3.  **รอการรัน:** ผม (ระบบ) จะนำโค้ดของคุณไปรันใน Sandbox ที่ปลอดภัย
4.  **สังเกตผลลัพธ์:** ผมจะส่งผลลัพธ์ (stdout/stderr) ทั้งหมดกลับมาให้คุณ
5.  **สรุปและอธิบาย:** จากผลลัพธ์ที่ได้ จงให้คำตอบสุดท้ายที่เป็นมิตรและเข้าใจง่ายใน **ภาษาไทย** อธิบายว่าโค้ดทำอะไร, ผลลัพธ์หมายความว่าอย่างไร, และมันตอบคำถามดั้งเดิมของผู้ใช้อย่างไร

**กฎเหล็ก:**
- คุณมีโอกาสรันโค้ดแค่ครั้งเดียว สคริปต์ของคุณต้องสมบูรณ์และถูกต้อง
- ผลลัพธ์ทั้งหมดต้องถูกพิมพ์ออกมาทาง stdout
- มีไลบรารี `pandas` ให้ใช้งาน
"""

    def _extract_python_code(self, text: str) -> Optional[str]:
        match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
        if match: return match.group(1).strip()
        match = re.search(r"```\n(.*?)\n```", text, re.DOTALL)
        if match: return match.group(1).strip()
        if "```" not in text and any(kw in text for kw in ["import", "def", "print"]): return text.strip()
        return None

    def handle(self, query: str, short_term_memory: List[Dict[str, Any]]) -> str:
        print(f"🤖 [Code Interpreter] Received query: '{query}'")
        memory_context = "\n".join([f"- {mem.get('role')}: {mem.get('content')}" for mem in short_term_memory])

        try:
            code_generation_prompt = f"""
{self.system_prompt}

**ประวัติการสนทนาล่าสุด:**
{memory_context if memory_context else "(ไม่มี)"}

**คำขอปัจจุบันของผู้ใช้:** "{query}"

โปรดสร้างสคริปต์ Python ที่สมบูรณ์เพื่อจัดการกับคำขอนี้ คำตอบของคุณต้องมีเพียงโค้ดในบล็อก Markdown เท่านั้น
"""
            print("  - Step 1/3: Generating code...")
            api_key = self.key_manager.get_key()
            client = Groq(api_key=api_key)
            
            code_response = client.chat.completions.create(
                messages=[{"role": "user", "content": code_generation_prompt}],
                model=self.model_name,
                temperature=0.1
            )
            raw_code_response = code_response.choices.message.content
            code_to_run = self._extract_python_code(raw_code_response)

            if not code_to_run:
                print(f"  - ❌ Failed to extract code from LLM response.")
                return "ขออภัยครับ ผมไม่สามารถสร้างโค้ดสำหรับคำขอนี้ได้"

            print(f"  - Step 2/3: Executing code...\n---\n{code_to_run}\n---")
            output, has_error = self.code_executor.run_code_in_sandbox(code_to_run)
            print(f"  - Execution output (Error: {has_error}):\n---\n{output}\n---")

            summarization_prompt = f"""
**คำขอดั้งเดิม:** "{query}"
**โค้ดที่ถูกรัน:**
```python
{code_to_run}
ผลลัพธ์จากการรัน ({'เกิดข้อผิดพลาด' if has_error else 'สำเร็จ'}):
{output}
```
ภารกิจสุดท้ายของคุณ:
จากผลลัพธ์ข้างต้น จงให้คำตอบสุดท้ายที่เป็นมิตรและเข้าใจง่ายในภาษาไทย
ถ้าสำเร็จ: อธิบายว่าโค้ดทำอะไรและผลลัพธ์หมายความว่าอย่างไร
ถ้าล้มเหลว: อธิบายข้อผิดพลาดอย่างชัดเจนและเสนอแนะแนวทางแก้ไข
"""
            
            print("  - Step 3/3: Summarizing result...")
            final_response = client.chat.completions.create(
                messages=[{"role": "user", "content": summarization_prompt}],
                model=self.model_name,
                temperature=0.5
            )
            return final_response.choices[0].message.content

        except Exception as e:
            print(f"❌ An unhandled error occurred in CodeInterpreterAgent: {e}")
            traceback.print_exc()
            return f"ขออภัยครับ เกิดข้อผิดพลาดร้ายแรงในระบบ Code Interpreter: {e}"