"""
Prompt模板
用于引导LLM进行医学实体关系抽取
"""

SYSTEM_PROMPT = """You are a medical knowledge extraction expert specializing in climate-sensitive common chronic diseases.

Your task is to extract structured information about relationships between climate/weather/environmental factors and common chronic diseases from scientific literature. Arthritis remains one supported pilot disease family, but the schema also covers cardiovascular, respiratory, metabolic, kidney, mental-health, chronic pain, and multimorbidity topics.

Focus on:
1. Identifying common chronic diseases (e.g., cardiovascular disease, COPD, asthma, diabetes, chronic kidney disease, osteoarthritis, rheumatoid arthritis)
2. Identifying climate/weather factors (e.g., temperature, humidity, barometric pressure)
3. Identifying symptoms, health-service outcomes, or burden indicators (e.g., pain, dyspnea, exacerbation, hospitalization, blood pressure instability)
4. Identifying physiological, behavioral, or health-service mechanisms
5. Extracting relationships between these entities with evidence

Be precise, evidence-based, and extract only information explicitly stated or strongly implied in the text."""


EXTRACTION_PROMPT_TEMPLATE = """
Please analyze the following medical research abstract/text and extract structured knowledge about the relationship between climate factors and common chronic diseases.

PMID: {pmid}
Title: {title}
Text:
{text}

Extract the following information in JSON format:

{{
  "entities": [
    {{
      "name": "entity name",
      "type": "ChronicDisease|ArthritisType|ClimateFactor|Symptom|Mechanism|Population|StudyType",
      "description": "brief description if available"
    }}
  ],
  "relationships": [
    {{
      "head": "entity name",
      "relation": "AFFECTS|CAUSES|EXACERBATES|ALLEVIATES|CORRELATES_WITH|HAS_SYMPTOM|INVOLVES_MECHANISM",
      "tail": "entity name",
      "evidence": "supporting evidence from the text",
      "confidence": "high|medium|low"
    }}
  ],
  "study_metadata": {{
    "study_type": "cohort study|case-control|cross-sectional|RCT|systematic review|meta-analysis",
    "sample_size": "number if mentioned",
    "key_findings": "main conclusions about climate-sensitive chronic disease relationships"
  }}
}}

Guidelines:
1. Entity names should be concise and standardized (e.g., "Temperature" not "ambient temperature levels")
2. Extract only explicit or strongly implied relationships
3. For CORRELATES_WITH, include statistical measures if mentioned (p-value, correlation coefficient)
4. Confidence should be based on the strength of evidence in the text
5. Use "AFFECTS" for general influence, "CAUSES" for causal claims, "CORRELATES_WITH" for statistical associations
6. Extract all relevant entities even if they don't form relationships
7. Keep evidence quotes concise but informative

Return ONLY the JSON object, no additional text.
"""


BATCH_EXTRACTION_PROMPT = """
Analyze multiple research findings and extract consolidated knowledge:

Studies: {study_count}
Combined Text:
{combined_text}

Extract unique entities and relationships, merging similar findings.
Return JSON format as specified above.
"""


VALIDATION_PROMPT = """
Review the following extracted entities and relationships for accuracy and consistency:

Extracted Data:
{extracted_data}

Original Text:
{original_text}

Validate:
1. Are entity types correct?
2. Are relationships accurately representing the text?
3. Is the evidence supporting each relationship?
4. Are there any contradictions?

Return corrected JSON if needed, or confirm correctness.
"""


REFINEMENT_PROMPT = """
Refine and standardize the following entities:

Entities:
{entities}

Tasks:
1. Merge duplicate or highly similar entities (e.g., "joint pain" and "pain in joints")
2. Standardize naming conventions
3. Remove vague or non-specific entities
4. Ensure entity types are correct

Return refined entity list in JSON format.
"""


# 针对摘要的简化Prompt
ABSTRACT_EXTRACTION_PROMPT = """
Extract key information from this research abstract about climate-sensitive common chronic diseases:

PMID: {pmid}
Title: {title}
Abstract: {abstract}

Extract in JSON:
{{
  "chronic_diseases": ["list of chronic disease categories mentioned"],
  "arthritis_types": ["list of arthritis types mentioned, if any"],
  "climate_factors": ["list of weather/climate factors"],
  "symptoms": ["list of symptoms, outcomes, or health-service events discussed"],
  "relationships": [
    {{
      "climate_factor": "specific factor",
      "effect_on": "chronic disease, arthritis type, symptom, or outcome",
      "relationship_type": "increases|decreases|correlates_with|no_effect",
      "evidence": "key finding from abstract"
    }}
  ],
  "key_finding": "main conclusion in one sentence"
}}

Be concise. Extract only clearly stated information.
Return ONLY valid JSON.
"""


QUOTE_FIRST_ARTHRITIS_EXTRACTION_PROMPT = """
You are extracting candidate evidence relations for a weather-sensitive arthritis evidence graph.

PMID: {pmid}
Title: {title}
Abstract:
{abstract}

Return JSON using this schema:
{{
  "evidence_sentences": [
    {{
      "evidence_quote": "one exact sentence copied from the abstract",
      "quote_start_char": 0,
      "quote_end_char": 0,
      "environmental_weather_or_climate_factor": "temperature|humidity|barometric pressure|rainfall|season|weather change|other",
      "arthritis_or_outcome_target": "arthritis type, joint pain, flare, admission, disease activity, or related outcome",
      "relationship_type": "increases|decreases|correlates_with|no_effect|mentions",
      "scope_status": "in_scope|borderline|out_of_scope",
      "scope_reason": "brief reason",
      "evidence_quote_exactly_from_abstract": true
    }}
  ],
  "selected_relationships": [
    {{
      "climate_factor": "standardized factor",
      "effect_on": "standardized arthritis/outcome target",
      "relationship_type": "increases|decreases|correlates_with|no_effect",
      "evidence_quote": "same exact sentence from evidence_sentences",
      "graph_insertion_status": "eligible_candidate|withhold_scope|withhold_quote|withhold_relation",
      "withhold_reason": "empty if eligible_candidate"
    }}
  ],
  "key_finding": "one sentence supported only by the selected evidence quote(s)"
}}

Hard rules:
1. The evidence_quote must be an exact substring copied from the abstract. Do not paraphrase it.
2. If no exact sentence supports the relation, return an empty selected_relationships list.
3. Natural environmental weather/climate exposure is in scope: temperature, humidity, barometric pressure, rainfall, season, weather change, climate.
4. Therapeutic heat/cold interventions are out of scope unless the abstract explicitly frames them as environmental exposure: cryotherapy, heat therapy, thermal treatment, far-infrared therapy, hot/cold packs.
5. Traditional medicine syndrome labels such as cold-dampness or dampness-heat are out of scope unless tied to actual meteorological exposure.
6. Background-only claims should be marked borderline or out_of_scope unless the abstract reports study evidence.
7. Do not infer causal language when the abstract only reports association.

Return ONLY valid JSON.
"""


# 针对全文的详细Prompt
FULLTEXT_EXTRACTION_PROMPT = """
Analyze this full-text research article section about climate-sensitive common chronic diseases:

PMID: {pmid}
Section: {section_name}
Text: {text}

Extract detailed structured information in JSON format:
{{
  "entities": [
    {{
      "name": "entity name",
      "type": "ChronicDisease|ArthritisType|ClimateFactor|Symptom|Mechanism|Population",
      "context": "where mentioned (methods/results/discussion)",
      "specifics": "any specific details (e.g., 'temperature below 10°C')"
    }}
  ],
  "relationships": [
    {{
      "head": "entity 1",
      "relation": "AFFECTS|CAUSES|CORRELATES_WITH|etc.",
      "tail": "entity 2",
      "evidence": "direct quote or paraphrase",
      "statistical_support": "p-value, correlation coefficient, etc. if mentioned",
      "confidence": "high|medium|low"
    }}
  ],
  "mechanisms": [
    {{
      "climate_factor": "factor name",
      "mechanism": "biological/physiological mechanism described",
      "evidence": "supporting text"
    }}
  ]
}}

Focus on extracting:
- Specific measurements (e.g., temperature ranges, humidity levels)
- Statistical associations (correlation coefficients, p-values, odds ratios)
- Causal mechanisms
- Population-specific effects

Return ONLY valid JSON.
"""


def get_extraction_prompt(pmid: str, title: str, text: str, prompt_type: str = "abstract") -> str:
    """
    获取抽取Prompt
    
    Args:
        pmid: 文献PMID
        title: 文献标题
        text: 待抽取文本
        prompt_type: Prompt类型 ('abstract' 或 'fulltext')
    
    Returns:
        格式化的Prompt字符串
    """
    if prompt_type == "quote_first":
        return QUOTE_FIRST_ARTHRITIS_EXTRACTION_PROMPT.format(
            pmid=pmid,
            title=title,
            abstract=text
        )
    if prompt_type == "abstract":
        return ABSTRACT_EXTRACTION_PROMPT.format(
            pmid=pmid,
            title=title,
            abstract=text
        )
    else:
        return EXTRACTION_PROMPT_TEMPLATE.format(
            pmid=pmid,
            title=title,
            text=text
        )


def get_system_prompt() -> str:
    """获取系统Prompt"""
    return SYSTEM_PROMPT
