"""
RAG引擎 - 检索增强生成
结合知识图谱检索和LLM生成
"""

from __future__ import annotations

from typing import Dict, List
import logging

from .claim_ledger import ClaimEvidenceLedger
from .evidence_contract import ContractClaimVerifier, EvidenceContractCompiler
from .evidence_boundary import EvidenceBoundaryGate

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG引擎 - 核心智能问答服务"""
    
    def __init__(self, graph_service, llm_service):
        """初始化"""
        self.graph = graph_service
        self.llm = llm_service
        self.boundary_gate = EvidenceBoundaryGate()
        self.contract_compiler = EvidenceContractCompiler()
        self.contract_verifier = ContractClaimVerifier()
        self.claim_ledger = ClaimEvidenceLedger()
        logger.info("RAG引擎初始化完成")
    
    # ==================== 问题理解 ====================
    
    def parse_question(self, question: str) -> Dict:
        """
        解析用户问题，提取关键信息
        
        Returns:
            {
                'entities': 识别的实体,
                'intent': 问题意图 (what/why/how/statistics),
                'keywords': 关键词列表
            }
        """
        # 简单的关键词提取（实际可用更复杂的NLP）
        keywords = []
        entities = []
        
        question_lower = question.lower()
        
        # 常见慢性病关键词（中英文），关节炎作为专家初评可行性语料保留。
        disease_keywords = {
            '类风湿': 'rheumatoid arthritis',
            '骨关节炎': 'osteoarthritis', 
            '风湿性': 'rheumatic',
            '痛风': 'gout',
            '强直性脊柱炎': 'ankylosing spondylitis',
            '关节炎': 'arthritis',
            '慢性病': 'chronic disease',
            '多病共存': 'multimorbidity',
            '心血管': 'cardiovascular disease',
            '冠心病': 'ischemic heart disease',
            '心衰': 'heart failure',
            '心力衰竭': 'heart failure',
            '高血压': 'hypertension',
            '慢阻肺': 'chronic obstructive pulmonary disease',
            '哮喘': 'asthma',
            '糖尿病': 'diabetes',
            '肾病': 'chronic kidney disease',
            '慢性肾病': 'chronic kidney disease',
            '心理': 'chronic mental health conditions',
            '抑郁': 'depression',
            'arthritis': 'arthritis',
            'rheumatoid': 'rheumatoid arthritis',
            'osteoarthritis': 'osteoarthritis',
            'ra': 'rheumatoid arthritis',
            'oa': 'osteoarthritis',
            'chronic disease': 'chronic disease',
            'multimorbidity': 'multimorbidity',
            'cardiovascular': 'cardiovascular disease',
            'hypertension': 'hypertension',
            'ischemic': 'ischemic heart disease',
            'heart failure': 'heart failure',
            'copd': 'chronic obstructive pulmonary disease',
            'asthma': 'asthma',
            'diabetes': 'diabetes',
            'kidney disease': 'chronic kidney disease',
            'mental health': 'chronic mental health conditions',
            'depression': 'depression',
        }
        for kw, en in disease_keywords.items():
            if kw in question_lower:
                entities.append(('chronic_disease', en))
                keywords.append(en)
        
        # 气候因素关键词（中英文）
        climate_keywords = {
            '温度': 'temperature',
            '湿度': 'humidity',
            '气压': 'pressure',
            '天气': 'weather',
            '气候': 'climate',
            '冷': 'cold',
            '热': 'heat',
            '高温': 'extreme heat',
            '热浪': 'heat wave',
            '空气污染': 'air pollution',
            '污染': 'air pollution',
            '野火烟雾': 'wildfire smoke',
            '洪水': 'flooding',
            '潮湿': 'humidity',
            '下雨': 'rain',
            '季节': 'season',
            '温差': 'temperature variability',
            'temperature': 'temperature',
            'humidity': 'humidity',
            'pressure': 'pressure',
            'weather': 'weather',
            'climate': 'climate',
            'cold': 'cold',
            'heat': 'heat',
            'heat wave': 'heat wave',
            'extreme heat': 'extreme heat',
            'air pollution': 'air pollution',
            'wildfire smoke': 'wildfire smoke',
            'flooding': 'flooding',
            'rain': 'rain',
            'season': 'season',
            'temperature variability': 'temperature variability',
        }
        for kw, en in climate_keywords.items():
            if kw in question_lower:
                entities.append(('climate', en))
                keywords.append(en)
        
        # 症状关键词（中英文）
        symptom_keywords = {
            '疼痛': 'pain',
            '肿胀': 'swelling',
            '僵硬': 'stiffness',
            '炎症': 'inflammation',
            '关节痛': 'joint pain',
            '急性加重': 'exacerbation',
            '加重': 'exacerbation',
            '住院': 'hospital admission',
            '呼吸困难': 'dyspnea',
            '气短': 'dyspnea',
            '血压': 'blood pressure instability',
            '血糖': 'glycemic instability',
            '脱水': 'dehydration',
            '肾功能': 'renal stress',
            '用药安全': 'medication safety',
            '活动受限': 'functional limitation',
            '焦虑': 'anxiety',
            'pain': 'pain',
            'swelling': 'swelling',
            'stiffness': 'stiffness',
            'inflammation': 'inflammation',
            'exacerbation': 'exacerbation',
            'hospital admission': 'hospital admission',
            'dyspnea': 'dyspnea',
            'blood pressure': 'blood pressure instability',
            'blood glucose': 'glycemic instability',
            'dehydration': 'dehydration',
            'renal function': 'renal stress',
            'medication': 'medication safety',
            'functional limitation': 'functional limitation',
            'anxiety': 'anxiety',
        }
        for kw, en in symptom_keywords.items():
            if kw in question_lower:
                entities.append(('symptom', en))
                keywords.append(en)
        
        # 意图识别（中英文）
        intent = 'what'  # 默认
        if any(w in question_lower for w in ['为什么', '原因', '机制', '如何影响', 'why', 'cause', 'mechanism', 'how affect']):
            intent = 'why'
        elif any(w in question_lower for w in ['怎么', '如何', '方法', '建议', 'how', 'method', 'suggestion', 'recommend']):
            intent = 'how'
        elif any(w in question_lower for w in ['统计', '数量', '多少', '哪些', 'statistics', 'how many', 'which']):
            intent = 'statistics'
        elif any(w in question_lower for w in ['研究', '文献', '论文', 'research', 'study', 'paper']):
            intent = 'research'
        
        # 去重关键词
        keywords = list(set(keywords))
        
        return {
            'entities': entities,
            'intent': intent,
            'keywords': keywords,
            'original': question
        }
    
    # ==================== 知识检索 ====================
    
    def retrieve_knowledge(self, parsed_question: Dict, max_results: int = 10) -> Dict:
        """
        从知识图谱检索相关知识
        
        Returns:
            {
                'entities': 实体列表,
                'relations': 关系列表,
                'studies': 文献列表,
                'summary': 检索摘要
            }
        """
        knowledge = {
            'entities': [],
            'relations': [],
            'studies': [],
            'triage': [],
            'summary': {}
        }
        
        keywords = parsed_question['keywords']
        
        if not keywords:
            logger.warning("未提取到关键词，尝试使用原始问题")
            # 直接搜索问题中的单词
            words = parsed_question['original'].lower().split()
            keywords = [w for w in words if len(w) > 3][:3]
        
        logger.info(f"检索关键词: {keywords}")
        
        # 1. 搜索相关实体
        seen_entities = set()
        
        for keyword in keywords[:5]:  # 限制关键词数量
            try:
                entities = self.graph.search_entity(keyword)
                for e in entities:
                    entity_key = f"{e['name']}_{e['type']}"
                    if entity_key not in seen_entities:
                        seen_entities.add(entity_key)
                        knowledge['entities'].append(e)
                        if len(knowledge['entities']) >= max_results:
                            break
            except Exception as e:
                logger.error(f"搜索实体'{keyword}'失败: {e}")
                continue
            
            if len(knowledge['entities']) >= max_results:
                break
        
        logger.info(f"检索到 {len(knowledge['entities'])} 个实体")
        
        # 2. 获取实体间关系
        if len(knowledge['entities']) >= 2:
            # 查找前几个实体之间的关系
            for i, e1 in enumerate(knowledge['entities'][:3]):
                for e2 in knowledge['entities'][i+1:4]:
                    try:
                        rels = self.graph.find_relation(e1['name'], e2['name'])
                        knowledge['relations'].extend(rels)
                    except Exception as e:
                        logger.error(f"查找关系失败: {e}")
                        continue
        
        # 3. 获取相关文献
        if knowledge['entities']:
            # 取最相关的实体
            for entity in knowledge['entities'][:3]:
                try:
                    studies = self.graph.get_entity_studies(entity['name'])
                    knowledge['studies'].extend(studies[:3])
                    if len(knowledge['studies']) >= 5:
                        break
                except Exception as e:
                    logger.error(f"获取文献失败: {e}")
                    continue
        
        # 去重文献
        seen_pmids = set()
        unique_studies = []
        for study in knowledge['studies']:
            if study['pmid'] not in seen_pmids:
                seen_pmids.add(study['pmid'])
                unique_studies.append(study)
        knowledge['studies'] = unique_studies[:5]

        # 4. Retrieve evidence-triage modules when the backend exposes them.
        try:
            triage_rows = self.graph.get_evidence_triage()
            original_text = parsed_question["original"].lower()
            scored_rows = []
            for row in triage_rows:
                row_text = " ".join(str(value).lower() for value in row.values())
                score = sum(1 for keyword in keywords if keyword.lower() in row_text)
                if score == 0 and any(term in row_text for term in original_text.split() if len(term) > 3):
                    score = 1
                if score > 0:
                    scored_rows.append((score, row))
            if not scored_rows:
                scored_rows = [(0, row) for row in triage_rows[:2]]
            knowledge['triage'] = [row for _, row in sorted(scored_rows, key=lambda item: item[0], reverse=True)[:3]]
        except Exception as e:
            logger.debug(f"证据分诊模块不可用: {e}")
        
        # 5. 生成检索摘要
        knowledge['summary'] = {
            'entity_count': len(knowledge['entities']),
            'relation_count': len(knowledge['relations']),
            'study_count': len(knowledge['studies']),
            'triage_count': len(knowledge['triage']),
            'top_entities': [e['name'] for e in knowledge['entities'][:5]]
        }
        
        logger.info(f"检索完成: 实体{knowledge['summary']['entity_count']}个, "
                   f"关系{knowledge['summary']['relation_count']}个, "
                   f"文献{knowledge['summary']['study_count']}篇")
        
        return knowledge
    
    # ==================== 上下文构建 ====================
    
    def build_context(self, knowledge: Dict, role: str = "public") -> str:
        """
        构建RAG上下文
        
        Args:
            knowledge: 检索到的知识
            role: 用户角色 (public/medical/researcher)
        """
        context_parts = []
        
        # 1. 实体信息
        if knowledge['entities']:
            context_parts.append("[Relevant entities]")
            for entity in knowledge['entities'][:5]:
                context_parts.append(
                    f"- {entity['name']} ({entity['type']}): "
                    f"mentioned in {entity.get('study_count', 0)} studies"
                )
        
        # 2. 关系信息
        if knowledge['relations']:
            context_parts.append("\n[Entity relationships]")
            for rel in knowledge['relations'][:8]:
                if 'source' in rel and 'target' in rel:
                    context_parts.append(
                        f"- {rel['source']} {rel['relation']} {rel['target']}"
                    )
        
        # 3. 文献支持（医务工作者和研究者版显示）
        if role in ['medical', 'researcher'] and knowledge['studies']:
            context_parts.append("\n[Related studies]")
            for study in knowledge['studies'][:3]:
                context_parts.append(
                    f"- PMID:{study['pmid']} - {study.get('title', 'Untitled')[:60]}..."
                )

        # 4. Evidence triage modules
        if knowledge.get('triage'):
            context_parts.append("\n[Clinical-grade evidence triage]")
            for row in knowledge['triage'][:3]:
                context_parts.append(
                    f"- {row.get('module', 'N/A')}: grade={row.get('evidence_grade', 'N/A')}; "
                    f"validation={row.get('validation_status', 'N/A')}; "
                    f"clinical translation={row.get('clinical_translation', 'N/A')}; "
                    f"research readiness={row.get('research_readiness', 'N/A')}"
                )
        
        context = "\n".join(context_parts)
        return context if context else "No directly relevant graph evidence was retrieved."
    
    # ==================== 提示词生成 ====================
    
    def build_prompt(
        self,
        question: str,
        context: str,
        role: str = "public",
        boundary_instructions: str | None = None,
    ) -> List[Dict]:
        """
        构建完整的提示词
        
        Args:
            question: 用户问题
            context: RAG上下文
            role: 用户角色
        """
        # 系统提示词（根据角色定制）
        system_prompts = {
            "public": """You are a friendly public-health explainer answering questions about climate-sensitive common chronic diseases.

Answer requirements:
1. Use plain language and avoid unnecessary medical jargon.
2. Keep the answer concise, preferably under 200 words.
3. If the answer touches on medical decisions, advise users to consult a qualified clinician.
4. Be calm, clear, and evidence-aware.
5. Cover common chronic disease contexts such as cardiovascular disease, respiratory disease, diabetes, kidney disease, chronic pain, arthritis, and multimorbidity when relevant.
6. Base the answer on the supplied graph evidence; if evidence is limited, say so explicitly.""",
            
            "medical": """You are a clinical evidence assistant for health professionals.

Answer requirements:
1. Use accurate clinical terminology.
2. Analyze the supplied knowledge-graph evidence.
3. Cite PMIDs when supporting studies are available.
4. Use the evidence-triage grade, validation status, and research-readiness fields when supplied.
5. State clinical relevance and practical interpretation boundaries.
6. Maintain a professional and cautious tone.
7. Do not present graph associations as individualized clinical decision support.""",
            
            "researcher": """You are a research exploration assistant for a climate-sensitive chronic disease evidence graph.

Answer requirements:
1. Provide a structured academic analysis.
2. Use the knowledge graph to identify evidence patterns, gaps, and key findings.
3. Cite PMIDs when available.
4. Include critical interpretation and actionable research suggestions.
5. Use concise scholarly language, preferably under 300 words.
6. Emphasize that the platform supports evidence translation, not causal effect estimation.
7. If asked about evidence scope, explain which disease areas are preliminary expert-adjudicated feasibility examples and which areas require further disease-specific review.
8. Use evidence grade, validation status, and research-readiness fields to separate stronger evidence from exploratory modules."""
        }
        
        system_prompt = system_prompts.get(role, system_prompts["public"])
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Knowledge graph context:
{context}

{boundary_instructions or ""}

User question: {question}

Please answer based on the knowledge graph context above."""}
        ]
        
        return messages
    
    # ==================== 主接口 ====================
    
    def answer_question(self, question: str, role: str = "public", 
                       max_results: int = 10) -> Dict:
        """
        回答问题（主接口）
        
        Args:
            question: 用户问题
            role: 用户角色
            max_results: 最大检索结果数
        
        Returns:
            {
                'answer': 生成的答案,
                'knowledge': 检索到的知识,
                'context': RAG上下文,
                'question_analysis': 问题分析
            }
        """
        logger.info(f"收到问题 ({role}): {question}")
        
        # 1. 问题理解
        parsed = self.parse_question(question)
        logger.info(f"问题分析: 意图={parsed['intent']}, 关键词={parsed['keywords']}")
        
        # 2. 知识检索
        knowledge = self.retrieve_knowledge(parsed, max_results)
        
        # 3. Scope and safety boundary assessment
        boundary = self.boundary_gate.assess(
            question,
            role=role,
            parsed_question=parsed,
            knowledge=knowledge,
        )
        evidence_contract = self.contract_compiler.compile(
            question=question,
            role=role,
            boundary=boundary,
            knowledge=knowledge,
        )

        # 4. 构建上下文
        context = self.build_context(knowledge, role)
        
        boundary_instructions = "\n\n".join(
            [
                self.boundary_gate.prompt_instructions(boundary),
                self.contract_compiler.prompt_instructions(evidence_contract, boundary),
            ]
        )

        controlled_answer = self.contract_compiler.controlled_answer(
            question=question,
            role=role,
            contract=evidence_contract,
            boundary=boundary,
        )

        # 5. Generate or deterministically abstain according to the evidence contract.
        if evidence_contract.get("answer_mode") == "controlled_boundary_answer":
            answer = controlled_answer
        else:
            messages = self.build_prompt(question, context, role, boundary_instructions)
            temperature_map = {"public": 0.25, "medical": 0.15, "researcher": 0.15}
            temperature = temperature_map.get(role, 0.2)
            answer = self.llm.generate(messages, temperature=temperature)

        # 6. Verify answer against the evidence contract and repair if needed.
        answer, claim_verification = self.contract_verifier.verify_and_repair(
            answer=answer,
            question=question,
            context=context,
            contract=evidence_contract,
            boundary=boundary,
            role=role,
            controlled_answer=controlled_answer,
        )
        answer = self.boundary_gate.append_notice(answer, boundary)
        claim_ledger = self.claim_ledger.build(
            question=question,
            answer=answer,
            knowledge=knowledge,
            boundary=boundary,
            role=role,
        )
        
        logger.info(f"回答生成完成，长度: {len(answer)}")
        
        return {
            'answer': answer,
            'knowledge': knowledge,
            'context': context,
            'question_analysis': parsed,
            'boundary': boundary,
            'evidence_contract': evidence_contract,
            'claim_verification': claim_verification,
            'claim_ledger': claim_ledger
        }
    
    def answer_question_stream(self, question: str, role: str = "public", 
                              max_results: int = 10):
        """
        流式回答问题
        
        Yields:
            生成的文本片段
        """
        # 检索和构建提示词
        parsed = self.parse_question(question)
        knowledge = self.retrieve_knowledge(parsed, max_results)
        boundary = self.boundary_gate.assess(question, role=role, parsed_question=parsed, knowledge=knowledge)
        context = self.build_context(knowledge, role)
        messages = self.build_prompt(question, context, role, self.boundary_gate.prompt_instructions(boundary))
        
        temperature_map = {"public": 0.5, "medical": 0.3, "researcher": 0.2}
        temperature = temperature_map.get(role, 0.3)
        
        # 流式生成
        for chunk in self.llm.generate_stream(messages, temperature=temperature):
            yield chunk
        if boundary.get("warnings"):
            label = "Evidence boundary note"
            if role == "public":
                label = "Use boundary"
            elif role == "medical":
                label = "Clinical boundary"
            elif role == "researcher":
                label = "Research boundary"
            yield f"\n\n**{label}:** {' '.join(boundary['warnings'])}"


if __name__ == "__main__":
    import os
    from ..config import NEO4J_CONFIG, DEEPSEEK_CONFIG
    
    # 初始化服务
    graph_service = GraphQueryService(**NEO4J_CONFIG)
    llm_service = LLMService(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=DEEPSEEK_CONFIG['base_url'],
        model_name=DEEPSEEK_CONFIG['model_name']
    )
    
    # 创建RAG引擎
    rag = RAGEngine(graph_service, llm_service)
    
    # 测试
    result = rag.answer_question("温度对类风湿关节炎有什么影响？", role="public")
    print(f"\n问题分析: {result['question_analysis']}")
    print(f"\n检索摘要: {result['knowledge']['summary']}")
    print(f"\n答案:\n{result['answer']}")
    
    graph_service.close()
