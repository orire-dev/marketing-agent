"""
FastAPI main application for Marketing Agent
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import ValidationError

from app.schemas import GenerateRequest, GenerateResponse, RequestMeta, Constraints, RetrievedSource
from app.llm_client import LLMClient
from app.rag import RAGRetriever
from app.planner import Planner
from app.generator import CopyGenerator
from app.compliance import ComplianceChecker
from app.prompt_builder import PromptBuilder
from app.ranker import Ranker
from app.renderers.stub import StubRenderer
from app.renderers.openai_renderer import OpenAIRenderer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="eToro Marketing Agent API",
    description="AI-powered marketing creative generation",
    version="0.1.0"
)

# Serve static files (UI)
import os
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
llm_client = LLMClient()
retriever = RAGRetriever()
planner = Planner(llm_client, retriever)
generator = CopyGenerator(llm_client)
compliance_checker = ComplianceChecker(llm_client)
prompt_builder = PromptBuilder(llm_client)
ranker = Ranker()

# Initialize renderer (try OpenAI, fallback to stub)
try:
    renderer = OpenAIRenderer()
    logger.info("Using OpenAI DALL-E renderer")
except Exception as e:
    logger.warning(f"OpenAI renderer not available, using stub: {e}")
    renderer = StubRenderer()


@app.get("/")
async def root():
    """Serve the UI"""
    ui_path = os.path.join(static_dir, "index.html")
    if os.path.exists(ui_path):
        return FileResponse(ui_path)
    return {
        "service": "eToro Marketing Agent",
        "status": "running",
        "version": "0.1.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "service": "eToro Marketing Agent",
        "status": "running",
        "version": "0.1.0"
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate_creative(request: GenerateRequest) -> GenerateResponse:
    """
    Generate marketing creative options.
    
    This is the main endpoint that orchestrates the entire generation pipeline.
    """
    try:
        logger.info(f"Received generation request: {request.model_dump()}")
        
        request_dict = request.model_dump()
        generation_id = str(uuid.uuid4())
        
        # Step 1: Create plan
        logger.info("Step 1: Planning...")
        plan = planner.create_plan(request_dict)
        
        # Step 2: Retrieve relevant chunks
        logger.info("Step 2: Retrieving relevant content...")
        query = f"{request.product_scope} {request.campaign_goal or ''} {request.style_guidance or ''}"
        chunks = retriever.retrieve_all(
            query=query,
            product_scope=request.product_scope,
            segment_id=request.segment_id
        )
        
        # Step 3: Generate creative options
        logger.info("Step 3: Generating creative options...")
        options = generator.generate_options(
            request_dict,
            plan,
            chunks,
            num_options=request.num_options
        )
        
        # Step 4: Build prompts for each option
        logger.info("Step 4: Building image/motion prompts...")
        for option in options:
            prompts = prompt_builder.build_prompts(
                option,
                request.asset,
                request.languages,
                request.style_guidance or "standard"
            )
            option.prompts = prompts
        
        # Step 4.5: Generate actual images
        logger.info("Step 4.5: Generating images...")
        # Create renderer with dynamic API key if provided
        image_renderer = renderer
        if request.openai_api_key:
            # Use provided API key
            from app.renderers.openai_renderer import OpenAIRenderer
            image_renderer = OpenAIRenderer(api_key=request.openai_api_key)
            logger.info("Using OpenAI API key from request")
        elif isinstance(renderer, StubRenderer):
            # Try to use env var if available
            import os
            env_key = os.getenv("OPENAI_API_KEY")
            if env_key:
                from app.renderers.openai_renderer import OpenAIRenderer
                image_renderer = OpenAIRenderer(api_key=env_key)
                logger.info("Using OpenAI API key from environment")
        
        for option in options:
            for asset_format, lang_prompts in option.prompts.items():
                for lang, asset_prompt in lang_prompts.items():
                    try:
                        logger.info(f"Generating image for {asset_format}/{lang}...")
                        image_uri = image_renderer.render_image(
                            prompt=asset_prompt.image_prompt,
                            negative_prompt=asset_prompt.negative_prompt,
                            aspect_ratio=asset_prompt.aspect_ratio,
                            seed=asset_prompt.seed
                        )
                        asset_prompt.generated_image_uri = image_uri
                        asset_prompt.generation_status = "completed"
                        logger.info(f"✅ Generated image for {asset_format}/{lang}: {image_uri[:80]}...")
                    except ValueError as e:
                        # User-friendly error (billing, auth, etc.)
                        logger.error(f"❌ Image generation failed for {asset_format}/{lang}: {e}")
                        asset_prompt.generation_status = "failed"
                        asset_prompt.generated_image_uri = None
                        # Store error message for UI display
                        if not hasattr(asset_prompt, 'error_message'):
                            asset_prompt.error_message = str(e)
                    except Exception as e:
                        logger.error(f"❌ Image generation failed for {asset_format}/{lang}: {e}", exc_info=True)
                        asset_prompt.generation_status = "failed"
                        asset_prompt.generated_image_uri = None
                        asset_prompt.error_message = f"Image generation error: {str(e)}"
        
        # Step 5: Check compliance
        logger.info("Step 5: Checking compliance...")
        for option in options:
            compliance_result = compliance_checker.check_compliance(
                option,
                request.product_scope,
                request.must_not_say or []
            )
            option.compliance = compliance_result
        
        # Step 6: Rank options
        logger.info("Step 6: Ranking options...")
        ranked_options = ranker.rank_options(options, chunks, request.product_scope)
        
        # Step 7: Build response
        logger.info("Step 7: Building response...")
        
        # Format retrieved sources for audit
        retrieved_sources = []
        for source_type, chunk_list in chunks.items():
            for chunk in chunk_list:
                retrieved_sources.append(RetrievedSource(
                    doc=chunk.doc_name,
                    section=chunk.section,
                    page=chunk.page,
                    chunk_id=chunk.chunk_id
                ))
        
        # Build global disclaimers per language
        default_disclaimer = compliance_checker.REQUIRED_DISCLAIMERS.get(
            request.product_scope,
            compliance_checker.REQUIRED_DISCLAIMERS["default"]
        )
        global_disclaimers = {
            lang: default_disclaimer for lang in request.languages
        }
        
        response = GenerateResponse(
            request_meta=RequestMeta(
                channel=request.channel.value,
                format=request.asset.value,
                sizes=[request.asset.value],  # Simplified
                languages=[lang.value for lang in request.languages],
                segment_id=request.segment_id,
                product_scope=request.product_scope,
                campaign_goal=request.campaign_goal,
                date=datetime.utcnow()
            ),
            constraints=Constraints(
                tone=request.tone,
                style=request.style_guidance,
                must_say=request.must_say,
                must_not_say=request.must_not_say,
                disclaimers=None
            ),
            options=ranked_options[:request.num_options],
            global_disclaimers=global_disclaimers,
            audit={
                "retrieved_sources": [s.model_dump() for s in retrieved_sources],
                "model_versions": {"claude": llm_client.default_model},
                "timestamps": {
                    "generation_start": datetime.utcnow().isoformat(),
                    "generation_end": datetime.utcnow().isoformat()
                },
                "generation_id": generation_id
            }
        )
        
        logger.info(f"Generation complete: {len(response.options)} options")
        return response
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/generation/{generation_id}")
async def get_generation(generation_id: str):
    """Get a previous generation by ID"""
    # TODO: Implement retrieval from Databricks
    raise HTTPException(status_code=501, detail="Not yet implemented")


@app.post("/regenerate")
async def regenerate_creative():
    """Regenerate with constraints"""
    # TODO: Implement regeneration
    raise HTTPException(status_code=501, detail="Not yet implemented")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
