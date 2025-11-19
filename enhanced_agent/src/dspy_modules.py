"""
DSPy modules for structured reasoning in the enhanced research agent.

This module provides DSPy signatures and modules for:
1. Query analysis and structuring
2. Information synthesis 
3. Response generation with structured thinking
"""

import dspy
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


class QueryAnalysis(dspy.Signature):
    """Analyze a user query to extract key components and research needs."""
    
    user_query: str = dspy.InputField(description="The original user query")
    
    # Structured outputs
    main_topic: str = dspy.OutputField(description="Primary topic or subject of the query")
    sub_topics: str = dspy.OutputField(description="Related subtopics to research (comma-separated)")
    query_type: str = dspy.OutputField(description="Type of query: factual, analytical, creative, or procedural")
    information_needs: str = dspy.OutputField(description="Specific types of information needed to answer the query")
    search_terms: str = dspy.OutputField(description="Optimal search terms for external information gathering")
    recommended_sources: str = dspy.OutputField(description="Recommended data sources: web_search, wikipedia, arxiv, news_api, finance, github, weather")


class InformationSynthesis(dspy.Signature):
    """Synthesize gathered information with the original query context."""
    
    user_query: str = dspy.InputField(description="The original user query")
    query_analysis: str = dspy.InputField(description="Structured analysis of the query")
    external_info: str = dspy.InputField(description="Information gathered from external sources")
    
    # Synthesis outputs
    key_insights: str = dspy.OutputField(description="Main insights extracted from the information")
    relevance_assessment: str = dspy.OutputField(description="How well the information addresses the query")
    gaps_identified: str = dspy.OutputField(description="Information gaps that still need to be addressed")
    synthesized_context: str = dspy.OutputField(description="Integrated context combining query and information")


class ResponseGeneration(dspy.Signature):
    """Generate a comprehensive response based on structured analysis and synthesized information."""
    
    user_query: str = dspy.InputField(description="The original user query")
    synthesized_context: str = dspy.InputField(description="Synthesized information and insights")
    
    # Response outputs
    direct_answer: str = dspy.OutputField(description="Direct answer to the user's question")
    supporting_details: str = dspy.OutputField(description="Additional details and context")
    actionable_insights: str = dspy.OutputField(description="Practical next steps or recommendations")
    confidence_level: str = dspy.OutputField(description="Confidence level: high, medium, or low with reasoning")


@dataclass 
class ResearchPiplineResult:
    """Container for the complete research pipeline results."""
    
    # Query analysis results
    main_topic: str
    sub_topics: List[str]
    query_type: str
    information_needs: str
    search_terms: List[str]
    
    # Synthesis results
    key_insights: str
    relevance_assessment: str
    gaps_identified: str
    synthesized_context: str
    
    # Final response
    direct_answer: str
    supporting_details: str
    actionable_insights: str
    confidence_level: str
    
    # Raw external information
    external_info: str


class StructuredResearchPipeline(dspy.Module):
    """
    A complete DSPy module that orchestrates structured research using:
    1. Query analysis
    2. Information gathering (via MCP)  
    3. Information synthesis
    4. Response generation
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize DSPy components
        self.query_analyzer = dspy.ChainOfThought(QueryAnalysis)
        self.info_synthesizer = dspy.ChainOfThought(InformationSynthesis)
        self.response_generator = dspy.ChainOfThought(ResponseGeneration)
        
        # Store for intermediate results
        self._last_analysis = None
        self._last_synthesis = None
        
    def analyze_query(self, user_query: str) -> Dict[str, Any]:
        """Analyze the user query using DSPy structured reasoning."""
        
        result = self.query_analyzer(user_query=user_query)
        
        analysis = {
            'main_topic': result.main_topic,
            'sub_topics': [topic.strip() for topic in result.sub_topics.split(',')],
            'query_type': result.query_type,
            'information_needs': result.information_needs,
            'search_terms': [term.strip() for term in result.search_terms.split(',')],
            'recommended_sources': [source.strip() for source in result.recommended_sources.split(',')]
        }
        
        self._last_analysis = analysis
        return analysis
    
    def synthesize_information(self, user_query: str, query_analysis: Dict[str, Any], 
                             external_info: str) -> Dict[str, Any]:
        """Synthesize external information with query context."""
        
        # Convert analysis dict to string for DSPy input
        analysis_str = f"""
        Main Topic: {query_analysis['main_topic']}
        Sub Topics: {', '.join(query_analysis['sub_topics'])}
        Query Type: {query_analysis['query_type']}
        Information Needs: {query_analysis['information_needs']}
        """
        
        result = self.info_synthesizer(
            user_query=user_query,
            query_analysis=analysis_str,
            external_info=external_info
        )
        
        synthesis = {
            'key_insights': result.key_insights,
            'relevance_assessment': result.relevance_assessment,
            'gaps_identified': result.gaps_identified,
            'synthesized_context': result.synthesized_context
        }
        
        self._last_synthesis = synthesis
        return synthesis
    
    def generate_response(self, user_query: str, synthesized_context: str) -> Dict[str, Any]:
        """Generate the final structured response."""
        
        result = self.response_generator(
            user_query=user_query,
            synthesized_context=synthesized_context
        )
        
        return {
            'direct_answer': result.direct_answer,
            'supporting_details': result.supporting_details, 
            'actionable_insights': result.actionable_insights,
            'confidence_level': result.confidence_level
        }
    
    def forward(self, user_query: str, external_info: str) -> ResearchPiplineResult:
        """
        Complete forward pass through the research pipeline.
        
        Args:
            user_query: The user's research query
            external_info: Information gathered from MCP sources
            
        Returns:
            ResearchPiplineResult with all structured outputs
        """
        
        # Step 1: Analyze the query
        analysis = self.analyze_query(user_query)
        
        # Step 2: Synthesize information
        synthesis = self.synthesize_information(user_query, analysis, external_info)
        
        # Step 3: Generate response
        response = self.generate_response(user_query, synthesis['synthesized_context'])
        
        # Combine all results
        return ResearchPiplineResult(
            # Query analysis
            main_topic=analysis['main_topic'],
            sub_topics=analysis['sub_topics'],
            query_type=analysis['query_type'],
            information_needs=analysis['information_needs'],
            search_terms=analysis['search_terms'],
            
            # Synthesis
            key_insights=synthesis['key_insights'],
            relevance_assessment=synthesis['relevance_assessment'],
            gaps_identified=synthesis['gaps_identified'],
            synthesized_context=synthesis['synthesized_context'],
            
            # Response
            direct_answer=response['direct_answer'],
            supporting_details=response['supporting_details'],
            actionable_insights=response['actionable_insights'],
            confidence_level=response['confidence_level'],
            
            # Raw data
            external_info=external_info
        )


class QuickAnalysis(dspy.Module):
    """Simplified DSPy module for quick query processing without full pipeline."""
    
    def __init__(self):
        super().__init__()
        self.analyzer = dspy.ChainOfThought(QueryAnalysis)
    
    def forward(self, user_query: str) -> Dict[str, Any]:
        """Quick analysis of a user query."""
        result = self.analyzer(user_query=user_query)
        
        return {
            'main_topic': result.main_topic,
            'sub_topics': [topic.strip() for topic in result.sub_topics.split(',')],
            'query_type': result.query_type,
            'information_needs': result.information_needs,
            'search_terms': [term.strip() for term in result.search_terms.split(',')],
            'recommended_sources': [source.strip() for source in result.recommended_sources.split(',')]
        }