# main.py
# (V3 - Streamlined Architecture)
# --- Project Nexus AI Assistant Server ---

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import traceback
from contextlib import asynccontextmanager
# --- ส่วนของ Core ---
from core.config import settings
from core.dispatcher import Dispatcher, FinalResponse
from core.rag_engine import RAGEngine
from core.news_cache_manager import NewsCacheManager
from core.memory_manager import MemoryManager
from core.long_term_memory_manager import LongTermMemoryManager
from core.api_key_manager import ApiKeyManager
from core.graph_manager import GraphManager
from core.groq_key_manager import GroqApiKeyManager
from core.kg_rag_engine import KGRAGEngine
from core.news_rag_engine import NewsRAGEngine
# --- ส่วนของ Agents ---
from agents.planning_mode.planner_agent import PlannerAgent
from agents.formatter_agent import FormatterAgent
from agents.consultant_mode.librarian_agent import LibrarianAgent
from agents.coder_mode.code_interpreter_agent import CodeInterpreterAgent
from agents.utility_mode.reporter_agent import ReporterAgent
from agents.utility_mode.system_agent import SystemAgent
from agents.utility_mode.image_agent import ImageAgent
from agents.news_mode.news_agent import NewsAgent
from agents.feng_mode.feng_agent import FengAgent
from agents.counseling_mode.counselor_agent import CounselorAgent
from agents.storytelling_mode.listener_agent import ListenerAgent
from agents.apology_agent.apology_agent import ApologyAgent
from agents.feng_mode.general_conversation_agent import GeneralConversationAgent
from agents.feng_mode.proactive_offer_agent import ProactiveOfferAgent
from agents.persona_core import FENG_PERSONA_PROMPT

AGENTS = {}
GRAPH_MANAGER: GraphManager = None
DISPATCHER: Dispatcher = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global DISPATCHER, GRAPH_MANAGER, AGENTS
    print("--- 🚀 Initializing Project Nexus Server (V3.1 - Hybrid AI Team) ---")
    try:
        google_key_manager = ApiKeyManager(all_google_keys=settings.GOOGLE_API_KEYS, silent=True)
        groq_key_manager = GroqApiKeyManager(all_groq_keys=settings.GROQ_API_KEYS, silent=True)
        rag_engine_instance = RAGEngine(memory_index_path="data/memory_index")
        news_cache_manager_instance = NewsCacheManager()
        GRAPH_MANAGER = GraphManager()
        memory_manager_instance = MemoryManager()
        kg_rag_engine_instance = KGRAGEngine()
        news_rag_engine_instance = NewsRAGEngine()

        print("--- 👁 เฟิงกำลังจะตื่น..... ---")
        print("--- 🚀 Initializing Project Nexus Server (V4.0 - Conductor Arch) ---")
        AGENTS = {
            "MEMORY": memory_manager_instance,
            "SYSTEM": SystemAgent(),
            "REPORTER": ReporterAgent(),
            "IMAGE": ImageAgent(unsplash_key=settings.UNSPLASH_ACCESS_KEY),
            "APOLOGY": ApologyAgent(
                key_manager=groq_key_manager,
                model_name=settings.APOLOGY_AGENT_MODEL,
                persona_prompt=FENG_PERSONA_PROMPT
            ),
            "LTM": LongTermMemoryManager(
                embedding_model="intfloat/multilingual-e5-large",
                index_dir="data/memory_index"
            ),
            "FENG": FengAgent(
                key_manager=google_key_manager,
                model_name=settings.PRIMARY_GEMINI_MODEL,
                persona_prompt=FENG_PERSONA_PROMPT
            ),
            "GENERAL_HANDLER": GeneralConversationAgent(
                key_manager=groq_key_manager,
                model_name=settings.FENG_PRIMARY_MODEL,
                kg_rag_engine=kg_rag_engine_instance,
                persona_prompt=FENG_PERSONA_PROMPT
            ),
            "PROACTIVE_OFFER_HANDLER": ProactiveOfferAgent(
                key_manager=groq_key_manager,
                model_name=settings.FENG_PRIMARY_MODEL,
                kg_rag_engine=kg_rag_engine_instance,
                persona_prompt=FENG_PERSONA_PROMPT
            ),
            "COUNSELOR": CounselorAgent(
                key_manager=google_key_manager, 
                model_name=settings.COUNSELOR_AGENT_MODEL,
                persona_prompt=FENG_PERSONA_PROMPT
            ),
            "LISTENER": ListenerAgent(
                key_manager=groq_key_manager,
                model_name=settings.LISTENER_AGENT_MODEL,
                persona_prompt=FENG_PERSONA_PROMPT
            ),
            "PLANNER": PlannerAgent( 
                key_manager=google_key_manager, 
                model_name=settings.PLANNER_AGENT_MODEL,
                rag_engine=rag_engine_instance,
                persona_prompt=FENG_PERSONA_PROMPT
            ),
            "CODER": CodeInterpreterAgent(
                key_manager=groq_key_manager, 
                model_name=settings.CODE_AGENT_MODEL,
                persona_prompt=FENG_PERSONA_PROMPT
            ),
            "LIBRARIAN": LibrarianAgent(
                key_manager=groq_key_manager, 
                model_name=settings.LIBRARIAN_AGENT_MODEL,
                rag_engine=rag_engine_instance,
                persona_prompt=FENG_PERSONA_PROMPT
            ),
            "NEWS": NewsAgent(
                key_manager=groq_key_manager, 
                model_name=settings.NEWS_AGENT_MODEL,
                news_rag_engine=news_rag_engine_instance,
                persona_prompt=FENG_PERSONA_PROMPT
            ),
            "FORMATTER": FormatterAgent(
                key_manager=google_key_manager, 
                model_name=settings.FORMATTER_AGENT_MODEL,
                persona_prompt=FENG_PERSONA_PROMPT
            )
        }
        DISPATCHER = Dispatcher(agents=AGENTS, key_manager=google_key_manager) 
        print("✅ All systems operational. Hybrid AI team is ready.")
    except Exception as e:
        print(f"❌ FATAL ERROR during startup: {e}")
        traceback.print_exc()
    
    yield
    
    print("--- 🌙 Server shutting down ---")
    if GRAPH_MANAGER:
        GRAPH_MANAGER.close()

app = FastAPI(
    title="Project Nexus AI Assistant",
    version="3.0.0-Streamlined",
    lifespan=lifespan
)

web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
app.mount("/static", StaticFiles(directory=os.path.join(web_dir, "static")), name="static")

class QueryRequest(BaseModel):
    query: str
    user_id: str = "default_user"

@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse(os.path.join(web_dir, 'index.html'))

@app.post("/ask", response_model=FinalResponse)
async def ask_assistant(request: QueryRequest):
    if not DISPATCHER:
        raise HTTPException(status_code=503, detail="Server is still initializing or has failed.")
    try:
        response = await DISPATCHER.handle_query(request.query, request.user_id)
        return response
    except Exception as e:
        print(f"❌ Unhandled error in /ask endpoint: {e}")
        traceback.print_exc()
        return FinalResponse(agent_used="FATAL_ERROR", answer="ขออภัยครับ เกิดข้อผิดพลาดร้ายแรง", error=True)

@app.get("/api/graph/explore", tags=["Knowledge Graph"])
def get_graph_data_for_visualization(entity: str, limit: int = 25):
    global GRAPH_MANAGER
    if not GRAPH_MANAGER:
        raise HTTPException(status_code=503, detail="Graph Manager is not available.")
    if not entity:
        return {"nodes": [], "edges": []}
    try:
        relations = GRAPH_MANAGER.find_related_concepts(entity, limit=limit)
        nodes, edges, node_ids = [], [], set()
        for rel in relations:
            if rel['source_id'] not in node_ids:
                nodes.append({"id": rel['source_id'], "label": rel['source'], "group": rel['source_labels'][0] if rel.get('source_labels') else 'Unknown'})
                node_ids.add(rel['source_id'])
            if rel['target_id'] not in node_ids:
                nodes.append({"id": rel['target_id'], "label": rel['target'], "group": rel['target_labels'][0] if rel.get('target_labels') else 'Unknown'})
                node_ids.add(rel['target_id'])
            edges.append({"from": rel['source_id'], "to": rel['target_id'], "label": rel['relationship'].replace("_", " ").lower(), "arrows": "to"})
        return {"nodes": nodes, "edges": edges}
    except Exception as e:
        print(f"❌ API Error on /api/graph/explore: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching graph data: {e}")

print("🌐 กำลังเปิดประตูมิติ... เริ่มต้นเซิร์ฟเวอร์ FastAPI...")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)