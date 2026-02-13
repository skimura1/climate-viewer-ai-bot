"""
RAG Query System for Climate Literature
Uses SQLAlchemy for retrieval and GPT-4o for response synthesis
"""

import os
from typing import Any

from openai import OpenAI
from sqlalchemy import ARRAY, String, cast, create_engine
from sqlalchemy.orm import sessionmaker

# Import the DocumentChunk model
import sys
import os
from models.chat import ChatContext, MapState, RAGMetadata, RAGResponse
# Add the backend directory to the path so we can import models
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
from models.document_chunk import DocumentChunk


class ClimateRAGSystem:
    """
    RAG system for querying climate literature using SQLAlchemy and GPT-4o.
    """

    # Layer keyword mapping for automatic detection
    LAYER_KEYWORDS = {
        "passive_marine_flooding": [
            "marine inundation",
            "coastal flooding",
            "flooded area",
            "flood zone",
            "bathtub model",
            "passive flooding",
            "flood depth",
            "ocean flooding",
            "sea water inundation",
        ],
        "groundwater_inundation": [
            "groundwater",
            "water table",
            "subsurface flooding",
            "groundwater emergence",
            "aquifer",
            "groundwater flooding",
            "water table rise",
            "underground water",
        ],
        "low_lying_flooding": [
            "low-lying",
            "low elevation",
            "critical elevation",
            "elevation threshold",
            "below elevation",
            "low areas",
            "low lying areas",
        ],
        "compound_flooding": [
            "compound flooding",
            "multiple flood",
            "combined flooding",
            "concurrent flooding",
            "storm surge and rain",
            "multiple mechanisms",
        ],
        "drainage_backflow": [
            "storm drain",
            "drainage",
            "sewer",
            "backflow",
            "stormwater",
            "drainage system",
            "sewer flooding",
            "drain capacity",
        ],
        "future_erosion_hazard_zone": [
            "erosion",
            "shoreline retreat",
            "beach loss",
            "coastal erosion",
            "shoreline change",
            "erosion rate",
            "beach erosion",
            "hazard zone",
        ],
        "annual_high_wave_flooding": [
            "wave",
            "wave runup",
            "wave-driven",
            "overwash",
            "wave setup",
            "high wave",
            "extreme wave",
            "wave impact",
            "wave flooding",
        ],
        "emergent_and_shallow_groundwater": [
            "shallow groundwater",
            "emergent groundwater",
            "groundwater depth",
            "groundwater level",
            "subsurface water",
            "water table depth",
        ],
    }

    def __init__(
        self,
        database_url: str | None = None,
        model: str = "gpt-4o",
        embedding_model: str = "text-embedding-3-small",
    ):
        """
        Initialize the RAG system.

        Args:
            database_url: PostgreSQL connection URL (defaults to env var)
            model: GPT model for response synthesis
            embedding_model: Model for generating query embeddings
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL not provided and not found in environment")

        self.model = model
        self.embedding_model = embedding_model
        self.client = OpenAI()

        # Setup database connection
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for query text."""
        response = self.client.embeddings.create(
            input=text, model=self.embedding_model
        )
        return response.data[0].embedding

    def detect_layers_from_query(self, query: str) -> list[str]:
        """
        Automatically detect relevant layers based on keywords in the query.

        Args:
            query: User's question text

        Returns:
            List of detected layer names (empty list if none detected)
        """
        query_lower = query.lower()
        detected_layers = []

        for layer, keywords in self.LAYER_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    if layer not in detected_layers:
                        detected_layers.append(layer)
                    break  # Move to next layer once we found a match

        return detected_layers

    def retrieve_chunks(
        self,
        query: str,
        top_k: int = 10,
        layers: list[str] | None = None,
        min_confidence: str | None = "MEDIUM",
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant chunks from the database.

        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            layers: Optional list of climate layers to filter by
            min_confidence: Minimum confidence level (HIGH, MEDIUM, LOW)

        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Confidence level mapping
        confidence_levels = {
            "HIGH": ["HIGH"],
            "MEDIUM": ["HIGH", "MEDIUM"],
            "LOW": ["HIGH", "MEDIUM", "LOW"],
        }

        with self.SessionLocal() as session:
            # Build query
            query_obj = session.query(
                DocumentChunk,
                DocumentChunk.embedding.cosine_distance(query_embedding).label(
                    "distance"
                ),
            )

            # Filter by layers if specified
            if layers:
                filter_array = cast(layers, ARRAY(String))
                query_obj = query_obj.filter(
                    DocumentChunk.relevant_layers.op("&&")(filter_array)
                )

            # Filter by confidence
            if min_confidence:
                allowed_confidences = confidence_levels.get(
                    min_confidence, ["HIGH", "MEDIUM", "LOW"]
                )
                query_obj = query_obj.filter(
                    DocumentChunk.confidence.in_(allowed_confidences)
                )

            # Execute query
            results = query_obj.order_by("distance").limit(top_k).all()

            # Format results
            chunks = []
            for chunk, distance in results:
                chunks.append(
                    {
                        "chunk_id": chunk.chunk_id,
                        "text": chunk.text,
                        "similarity_score": 1 - distance,
                        "distance": distance,
                        "filename": chunk.filename,
                        "confidence": chunk.confidence,
                        "relevant_layers": chunk.relevant_layers or [],
                        "key_findings": chunk.key_findings,
                        "locations": chunk.locations or [],
                        "slr_projections": chunk.slr_projections or [],
                        "measurements": chunk.measurements or [],
                        "timeframes": chunk.timeframes or [],
                        "reasoning": chunk.reasoning,
                    }
                )

            return chunks

    def build_context_prompt(
        self, query: str, chunks: list[dict[str, Any]], chat_context: ChatContext, map_state: MapState
    ) -> str:
        """
        Build the context prompt from retrieved chunks.

        Args:
            query: User's question
            chunks: Retrieved document chunks
            chat_context: Chat context
            map_state: Map state

        Returns:
            Formatted prompt string
        """
        # Build context from chunks
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"=== SOURCE {i} ===")
            context_parts.append(f"Document: {chunk['filename']}")
            context_parts.append(f"Confidence: {chunk['confidence']}")
            if chunk['relevant_layers']:
                context_parts.append(
                    f"Relevant Layers: {', '.join(chunk['relevant_layers'])}"
                )
            if chunk['locations']:
                context_parts.append(f"Locations: {', '.join(chunk['locations'])}")
            if chunk['slr_projections']:
                context_parts.append(
                    f"SLR Projections: {', '.join(chunk['slr_projections'])}"
                )
            if chunk['measurements']:
                context_parts.append(
                    f"Measurements: {', '.join(chunk['measurements'])}"
                )
            if chunk['key_findings']:
                context_parts.append(f"Key Findings: {chunk['key_findings']}")

            context_parts.append(f"\nText:\n{chunk['text']}\n")
            context_parts.append("-" * 80 + "\n")

        context = "\n".join(context_parts)

        chat_history = f"Chat History: {chat_context.messages}"
        basemap_info = f"Current Basemap: {map_state.basemap_name}"
        if map_state.active_layers:
            layer_info = "Currently displayed layers:\n"
            for layer in map_state.active_layers:
                layer_info += f"    {layer}\n"
        else:
            layer_info = "No layers currently displayed."

        # Build the full prompt
        prompt = f"""You are a helpful climate assistant for Hawaii who is an expert in sea level rise and coastal flooding. Your job is to make scientific research about sea level rise and coastal flooding easy to understand for everyone—from students to homeowners to policymakers. You also will guide users in using the CRC Climate Viewer to answer their questions.

=== RETRIEVED SCIENTIFIC LITERATURE ===
{context}

=== CURRENT MAP STATE ===
{basemap_info}
{layer_info}

=== LAYER DEFINITIONS (for reference) ===

**FLOODING TYPES**:

1. **passive_marine_flooding** - Ocean water flooding the land as sea levels rise
2. **groundwater_inundation** - Flooding from groundwater rising to the surface
3. **low_lying_flooding** - Low-elevation areas vulnerable to flooding
4. **compound_flooding** - Multiple types of flooding happening at once
5. **drainage_backflow** - Storm drains and sewers backing up during floods

**COASTAL HAZARDS**:

6. **future_erosion_hazard_zone** - Areas where beaches/shorelines are eroding
7. **annual_high_wave_flooding** - Coastal flooding from large waves
8. **emergent_and_shallow_groundwater** - Groundwater very close to the surface

=== CONVERSATION CONTEXT ===
{chat_history}

=== YOUR ROLE ===

Answer the user's question in a friendly, conversational way: **{query}**

=== HOW TO RESPOND ===

**Tone & Style:**
- Write like you're explaining to a curious friend, not writing a research paper
- Use everyday language, but keep the science accurate
- Break down complex ideas into simple terms
- Be helpful and empathetic—people care about this because it affects their homes and communities

**Content Structure:**
1. **Start with a direct answer** - Don't make people wait for the key information
2. **Add supporting details** - Explain the "why" and "how" in simple terms
3. **Include specific numbers** - Say "3 feet of flooding by 2050" not just "significant flooding"
4. **Mention locations** - Help people understand if this affects their island/community
5. **Be honest about uncertainty** - If scientists aren't 100% sure, say so

**What to include:**
✅ Specific measurements (e.g., "3.2 feet of sea level rise")
✅ Timeframes (e.g., "by 2100" or "in the next 30 years")
✅ Hawaiian locations (e.g., "Waikiki, Honolulu, Maui")
✅ What this means practically (e.g., "This could affect coastal roads and buildings")
✅ Source attribution when important (e.g., "Research from UH found that...")

**What to avoid:**
❌ Jargon without explanation (don't say "NAVD88" unless you explain it)
❌ Vague statements (not "significant impacts" but "flooding up to 2 feet deep")
❌ Information not in the sources (don't make things up or guess)
❌ Overly academic language (not "inundation" → say "flooding")

**If the sources don't answer the question:**
- Be honest: "The research I have doesn't cover that specific question."
- Offer what you do know: "But here's what I can tell you about [related topic]..."
- Suggest clarification: "Could you ask about [specific aspect]?"

**Example good responses:**

Query: "Will Waikiki flood?"
Good: "Yes, Waikiki is vulnerable to flooding from sea level rise. Research from the University of Hawaii shows that with 3 feet of sea level rise (expected by 2060-2080), significant parts of Waikiki could experience regular flooding, especially during high tides and storms. This includes areas near the beach and some inland streets."

Query: "What's passive flooding?"
Good: "Passive flooding—also called marine inundation—happens when rising sea levels cause ocean water to simply overflow onto land, even without storms or waves. Think of it like a bathtub slowly filling up. Unlike dramatic storm flooding, this happens gradually and can become permanent as sea levels keep rising."

=== NOW ANSWER THE QUESTION ===

Remember: Be clear, specific, and helpful. Your goal is to help people understand what the science says and what it means for Hawaii.

Begin your response: """

        return prompt

    def generate_response(
        self,
        query: str,
        context: ChatContext,
        map_state: MapState,
        top_k: int = 10,
        layers: list[str] | None = None,
        min_confidence: str = "MEDIUM",
        temperature: float = 0.0,
        auto_detect_layers: bool = True,
    ) -> RAGResponse:
        """
        Generate a RAG response to a user query.

        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            layers: Optional layer filter (if None and auto_detect_layers=True, will auto-detect)
            min_confidence: Minimum confidence level
            temperature: GPT temperature (0 = deterministic, best for definition/testing)
            auto_detect_layers: If True and layers=None, automatically detect layers from query

        Returns:
            Dictionary with answer, sources, and metadata
        """
        # Auto-detect layers if enabled and no layers provided
        detected_layers = None
        if auto_detect_layers and layers is None:
            detected_layers = self.detect_layers_from_query(query)
            if detected_layers:
                print(f"🔍 Auto-detected layers: {', '.join(detected_layers)}")
                layers = detected_layers

        # Step 1: Retrieve relevant chunks
        print(f"🔍 Retrieving top {top_k} chunks...")
        if layers:
            print(f"   Filtering by layers: {', '.join(layers)}")

        chunks = self.retrieve_chunks(
            query=query,
            top_k=top_k,
            layers=layers,
            min_confidence=min_confidence,
        )

        if not chunks:
            return RAGResponse(
                response="No relevant information found in the database for this query.",
                sources=[],
                metadata=RAGMetadata(
                    chunks_retrieved=0,
                    model=self.model,
                    embedding_model=self.embedding_model,
                    query=query,
                    filters={"layers": layers, "min_confidence": min_confidence},
                    auto_detected_layers=detected_layers
                )
            )

        print(f"✅ Retrieved {len(chunks)} chunks")

        # Step 2: Build prompt with context
        print("📝 Building context prompt...")
        prompt = self.build_context_prompt(query, chunks, context, map_state)

        # Step 3: Generate response with GPT-4o
        print(f"🤖 Generating response with {self.model}...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )

        answer = response.choices[0].message.content

        # Step 4: Format response
        result = {
            "answer": answer,
            "sources": [
                {
                    "source_number": i + 1,
                    "filename": chunk["filename"],
                    "confidence": chunk["confidence"],
                    "layers": chunk["relevant_layers"],
                    "similarity_score": round(chunk["similarity_score"], 4),
                    "locations": chunk["locations"],
                    "measurements": chunk["measurements"],
                    "text_preview": chunk["text"][:200] + "...",
                }
                for i, chunk in enumerate(chunks)
            ],
            "metadata": {
                "chunks_retrieved": len(chunks),
                "model": self.model,
                "embedding_model": self.embedding_model,
                "query": query,
                "filters": {"layers": layers, "min_confidence": min_confidence},
                "auto_detected_layers": detected_layers,
            },
        }

        return RAGResponse(response=result["answer"], sources=result["sources"], metadata=result["metadata"])

    def print_response(self, result: RAGResponse):
        """Pretty print a RAG response."""
        print("\n" + "=" * 80)
        print("ANSWER")
        print("=" * 80)
        print(result.response)

        print("\n" + "=" * 80)
        print(f"SOURCES ({len(result.sources)} documents)")
        print("=" * 80)

        for source in result.sources:
            print(f"\n[{source.source_number}] {source.filename}")
            print(f"    Confidence: {source.confidence}")
            print(f"    Similarity: {source.similarity_score:.4f}")
            print(f"    Layers: {', '.join(source.layers)}")
            if source.locations:
                print(f"    Locations: {', '.join(source.locations)}")
            if source.measurements:
                print(f"    Measurements: {', '.join(source.measurements[:3])}...")

        print("\n" + "=" * 80)
        print("METADATA")
        print("=" * 80)
        print(f"Model: {result.metadata.model}")
        print(f"Chunks Retrieved: {result.metadata.chunks_retrieved}")
        print(f"Filters: {result.metadata.filters}")
        if result.metadata.auto_detected_layers:
            print(f"Auto-detected Layers: {', '.join(result.metadata.auto_detected_layers)}")
