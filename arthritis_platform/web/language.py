"""
Bilingual text packs for the three Streamlit interfaces.

The product theme is expanded from a single arthritis use case to a common
chronic-disease evidence translation platform. Arthritis remains the preliminary
expert-adjudicated feasibility corpus in the demo evidence lineage.
"""

from __future__ import annotations

from typing import Dict, List

from arthritis_platform.web.runtime import get_platform_metrics


LANGUAGE_LABELS = ["中文", "English"]


def language_code(label: str) -> str:
    return "en" if label == "English" else "zh"


def runtime_status(runtime: object, lang: str) -> Dict[str, str]:
    if getattr(runtime, "is_demo", True):
        if lang == "zh":
            return {
                "label": "证据库模式",
                "detail": "当前加载内置慢病证据和关节炎专家初评数据，可在没有外部服务的情况下完成解释、检索和导出。",
                "badge": "可用",
            }
        return {
            "label": "Local evidence-base mode",
            "detail": "This page loads embedded chronic-disease evidence and preliminary arthritis adjudication data for explanation, retrieval, and export without external services.",
            "badge": "READY",
        }

    if lang == "zh":
        return {
            "label": "实时Graph-RAG模式",
            "detail": "已连接Neo4j和外部LLM服务，可使用实时知识图谱检索、问答、导出和增量更新结果。",
            "badge": "实时",
        }
    return {
        "label": "Live Graph-RAG mode",
        "detail": "Connected to Neo4j and external LLM services for live retrieval, synthesis, export, and update inspection.",
        "badge": "LIVE",
    }


def localized_platform_metrics(graph: object, lang: str) -> List[Dict[str, str]]:
    metrics = get_platform_metrics(graph)
    if lang != "zh":
        return metrics

    labels = {
        "Evidence nodes": ("证据节点", "图谱概念"),
        "Relationships": ("关系数量", "可追溯链接"),
        "Climate factors": ("气候因素", "天气/气象暴露"),
        "Chronic disease entities": ("慢性病实体", "常见慢病类别"),
        "Triage modules": ("分诊模块", "临床级分层"),
        "KG time span": ("图谱时间跨度", "近20年文献窗口"),
        "Expert validation": ("专家验证", "图谱可用样本"),
    }
    localized = []
    for metric in metrics:
        label, detail = labels.get(metric["label"], (metric["label"], metric["detail"]))
        localized.append({"label": label, "value": metric["value"], "detail": detail})
    return localized


DEFAULT_TRIAGE_ROWS = [
    {
        "module": "Heat-cardio-renal-metabolic",
        "exposure": "heat wave / extreme heat",
        "disease_domain": "cardiovascular disease; heart failure; diabetes; chronic kidney disease",
        "evidence_grade": "Literature-based scaffold: external evidence; no in-study validation",
        "validation_status": "Ontology-supported extension; disease-specific extraction and expert validation pending",
        "clinical_translation": "Use for risk communication about hydration, medication safety, blood pressure/glucose monitoring, kidney stress, and follow-up thresholds.",
        "research_readiness": "High",
        "next_study": "Time-stratified case-crossover or DLNM using emergency, outpatient, or claims records.",
    },
    {
        "module": "Pollution-respiratory-cardiovascular",
        "exposure": "air pollution / wildfire smoke",
        "disease_domain": "COPD; asthma; cardiovascular disease",
        "evidence_grade": "Literature-based scaffold: external evidence; no in-study validation",
        "validation_status": "Ontology-supported extension; disease-specific extraction and expert validation pending",
        "clinical_translation": "Use for action-plan checks, inhaler adherence review, exacerbation recognition, and follow-up planning during smog or smoke events.",
        "research_readiness": "High",
        "next_study": "Multi-pollutant time-series or case-crossover analysis with weather interaction terms.",
    },
    {
        "module": "Cold-blood pressure-ischemic risk",
        "exposure": "cold exposure / temperature variability",
        "disease_domain": "hypertension; ischemic heart disease; heart failure",
        "evidence_grade": "Plausible scaffold: clinically important but no in-study validation",
        "validation_status": "Ontology-supported extension; disease-specific extraction and expert validation pending",
        "clinical_translation": "Use to organize blood-pressure logs, medication adherence checks, chest-pain triage, and warnings not to delay acute evaluation.",
        "research_readiness": "Moderate-high",
        "next_study": "Self-controlled case series or DLNM linking cold spells with blood pressure and visit records.",
    },
    {
        "module": "Weather-pain-rheumatology feasibility case",
        "exposure": "temperature; humidity; barometric pressure; seasonal variation",
        "disease_domain": "osteoarthritis; rheumatoid arthritis; gout; chronic pain",
        "evidence_grade": "Expert-adjudicated feasibility evidence: heterogeneous weather-pain signal",
        "validation_status": "Empirical extraction and preliminary dual-expert adjudication completed",
        "clinical_translation": "Use symptom diaries and standard disease assessment; do not treat weather sensitivity as diagnosis or disease activity.",
        "research_readiness": "High for feasibility extension",
        "next_study": "Repeated symptom diary study with local meteorology and within-person controls.",
    },
    {
        "module": "Extreme events-medication access",
        "exposure": "flooding / disrupted services / climate change",
        "disease_domain": "multimorbidity; chronic mental health conditions; medication safety",
        "evidence_grade": "Hypothesis-generating scaffold: service-continuity signal",
        "validation_status": "Ontology-supported extension; disease-specific extraction and expert validation pending",
        "clinical_translation": "Use for preparedness counseling, medication continuity planning, and vulnerability screening in chronic disease follow-up.",
        "research_readiness": "Moderate",
        "next_study": "Mixed-methods or interrupted time-series study of service disruption and medication continuity.",
    },
]


def _triage_rows(graph: object) -> List[Dict[str, str]]:
    try:
        rows = graph.get_evidence_triage()
        return rows if rows else DEFAULT_TRIAGE_ROWS
    except Exception:
        return DEFAULT_TRIAGE_ROWS


def localized_evidence_triage(graph: object, lang: str) -> List[Dict[str, str]]:
    """Return the evidence triage layer with language-specific column labels."""
    rows = _triage_rows(graph)
    if lang == "en":
        return [
            {
                "Module": row["module"],
                "Exposure": row["exposure"],
                "Disease domain": row["disease_domain"],
                "Evidence grade": row["evidence_grade"],
                "Validation status": row["validation_status"],
            }
            for row in rows
        ]

    grade_map = {
        "Literature-based scaffold: external evidence; no in-study validation": "外部文献支架：本研究未验证",
        "Plausible scaffold: clinically important but no in-study validation": "合理支架：临床重要但本研究未验证",
        "Expert-adjudicated feasibility evidence: heterogeneous weather-pain signal": "专家初评可行性证据：天气-疼痛信号存在异质性",
        "Hypothesis-generating scaffold: service-continuity signal": "假设生成支架：服务连续性信号",
    }
    status_map = {
        "Ontology-supported extension; disease-specific extraction and expert validation pending": "本体支持扩展；仍需疾病专题抽取和专家验证",
        "Empirical extraction and preliminary dual-expert adjudication completed": "已完成实证抽取和双专家初步判读",
    }
    module_map = {
        "Heat-cardio-renal-metabolic": "高温-心肾代谢模块",
        "Pollution-respiratory-cardiovascular": "污染-呼吸心血管模块",
        "Cold-blood pressure-ischemic risk": "寒冷-血压缺血风险模块",
        "Weather-pain-rheumatology feasibility case": "天气-疼痛风湿可行性样本",
        "Extreme events-medication access": "极端事件-用药连续性模块",
    }
    exposure_map = {
        "heat wave / extreme heat": "热浪/极端高温",
        "air pollution / wildfire smoke": "空气污染/野火烟雾",
        "cold exposure / temperature variability": "寒冷暴露/温度变异",
        "temperature; humidity; barometric pressure; seasonal variation": "温度、湿度、气压、季节变化",
        "flooding / disrupted services / climate change": "洪水/服务中断/气候变化",
    }
    disease_map = {
        "cardiovascular disease; heart failure; diabetes; chronic kidney disease": "心血管病、心衰、糖尿病、慢性肾病",
        "COPD; asthma; cardiovascular disease": "慢阻肺、哮喘、心血管病",
        "hypertension; ischemic heart disease; heart failure": "高血压、缺血性心脏病、心衰",
        "osteoarthritis; rheumatoid arthritis; gout; chronic pain": "骨关节炎、类风湿关节炎、痛风、慢性疼痛",
        "multimorbidity; chronic mental health conditions; medication safety": "多病共存、慢性心理健康问题、用药安全",
    }
    return [
        {
            "模块": module_map.get(row["module"], row["module"]),
            "暴露": exposure_map.get(row["exposure"], row["exposure"]),
            "慢病领域": disease_map.get(row["disease_domain"], row["disease_domain"]),
            "证据等级": grade_map.get(row["evidence_grade"], row["evidence_grade"]),
            "验证状态": status_map.get(row["validation_status"], row["validation_status"]),
        }
        for row in rows
    ]


def localized_clinical_translation(graph: object, lang: str) -> List[Dict[str, str]]:
    """Return practical clinician-facing actions with explicit boundaries."""
    rows = _triage_rows(graph)
    if lang == "en":
        return [
            {
                "Clinical module": row["module"],
                "Translation action": row["clinical_translation"],
                "Boundary": "Evidence translation only; not diagnosis, prediction, or medication adjustment.",
            }
            for row in rows
        ]
    module_map = {
        "Heat-cardio-renal-metabolic": "高温-心肾代谢模块",
        "Pollution-respiratory-cardiovascular": "污染-呼吸心血管模块",
        "Cold-blood pressure-ischemic risk": "寒冷-血压缺血风险模块",
        "Weather-pain-rheumatology feasibility case": "天气-疼痛风湿可行性样本",
        "Extreme events-medication access": "极端事件-用药连续性模块",
    }
    action_map = {
        "Use for risk communication about hydration, medication safety, blood pressure/glucose monitoring, kidney stress, and follow-up thresholds.": "用于补水、用药安全、血压/血糖监测、肾脏压力和复诊阈值的风险沟通。",
        "Use for action-plan checks, inhaler adherence review, exacerbation recognition, and follow-up planning during smog or smoke events.": "用于污染或烟雾事件中的行动计划核查、吸入药依从性、急性加重识别和随访安排。",
        "Use to organize blood-pressure logs, medication adherence checks, chest-pain triage, and warnings not to delay acute evaluation.": "用于整理血压记录、用药依从性、胸痛分诊，并强调不能因天气解释而延误急症评估。",
        "Use symptom diaries and standard disease assessment; do not treat weather sensitivity as diagnosis or disease activity.": "结合症状日记和标准疾病评估；不要把天气敏感性当作诊断或疾病活动度判断。",
        "Use for preparedness counseling, medication continuity planning, and vulnerability screening in chronic disease follow-up.": "用于慢病随访中的应急准备沟通、用药连续性计划和脆弱性筛查。",
    }
    return [
        {
            "临床模块": module_map.get(row["module"], row["module"]),
            "可转化行动": action_map.get(row["clinical_translation"], row["clinical_translation"]),
            "使用边界": "仅用于证据转译；不是诊断、预测或用药调整工具。",
        }
        for row in rows
    ]


def localized_research_readiness(graph: object, lang: str) -> List[Dict[str, str]]:
    """Return research-facing readiness classes for follow-up study planning."""
    rows = _triage_rows(graph)
    if lang == "en":
        return [
            {
                "Module": row["module"],
                "Readiness": row["research_readiness"],
                "Validation": row["validation_status"],
                "Next study design": row["next_study"],
            }
            for row in rows
        ]
    readiness_map = {"High": "高", "Moderate-high": "中高", "High for feasibility extension": "可行性延伸较高", "Moderate": "中"}
    module_map = {
        "Heat-cardio-renal-metabolic": "高温-心肾代谢模块",
        "Pollution-respiratory-cardiovascular": "污染-呼吸心血管模块",
        "Cold-blood pressure-ischemic risk": "寒冷-血压缺血风险模块",
        "Weather-pain-rheumatology feasibility case": "天气-疼痛风湿可行性样本",
        "Extreme events-medication access": "极端事件-用药连续性模块",
    }
    status_map = {
        "Ontology extension; disease-specific extraction pending": "证据库扩展信号；需疾病专题复核",
        "Empirical extraction and preliminary dual-expert adjudication completed": "已完成实证抽取和双专家初步判读",
        "Hypothesis-generating ontology extension": "假设生成型本体扩展",
    }
    design_map = {
        "Time-stratified case-crossover or DLNM using emergency, outpatient, or claims records.": "采用急诊、门诊或医保记录开展时间分层病例交叉或DLNM研究。",
        "Multi-pollutant time-series or case-crossover analysis with weather interaction terms.": "采用多污染物时间序列或病例交叉设计，并加入天气交互项。",
        "Self-controlled case series or DLNM linking cold spells with blood pressure and visit records.": "使用自我对照病例序列或DLNM连接寒潮、血压和就诊记录。",
        "Repeated symptom diary study with local meteorology and within-person controls.": "开展重复症状日记研究，链接本地气象暴露并控制个体内差异。",
        "Mixed-methods or interrupted time-series study of service disruption and medication continuity.": "开展服务中断和用药连续性的混合方法或中断时间序列研究。",
    }
    return [
        {
            "模块": module_map.get(row["module"], row["module"]),
            "研究就绪度": readiness_map.get(row["research_readiness"], row["research_readiness"]),
            "验证基础": status_map.get(row["validation_status"], row["validation_status"]),
            "后续研究设计": design_map.get(row["next_study"], row["next_study"]),
        }
        for row in rows
    ]


COMMON_EVIDENCE = {
    "zh": [
        {"领域": "高温/热浪与心肾代谢风险", "图谱信号": "高频慢病主题", "可追溯性": "实体、关系、PMID", "解释边界": "用于风险沟通，不做个体预测"},
        {"领域": "空气污染与呼吸/心血管事件", "图谱信号": "成熟证据簇", "可追溯性": "暴露-疾病-结局链", "解释边界": "暴露窗口和结局定义差异大"},
        {"领域": "天气波动与慢性疼痛/关节症状", "图谱信号": "专家初评可行性样本", "可追溯性": "关节炎语料、专家初评", "解释边界": "相关性，不替代疾病活动度评估"},
    ],
    "en": [
        {"Domain": "Heat and cardio-renal-metabolic risk", "Signal": "High-frequency chronic disease theme", "Traceability": "Entity, relation, PMID", "Caution": "Risk communication, not individual prediction"},
        {"Domain": "Air pollution and respiratory/cardiovascular events", "Signal": "Mature evidence cluster", "Traceability": "Exposure-disease-outcome chains", "Caution": "Exposure windows and endpoints vary"},
        {"Domain": "Weather variability and chronic pain/joint symptoms", "Signal": "Expert-adjudicated feasibility case", "Traceability": "Arthritis corpus and expert review", "Caution": "Association, not disease activity assessment"},
    ],
}


PUBLIC_TEXT = {
    "zh": {
        "page_title": "健康科普助手 - 天气与常见慢性病",
        "language_label": "页面语言",
        "hero": {
            "title": "天气与慢性病健康助手",
            "subtitle": "面向普通人的实用页面：把高温、寒潮、空气污染、潮湿和天气波动与心血管病、呼吸病、糖尿病、肾病、慢性疼痛和关节炎的关系讲清楚。",
            "eyebrow": "公众端健康解释与就医边界",
            "pills": ["通俗解释", "慢病风险", "症状记录", "就医提示", "非诊疗建议"],
        },
        "sections": {
            "value": ("我能帮你做什么", "先给出能直接使用的慢病健康解释和行动边界，再通过问答继续追问。"),
            "self_check": ("自我观察与就医边界", "这不是诊断表，而是帮助普通人把症状讲清楚、知道什么时候该就医。"),
            "visit_note": ("就医沟通小条", "把零散不舒服整理成医生能快速理解的三句话。"),
            "quick": ("快捷问题", "选择一个常见问题，系统会直接发送并生成回答。"),
            "snapshot": ("怎么理解这些信息", "把天气提示翻译成日常观察、就医沟通和安全边界。"),
        },
        "metrics": [
            {"label": "常见场景", "value": "3类", "detail": "热浪、污染、寒潮/潮湿"},
            {"label": "关注慢病", "value": "6类", "detail": "心肺肾代谢、疼痛、关节炎"},
            {"label": "行动重点", "value": "记录", "detail": "症状、暴露、用药背景"},
            {"label": "安全边界", "value": "红旗", "detail": "胸痛、严重气短、晕厥等"},
        ],
        "cards": [
            {
                "tag": "日常解释",
                "title": "天气和环境变化可能影响慢病症状，但不能单独说明病情加重。",
                "statement": "系统把高温、寒冷、空气污染、潮湿、心血管病、呼吸病、糖尿病、肾病、慢性疼痛和关节炎放入同一证据网络，帮助用户理解“风险提示”和“诊断”的区别。",
                "meta": [
                    {"label": "适合询问", "value": "热浪、雾霾、寒潮、下雨、潮湿时慢病症状为什么会波动。"},
                    {"label": "能得到", "value": "通俗解释、日常观察建议、就医边界。"},
                    {"label": "不能替代", "value": "医生诊断、用药调整、急症处理或个体风险预测。"},
                ],
            },
            {
                "tag": "行动边界",
                "title": "把症状、天气和用药背景记录下来，比只说“不舒服”更有用。",
                "statement": "建议记录症状出现时间、暴露场景、活动量、饮水、睡眠、用药和伴随症状，为就诊沟通提供线索。",
                "meta": [
                    {"label": "记录重点", "value": "胸闷、气短、头晕、血压/血糖波动、疼痛评分、晨僵、活动受限。"},
                    {"label": "及时就医", "value": "胸痛、严重呼吸困难、意识不清、晕厥、持续高热或症状快速加重。"},
                    {"label": "就医沟通", "value": "把科普问答变成可带去就诊的健康记录。"},
                ],
            },
        ],
        "self_check_rows": [
            {"使用场景": "热浪期间有心血管病、糖尿病或肾病", "可以先做": "避开高温时段、补水、关注尿量和血压/血糖，确认药物保存和服用情况。", "建议询问医生": "长期服用利尿剂、降压药、降糖药，或近期出现明显乏力、头晕。", "需要警惕": "胸痛、晕厥、意识混乱、严重脱水、呼吸困难。"},
            {"使用场景": "空气污染或烟雾天有哮喘/COPD", "可以先做": "减少户外活动，按医嘱使用吸入药，观察咳嗽、喘息和活动耐量。", "建议询问医生": "症状比平时明显、夜间憋醒、急救药使用次数增加。", "需要警惕": "说话困难、口唇发紫、静息气短或血氧下降。"},
            {"使用场景": "寒潮或潮湿后疼痛、僵硬、血压波动", "可以先做": "保暖、温和活动、记录疼痛和血压，不把所有变化都归因于天气。", "建议询问医生": "疼痛持续、关节肿胀、晨僵较长或血压持续异常。", "需要警惕": "红肿热痛、发热、突然不能负重、剧烈头痛或胸闷。"},
        ],
        "visit_note_rows": [
            {"告诉医生": "我原来有什么慢病", "怎么说更清楚": "例如高血压、冠心病、哮喘/COPD、糖尿病、慢性肾病、关节炎或慢性疼痛。", "最好带上": "近期血压/血糖、吸入药或止痛药使用、既往诊断和处方。"},
            {"告诉医生": "症状从什么时候开始", "怎么说更清楚": "说明高温、雾霾、寒潮、潮湿或天气突变前后，症状是否比平时更重。", "最好带上": "日期、疼痛评分、气短程度、晨僵时间、尿量、睡眠和活动变化。"},
            {"告诉医生": "有没有红旗信号", "怎么说更清楚": "胸痛、明显气短、晕厥、意识不清、持续高热、关节红肿热痛或突然不能负重。", "最好带上": "如果有这些情况，不建议等线上解释，应及时就医。"},
        ],
        "pipeline": [
            {"title": "描述情况", "body": "慢病类型、症状、天气/污染暴露和用药背景"},
            {"title": "查找资料", "body": "从气候敏感性慢病证据库整理相关概念"},
            {"title": "清楚解释", "body": "用普通人能理解的话说明相关性和不确定性"},
            {"title": "准备就医", "body": "整理可带给医生的问题和红旗信号"},
        ],
        "workbench": [
            {"title": "今天先看什么", "body": "根据热浪、污染、寒潮或潮湿场景，先看症状有没有变重。"},
            {"title": "就诊前记什么", "body": "记录症状时间、天气/污染暴露、血压血糖、疼痛评分、用药和活动情况。"},
            {"title": "什么时候别等", "body": "胸痛、严重气短、晕厥、意识混乱、突然不能负重等情况应及时就医。"},
        ],
        "sidebar": {
            "title": "使用说明",
            "body": "适合快速了解天气、空气污染和常见慢性病日常管理之间的关系。",
            "items": ["热浪时慢病患者怎么注意？", "雾霾天哮喘/COPD怎么办？", "天气变化为什么会疼？", "哪些情况需要及时就医？"],
            "caption": "提示：本助手仅供科普参考，具体诊疗请咨询专业医生。",
        },
        "chat": {"input": "请输入您的问题...", "spinner": "正在整理证据...", "sources": "知识来源", "boundary": "证据边界判断", "claim_ledger": "主张-证据账本", "concepts": "相关概念", "no_knowledge": "未找到相关知识", "error": "抱歉，处理您的问题时出错了：", "clear": "清除对话历史", "study_label": "篇文献提及"},
        "quick_questions": [
            {"button": "热浪时慢病患者注意什么？", "prompt": "热浪期间，心血管病、糖尿病或肾病患者需要注意什么？请用通俗语言说明。"},
            {"button": "雾霾天哮喘/COPD怎么办？", "prompt": "空气污染或烟雾天气会怎样影响哮喘和慢阻肺？普通人可以怎样观察和应对？"},
            {"button": "天气变化为什么会疼？", "prompt": "天气变化会影响慢性疼痛或关节炎症状吗？有哪些证据限制和日常应对建议？"},
        ],
        "evidence_snapshot": [
            {"情况": "热浪中有心血管病、糖尿病或肾病", "可以理解为": "天气可能增加身体负担，需要更留意补水、血压、血糖、尿量和用药保存。", "不要误解为": "不是说天气能单独诊断病情或决定改药。"},
            {"情况": "雾霾或烟雾天有哮喘/COPD", "可以理解为": "污染可能让咳嗽、喘息和活动耐量变差，需要按医嘱执行行动计划。", "不要误解为": "不能替代急性加重评估或血氧检查。"},
            {"情况": "天气变化后疼痛或关节不舒服", "可以理解为": "可以记录疼痛、晨僵、肿胀、睡眠和活动量，带给医生讨论。", "不要误解为": "天气敏感不等于疾病活动度，也不能排除感染或损伤。"},
        ],
    },
    "en": {
        "page_title": "Public Health Assistant - Weather and Common Chronic Disease",
        "language_label": "Page language",
        "hero": {
            "title": "Weather and Chronic Disease Health Assistant",
            "subtitle": "A practical public page explaining how heat, cold, air pollution, humidity, and weather variability may matter for cardiovascular disease, respiratory disease, diabetes, kidney disease, chronic pain, and arthritis.",
            "eyebrow": "Public explanation and care boundaries",
            "pills": ["Plain language", "Chronic disease risk", "Symptom notes", "Care signals", "Not medical advice"],
        },
        "sections": {
            "value": ("What this page helps with", "Start with usable chronic-disease explanations and action boundaries, then continue through question answering."),
            "self_check": ("Self-check and care boundaries", "This is not a diagnostic checklist; it helps people describe symptoms clearly and know when to seek care."),
            "visit_note": ("Visit Note", "Turn vague discomfort into three sentences a clinician can understand quickly."),
            "quick": ("Quick Questions", "Choose a common question and the system will send it directly."),
            "snapshot": ("How To Interpret This", "Translate weather information into daily observation, clinician communication, and safety boundaries."),
        },
        "metrics": [
            {"label": "Common scenarios", "value": "3", "detail": "heat, pollution, cold/humidity"},
            {"label": "Conditions covered", "value": "6", "detail": "heart, lung, kidney, metabolic, pain, arthritis"},
            {"label": "Main action", "value": "Track", "detail": "symptoms, exposure, medication context"},
            {"label": "Safety boundary", "value": "Red flags", "detail": "chest pain, severe dyspnea, fainting"},
        ],
        "cards": [
            {
                "tag": "Everyday explanation",
                "title": "Weather and environmental changes may influence chronic disease symptoms, but they do not prove disease worsening by themselves.",
                "statement": "The system connects heat, cold, air pollution, humidity, cardiovascular disease, respiratory disease, diabetes, kidney disease, chronic pain, and arthritis in one evidence network.",
                "meta": [
                    {"label": "Good for", "value": "Questions about heat waves, smog, cold spells, rainy days, humidity, and symptom fluctuation."},
                    {"label": "You receive", "value": "Plain-language explanation, daily observation ideas, and care-seeking boundaries."},
                    {"label": "Not a substitute for", "value": "Diagnosis, medication changes, emergency care, or individual risk prediction."},
                ],
            },
            {
                "tag": "Action boundary",
                "title": "Recording symptoms, exposure context, and medication background is more useful than only saying you feel unwell.",
                "statement": "Track timing, exposure, activity, hydration, sleep, medication, and accompanying symptoms so a visit can start with clearer information.",
                "meta": [
                    {"label": "Track", "value": "Chest tightness, breathlessness, dizziness, blood pressure/glucose fluctuation, pain score, stiffness, and functional limitation."},
                    {"label": "Seek care urgently for", "value": "Chest pain, severe breathlessness, confusion, fainting, persistent high fever, or rapidly worsening symptoms."},
                    {"label": "Care communication", "value": "Turns public education into structured notes for a clinical visit."},
                ],
            },
        ],
        "self_check_rows": [
            {"Situation": "Heat wave with cardiovascular disease, diabetes, or kidney disease", "First steps": "Avoid peak heat, hydrate, watch urine output and blood pressure/glucose, and check medication storage/use.", "Ask a clinician if": "You use diuretics, blood-pressure medicine, or glucose-lowering medicine, or feel unusually weak or dizzy.", "Watch urgently for": "Chest pain, fainting, confusion, severe dehydration, or breathlessness."},
            {"Situation": "Air pollution or smoke with asthma/COPD", "First steps": "Reduce outdoor activity, follow inhaler plans, and monitor cough, wheeze, and activity tolerance.", "Ask a clinician if": "Symptoms are worse than usual, sleep is interrupted, or rescue medication use increases.", "Watch urgently for": "Difficulty speaking, blue lips, breathlessness at rest, or low oxygen saturation."},
            {"Situation": "Cold/humidity with pain, stiffness, or blood-pressure fluctuation", "First steps": "Keep warm, move gently, record pain and blood pressure, and avoid blaming every change on weather.", "Ask a clinician if": "Pain persists, joints swell, morning stiffness is prolonged, or blood pressure remains abnormal.", "Watch urgently for": "Red hot swollen joints, fever, inability to bear weight, severe headache, or chest tightness."},
        ],
        "visit_note_rows": [
            {"Tell the clinician": "What chronic disease you already have", "Say it clearly": "For example hypertension, coronary disease, asthma/COPD, diabetes, chronic kidney disease, arthritis, or chronic pain.", "Bring if available": "Recent blood pressure/glucose, inhaler or pain-medicine use, diagnoses, and prescriptions."},
            {"Tell the clinician": "When symptoms started", "Say it clearly": "Describe whether symptoms changed after heat, smog, cold, humidity, or sudden weather variation.", "Bring if available": "Dates, pain score, breathlessness, morning stiffness, urine output, sleep, and activity changes."},
            {"Tell the clinician": "Whether red flags occurred", "Say it clearly": "Chest pain, severe breathlessness, fainting, confusion, persistent fever, hot swollen joint, or sudden inability to bear weight.", "Bring if available": "If these occur, do not wait for online explanation; seek timely care."},
        ],
        "pipeline": [
            {"title": "Describe context", "body": "Chronic condition, symptom, weather/pollution exposure, and medication background"},
            {"title": "Find context", "body": "Retrieve related concepts from the chronic-disease evidence base"},
            {"title": "Explain clearly", "body": "Describe association and uncertainty in everyday language"},
            {"title": "Prepare visit", "body": "Organize clinician questions and warning signals"},
        ],
        "workbench": [
            {"title": "What to check today", "body": "Start with whether symptoms changed during heat, pollution, cold, or humid conditions."},
            {"title": "What to note before care", "body": "Record timing, exposure, blood pressure/glucose, pain score, medication, and activity."},
            {"title": "When not to wait", "body": "Chest pain, severe breathlessness, fainting, confusion, or sudden inability to bear weight need timely care."},
        ],
        "sidebar": {
            "title": "How to use",
            "body": "For understanding links among weather, air pollution, and daily management of common chronic diseases.",
            "items": ["What should chronic disease patients do during heat waves?", "What about asthma/COPD on smoggy days?", "Why does weather change pain?", "When should I seek medical care?"],
            "caption": "This assistant is for health education only. Please consult a qualified clinician for diagnosis or treatment.",
        },
        "chat": {"input": "Type your question...", "spinner": "Organizing evidence...", "sources": "Knowledge sources", "boundary": "Evidence boundary assessment", "claim_ledger": "Claim-evidence ledger", "concepts": "Related concepts", "no_knowledge": "No related knowledge was found.", "error": "Sorry, an error occurred while processing your question: ", "clear": "Clear chat history", "study_label": "study mentions"},
        "quick_questions": [
            {"button": "Heat waves and chronic disease", "prompt": "During heat waves, what should people with cardiovascular disease, diabetes, or kidney disease watch for? Explain in plain language."},
            {"button": "Smog and asthma/COPD", "prompt": "How can air pollution or smoke affect asthma and COPD, and what can people observe safely?"},
            {"button": "Why weather changes pain", "prompt": "Can weather changes affect chronic pain or arthritis symptoms? Include evidence limits and safe daily coping ideas."},
        ],
        "evidence_snapshot": [
            {"Situation": "Heat wave with cardiovascular disease, diabetes, or kidney disease", "Means": "Weather may add body stress, so watch hydration, blood pressure, glucose, urine output, and medication storage.", "Does not mean": "Weather alone can diagnose worsening disease or decide medication changes."},
            {"Situation": "Smog or smoke with asthma/COPD", "Means": "Pollution may worsen cough, wheeze, and activity tolerance; follow the clinician-approved action plan.", "Does not mean": "It replaces assessment for acute exacerbation or oxygen status."},
            {"Situation": "Pain or joint symptoms after weather changes", "Means": "Track pain, stiffness, swelling, sleep, and activity for a clearer clinical discussion.", "Does not mean": "Weather sensitivity equals disease activity or excludes infection or injury."},
        ],
    },
}


MEDICAL_TEXT = {
    "zh": {
        "page_title": "临床工作台 - 气候敏感性慢性病",
        "language_label": "页面语言",
        "hero": {
            "title": "气候敏感性慢性病临床工作台",
            "subtitle": "面向医务工作者：把气象暴露、空气污染和常见慢病证据转成门诊沟通、患者教育、随访边界和PMID可追溯材料。",
            "eyebrow": "医务端证据分诊与患者沟通",
            "pills": ["证据摘要", "PMID溯源", "慢病场景", "沟通话术", "红旗症状"],
        },
        "metrics": [
            {"label": "临床场景", "value": "4类", "detail": "热、污染、寒潮、疼痛"},
            {"label": "慢病范围", "value": "6类+", "detail": "心肺肾代谢、疼痛、关节炎"},
            {"label": "安全边界", "value": "红旗", "detail": "急症信号单独提示"},
            {"label": "证据溯源", "value": "PMID", "detail": "可查文献线索"},
        ],
        "sections": {
            "value": ("临床可用场景", "把气候和环境暴露作为慢病症状与服务风险的修饰因素，而不是替代诊断和治疗决策。"),
            "matrix": ("临床转化矩阵", "把图谱关系转成门诊沟通、健康教育和公共卫生管理语言。"),
            "grade": ("证据分诊等级", "按证据成熟度、验证状态和临床可转化性对慢病模块分层。"),
            "triage": ("证据分诊工作台", "先判断模块属于外部文献支架、专家初评可行性样本还是假设生成，再决定如何解释。"),
            "clinical_brief": ("门诊随访记录要点", "把气候暴露变成可记录、可复核、可交接的临床信息。"),
            "translation": ("临床行动转化", "把证据关系转为可沟通、可随访、可审查的临床动作。"),
            "red_flags": ("红旗信号与使用边界", "把普通解释、门诊随访和急症评估边界分开。"),
            "qa": ("临床问答", "输入临床问题后，系统会结合知识图谱和文献线索生成参考答案。"),
            "examples": ("示例问题", "点击后会自动发送到临床问答。"),
            "entity": ("实体与关系查询", "检索慢病类型、气候因素和症状/结局，并查看关系与相关文献。"),
            "stats": ("证据概览", "刷新后查看证据类型、关系和高频主题分布。"),
            "snapshot": ("证据解释矩阵", "把检索信号转成临床解释时保留边界条件。"),
        },
        "cards": [
            {"tag": "门诊沟通", "title": "把气候暴露解释为慢病风险修饰因素，而不是个体诊断依据。", "statement": "医务人员可以用系统快速生成机制线索、证据边界和患者可理解的话术，同时继续按指南评估病情、用药和危险信号。", "meta": [{"label": "适合场景", "value": "热浪、雾霾、寒潮后患者慢病症状波动或就诊担忧。"}, {"label": "输出内容", "value": "机制解释、PMID线索、沟通话术、红旗症状。"}, {"label": "临床边界", "value": "不替代查体、检查、治疗调整和急症处置。"}]},
            {"tag": "科室支持", "title": "把分散文献变成可追溯的实体、关系和文献列表。", "statement": "医生可按暴露、疾病或症状检索关系网络，并查看相关文献线索，用于患者教育、随访模板或科室培训。", "meta": [{"label": "检索对象", "value": "heat wave, air pollution, hypertension, COPD, diabetes, chronic kidney disease, osteoarthritis等。"}, {"label": "证据线索", "value": "实体表、关系表、PMID、年份和标题。"}, {"label": "临床用途", "value": "从问答延伸到可复核的文献证据。"}]},
        ],
        "clinical_matrix": [
            {"场景": "热浪中的心血管病/肾病/糖尿病患者", "证据解释": "高温可与脱水、心肾负荷、血糖波动和医疗服务需求共现。", "临床行动": "核查用药、补水、血压血糖监测、避暑计划和复诊阈值。", "边界": "不根据天气单独调整处方，需结合病情和医嘱。"},
            {"场景": "空气污染或野火烟雾中的哮喘/COPD患者", "证据解释": "污染暴露与呼吸症状加重、急救药使用和就医风险相关。", "临床行动": "确认吸入治疗、行动计划、急性加重识别和随访。", "边界": "暴露指标、个体易感性和诊断状态差异明显。"},
            {"场景": "寒潮后血压升高或胸闷", "证据解释": "寒冷和温度变异可与血压波动和心血管事件风险共现。", "临床行动": "评估血压记录、胸痛/气短、药物依从性和急症信号。", "边界": "天气解释不能延误急性冠脉综合征等评估。"},
            {"场景": "慢性疼痛或关节炎患者诉天气敏感", "证据解释": "专家初评可行性样本显示天气、湿度、气压和疼痛/僵硬存在异质性关联。", "临床行动": "使用症状日记，同时评估炎症、功能、用药和红旗症状。", "边界": "不以天气敏感性替代疾病活动度判断。"},
        ],
        "clinical_brief_rows": [
            {"记录项": "暴露窗口", "门诊问法": "最近是否经历热浪、雾霾/烟雾、寒潮、潮湿或天气突变？", "临床用途": "判断是否需要强化监测或安排短期随访。"},
            {"记录项": "基础慢病与用药", "门诊问法": "是否有心血管病、糖尿病、肾病、哮喘/COPD、慢性疼痛或关节炎？近期用药是否改变？", "临床用途": "区分环境诱发担忧、疾病波动、依从性问题和药物相关风险。"},
            {"记录项": "红旗与功能变化", "门诊问法": "是否有胸痛、静息气短、晕厥、尿量明显减少、血糖/血压异常、关节红肿热痛或不能负重？", "临床用途": "决定门诊教育、加急复诊或急症评估边界。"},
        ],
        "pipeline": [
            {"title": "输入临床问题", "body": "暴露、疾病、症状、用药或随访场景"},
            {"title": "检索证据库", "body": "查找慢病实体、气候因素和症状结局"},
            {"title": "形成解释", "body": "生成证据摘要、机制线索和沟通话术"},
            {"title": "保留溯源", "body": "展示PMID、实体关系和证据边界"},
        ],
        "workbench": [
            {"title": "门诊解释", "body": "将患者对天气/污染的担忧转成谨慎、可执行的沟通。"},
            {"title": "患者教育", "body": "围绕热浪、雾霾、寒潮和极端天气准备慢病教育材料。"},
            {"title": "随访与红旗复核", "body": "围绕血压血糖、呼吸症状、尿量、疼痛功能和急症信号设置复诊边界。"},
        ],
        "sidebar": {"title": "临床工具", "body": "面向医务工作者，保留证据、PMID和解释边界。", "items": ["热浪与心肾代谢风险", "空气污染与呼吸慢病", "寒潮与血压/心血管风险", "天气敏感性疼痛沟通"], "options": "显示选项", "show_pmid": "显示PMID", "show_stats": "显示证据概览", "max_results": "最大检索结果数", "caption": "医务工作者版 v2.0"},
        "tabs": ["证据分诊", "临床问答", "实体查询", "证据概览"],
        "triage": {"info": "推荐临床使用顺序：先看证据等级和验证状态，再看可转化行动，最后确认是否存在急症或超出工具边界。"},
        "red_flag_rows": [
            {"场景": "心血管/心肾代谢风险", "可用于沟通": "热浪、脱水、血压/血糖波动、用药保存和随访阈值。", "立即评估": "胸痛、晕厥、意识混乱、严重呼吸困难、严重脱水或尿量明显减少。", "边界": "不能根据天气单独调整降压药、利尿剂或降糖药。"},
            {"场景": "呼吸慢病风险", "可用于沟通": "污染或烟雾暴露、咳嗽喘息、急救药使用和行动计划。", "立即评估": "静息气短、说话困难、口唇发紫、血氧下降或症状迅速恶化。", "边界": "不能替代肺功能、血氧、影像或急性加重评估。"},
            {"场景": "疼痛/关节炎天气敏感", "可用于沟通": "症状日记、晨僵、肿胀、功能、睡眠、活动量和用药背景。", "立即评估": "红肿热痛、发热、突然不能负重、神经症状或创伤后剧痛。", "边界": "不能用天气敏感性替代疾病活动度或感染鉴别。"},
        ],
        "chat": {"input": "请输入临床问题...", "spinner": "正在检索并生成临床摘要...", "entities": "相关实体", "studies": "相关文献", "relations": "相关关系", "triage": "证据分诊结果", "boundary": "临床边界门控", "claim_ledger": "主张-证据账本", "error": "错误："},
        "examples": [
            {"button": "热浪中的慢病随访", "prompt": "热浪期间，心血管病、糖尿病和慢性肾病患者应如何进行风险沟通和随访？"},
            {"button": "空气污染与COPD", "prompt": "空气污染或烟雾天气对COPD和哮喘患者有什么临床影响？请给出沟通边界。"},
            {"button": "寒潮与高血压", "prompt": "寒潮和温度变异与高血压或缺血性心脏病风险如何关联？临床上该如何解释？"},
            {"button": "天气敏感性关节痛", "prompt": "慢性疼痛或关节炎患者说天气变化就痛，如何用证据谨慎解释？"},
        ],
        "entity_query": {"name": "输入实体名称（如：heat wave, COPD, 糖尿病）", "type": "实体类型", "types": {"全部": None, "ChronicDisease": "ChronicDisease", "ClimateFactor": "ClimateFactor", "Symptom/Outcome": "Symptom", "Arthritis pilot": "ArthritisType"}, "button": "查询实体", "spinner": "正在查询...", "found": "找到 {n} 个实体。", "select": "选择实体查看关系", "relations_of": "“{name}”的相关关系", "related_studies": "相关文献（{n}篇）", "title": "标题", "year": "年份", "relation_fail": "关系加载失败：", "study_fail": "文献加载失败：", "no_results": "未找到结果。", "query_fail": "查询失败：", "no_entity": "请先输入实体名称。"},
        "stats": {"refresh": "刷新证据概览", "spinner": "正在加载证据概览...", "nodes": "证据类型", "relations": "关系类型", "top": "高频主题", "climate": "气候因素 Top 5", "symptom": "症状/结局 Top 5", "arthritis": "慢性病实体 Top 5", "study_suffix": "篇研究", "load_fail": "加载失败：", "fail": "证据概览加载失败："},
        "evidence_snapshot": COMMON_EVIDENCE["zh"],
    },
    "en": {
        "page_title": "Clinical Workbench - Climate-Sensitive Chronic Disease",
        "language_label": "Page language",
        "hero": {"title": "Climate-Sensitive Chronic Disease Workbench", "subtitle": "For health professionals: translate weather exposure, air pollution, and common chronic disease evidence into patient communication, follow-up boundaries, and PMID-traceable materials.", "eyebrow": "Clinical evidence triage and communication", "pills": ["Evidence summary", "PMID trace", "Chronic disease scenarios", "Counseling language", "Warning signs"]},
        "metrics": [
            {"label": "Clinical scenarios", "value": "4", "detail": "heat, pollution, cold, pain"},
            {"label": "Disease scope", "value": "6+", "detail": "heart, lung, kidney, metabolic, pain, arthritis"},
            {"label": "Safety boundary", "value": "Red flags", "detail": "urgent signals separated"},
            {"label": "Evidence trace", "value": "PMID", "detail": "searchable literature clues"},
        ],
        "sections": {"value": ("Clinical use cases", "Treat climate and environmental exposure as a contextual modifier of symptoms and service risk, not as a substitute for diagnosis or treatment decisions."), "matrix": ("Clinical Translation Matrix", "Convert evidence relationships into outpatient communication, health education, and public-health management language."), "grade": ("Evidence Triage Grades", "Stratify chronic-disease modules by evidence maturity, adjudication status, and clinical translatability."), "triage": ("Evidence Triage Workbench", "First identify whether a module is an external-literature scaffold, expert-adjudicated feasibility case, or hypothesis-generating module, then decide how it should be explained."), "clinical_brief": ("Follow-up Documentation Points", "Turn climate exposure into recordable, reviewable, and handoff-ready clinical information."), "translation": ("Clinical Action Translation", "Convert evidence links into communicable, follow-up-ready, and auditable clinical actions."), "red_flags": ("Warning Signals and Use Boundaries", "Separate public explanation, outpatient follow-up, and urgent evaluation boundaries."), "qa": ("Clinical Q&A", "Ask a clinical question and generate an evidence-informed reference answer."), "examples": ("Example Questions", "Click to send one question to the clinical Q&A."), "entity": ("Entity and Relationship Query", "Search chronic disease types, climate factors, and symptoms/outcomes, then inspect relationships and related studies."), "stats": ("Evidence Overview", "Refresh evidence types, relationship types, and high-frequency themes."), "snapshot": ("Evidence Interpretation Matrix", "Preserve interpretation boundaries when turning retrieval signals into clinical language.")},
        "cards": [
            {"tag": "Outpatient communication", "title": "Explain climate exposure as a chronic disease risk modifier, not an individual diagnostic basis.", "statement": "Clinicians can quickly generate mechanism clues, evidence boundaries, and patient-friendly wording while continuing guideline-based assessment.", "meta": [{"label": "Good for", "value": "Heat, smog, or cold-spell concerns after chronic disease symptom fluctuation."}, {"label": "Outputs", "value": "Mechanism clues, PMID traces, counseling language, and warning signs."}, {"label": "Boundary", "value": "Does not replace examination, tests, treatment changes, or emergency care."}]},
            {"tag": "Team support", "title": "Turn scattered literature into traceable entities, relationships, and study lists.", "statement": "Search by exposure, disease, or symptom and inspect related evidence for patient education, follow-up templates, or team training.", "meta": [{"label": "Search targets", "value": "heat wave, air pollution, hypertension, COPD, diabetes, chronic kidney disease, osteoarthritis."}, {"label": "Evidence clues", "value": "Entity tables, relationship tables, PMID, year, and title."}, {"label": "Clinical use", "value": "Extends Q&A into reviewable literature evidence."}]},
        ],
        "clinical_matrix": [
            {"Scenario": "Heat wave in patients with cardiovascular disease, kidney disease, or diabetes", "Evidence interpretation": "Heat may co-occur with dehydration, cardio-renal stress, glycemic fluctuation, and service demand.", "Clinical action": "Review medication, hydration, blood pressure/glucose monitoring, cooling plans, and follow-up thresholds.", "Boundary": "Do not adjust prescriptions based on weather alone."},
            {"Scenario": "Air pollution or wildfire smoke in asthma/COPD", "Evidence interpretation": "Pollution exposure is linked with symptom worsening, rescue medication use, and care-seeking risk.", "Clinical action": "Confirm inhaler plan, exacerbation recognition, action plan, and follow-up.", "Boundary": "Exposure metrics, susceptibility, and diagnostic status vary."},
            {"Scenario": "Cold spell followed by higher blood pressure or chest tightness", "Evidence interpretation": "Cold and temperature variability may co-occur with blood-pressure fluctuation and cardiovascular events.", "Clinical action": "Assess blood pressure logs, chest pain/breathlessness, adherence, and emergency signals.", "Boundary": "Weather explanations must not delay acute coronary evaluation."},
            {"Scenario": "Chronic pain or arthritis patient reports weather sensitivity", "Evidence interpretation": "The expert-adjudicated feasibility case shows heterogeneous links among weather, humidity, pressure, pain, and stiffness.", "Clinical action": "Use symptom diaries while assessing inflammation, function, medications, and red flags.", "Boundary": "Weather sensitivity is not disease activity assessment."},
        ],
        "clinical_brief_rows": [
            {"Item": "Exposure window", "Clinic question": "Recent heat wave, smog/smoke, cold spell, humidity, or sudden weather variation?", "Clinical use": "Decide whether monitoring or short-interval follow-up should be strengthened."},
            {"Item": "Baseline disease and medication", "Clinic question": "Cardiovascular disease, diabetes, kidney disease, asthma/COPD, chronic pain, or arthritis? Any medication change?", "Clinical use": "Separate exposure concern, disease fluctuation, adherence, and medication-related risk."},
            {"Item": "Red flags and function", "Clinic question": "Chest pain, breathlessness at rest, fainting, low urine output, abnormal glucose/BP, hot swollen joint, or inability to bear weight?", "Clinical use": "Set the boundary between education, expedited follow-up, and urgent evaluation."},
        ],
        "pipeline": [{"title": "Enter clinical question", "body": "Exposure, disease, symptom, medication, or follow-up scenario"}, {"title": "Retrieve evidence base", "body": "Find chronic disease entities, climate factors, and symptom outcomes"}, {"title": "Generate explanation", "body": "Produce evidence summary, mechanisms, and counseling wording"}, {"title": "Keep provenance", "body": "Show PMIDs, entity relationships, and interpretation boundaries"}],
        "workbench": [{"title": "Outpatient explanation", "body": "Translate weather or pollution concerns into cautious, usable communication."}, {"title": "Patient education", "body": "Prepare chronic disease material for heat, smog, cold spells, and extreme weather."}, {"title": "Follow-up and red-flag review", "body": "Set follow-up boundaries around blood pressure/glucose, respiratory symptoms, urine output, pain/function, and urgent signals."}],
        "sidebar": {"title": "Clinical tools", "body": "For health professionals; preserves evidence, PMIDs, and interpretation boundaries.", "items": ["Heat and cardio-renal-metabolic risk", "Air pollution and chronic respiratory disease", "Cold spells and blood pressure/cardiovascular risk", "Weather-sensitive pain communication"], "options": "Display options", "show_pmid": "Show PMIDs", "show_stats": "Show evidence overview", "max_results": "Maximum results", "caption": "Medical version v2.0"},
        "tabs": ["Evidence Triage", "Clinical Q&A", "Entity Query", "Evidence Overview"],
        "triage": {"info": "Recommended clinical sequence: review evidence grade and validation status, inspect the translation action, then check urgent signals and tool boundaries."},
        "red_flag_rows": [
            {"Scenario": "Cardio-renal-metabolic risk", "Useful for communication": "Heat, dehydration, blood pressure/glucose fluctuation, medication storage, and follow-up thresholds.", "Evaluate urgently": "Chest pain, fainting, confusion, severe breathlessness, severe dehydration, or markedly reduced urine output.", "Boundary": "Do not adjust antihypertensive, diuretic, or glucose-lowering medication based on weather alone."},
            {"Scenario": "Chronic respiratory risk", "Useful for communication": "Pollution or smoke exposure, cough/wheeze, rescue medication use, and action plans.", "Evaluate urgently": "Breathlessness at rest, difficulty speaking, blue lips, low oxygen saturation, or rapidly worsening symptoms.", "Boundary": "Does not replace spirometry, oxygen assessment, imaging, or acute exacerbation evaluation."},
            {"Scenario": "Weather-sensitive pain/arthritis", "Useful for communication": "Symptom diary, morning stiffness, swelling, function, sleep, activity, and medication context.", "Evaluate urgently": "Red hot swollen joint, fever, sudden inability to bear weight, neurological symptoms, or severe post-traumatic pain.", "Boundary": "Weather sensitivity cannot replace disease activity assessment or infection differential diagnosis."},
        ],
        "chat": {"input": "Enter a clinical question...", "spinner": "Retrieving and generating a clinical summary...", "entities": "Related entities", "studies": "Related studies", "relations": "Related relationships", "triage": "Evidence triage results", "boundary": "Clinical boundary gate", "claim_ledger": "Claim-evidence ledger", "error": "Error: "},
        "examples": [{"button": "Heat-wave chronic disease follow-up", "prompt": "During heat waves, how should clinicians communicate risk and follow-up boundaries for cardiovascular disease, diabetes, and chronic kidney disease?"}, {"button": "Air pollution and COPD", "prompt": "What clinical impact can air pollution or smoke have on COPD and asthma patients? Include communication boundaries."}, {"button": "Cold spell and hypertension", "prompt": "How are cold spells and temperature variability related to hypertension or ischemic heart disease risk, and how should clinicians explain this?"}, {"button": "Weather-sensitive joint pain", "prompt": "How should clinicians explain weather-sensitive chronic pain or arthritis symptoms cautiously using evidence?"}],
        "entity_query": {"name": "Entity name, e.g., heat wave, COPD, diabetes", "type": "Entity type", "types": {"All": None, "ChronicDisease": "ChronicDisease", "ClimateFactor": "ClimateFactor", "Symptom/Outcome": "Symptom", "Arthritis pilot": "ArthritisType"}, "button": "Query entity", "spinner": "Querying...", "found": "Found {n} entities.", "select": "Select an entity to inspect relationships", "relations_of": "Relationships of '{name}'", "related_studies": "Related studies ({n})", "title": "Title", "year": "Year", "relation_fail": "Relationship loading failed: ", "study_fail": "Study loading failed: ", "no_results": "No results found.", "query_fail": "Query failed: ", "no_entity": "Please enter an entity name first."},
        "stats": {"refresh": "Refresh evidence overview", "spinner": "Loading evidence overview...", "nodes": "Evidence types", "relations": "Relationship types", "top": "Top themes", "climate": "Climate factors Top 5", "symptom": "Symptoms/outcomes Top 5", "arthritis": "Chronic disease entities Top 5", "study_suffix": "studies", "load_fail": "Loading failed: ", "fail": "Evidence overview loading failed: "},
        "evidence_snapshot": COMMON_EVIDENCE["en"],
    },
}


RESEARCH_TEXT = {
    "zh": {
        "page_title": "科研工作台 - 气候敏感性慢性病证据分析",
        "language_label": "页面语言",
        "hero": {"title": "气候-慢性病科研工作台", "subtitle": "面向科研人员：用近20年文献证据、研究热点、证据缺口、假设库和可导出数据支持气候敏感性慢病研究选题与分析。", "eyebrow": "科研证据检索与分析工作台", "pills": ["文献证据", "慢病扩展", "质量审计", "假设库", "数据导出"]},
        "sections": {"value": ("科研使用场景", "服务研究问题形成、证据检索、热点/缺口分析、研究设计和数据导出。"), "research_path": ("研究分析路径", "把页面输出对应到选题、证据整理、数据导出和后续研究设计。"), "intelligence": ("科研证据情报", "聚焦研究者需要的高频主题、机制簇、新兴暴露、假设和可导出证据。"), "hypotheses": ("研究假设库", "把证据关系转成可进一步验证的暴露、人群、设计和公共卫生价值。"), "readiness": ("研究就绪度分层", "区分专家初评可行性样本、外部文献支架和仍需疾病专门验证的假设模块。"), "triage": ("证据分诊层", "把暴露-疾病-结局链转成证据等级、验证状态和研究下一步。"), "qa": ("科研问答", "输入科研问题，并保留检索细节用于复核、比较和导出。"), "examples": ("示例科研问题", "点击后生成科研向回答。"), "advanced": ("高级实体查询", "检索实体、路径、共现模式和中心子图。"), "analysis": ("研究热点与证据缺口", "用图谱统计发现高频主题和低支持方向。"), "cypher": ("只读Cypher控制台", "运行安全只读Cypher语句，查看结构并提取研究数据。"), "export": ("数据导出", "按统计、实体、关系或研究列表生成可下载结果。"), "governance": ("证据库质量审计", "检查结构、溯源覆盖、实体标准化和关系支持度。"), "scope": ("近20年文献范围", "默认PubMed窗口为2006-01-01至当前日期，实时更新也限制在同一窗口。"), "schema": ("图谱结构", "查看节点类型、关系类型和支持强度。"), "rationale": ("质量逻辑", "证据库同时保留标准实体、证据断言和关系级支持，便于排序与复核。"), "live": ("更新状态", "查看PubMed增量检索、证据追加和质量审计状态。")},
        "original_cards": [
            {"tag": "研究入口", "title": "从暴露、慢病类别、症状/结局和文献线索开始形成研究问题。", "statement": "研究者可先看高频主题与低支持链接，再进入实体检索、路径查询、共现分析和数据导出。", "meta": [{"label": "可检索对象", "value": "热浪、空气污染、寒潮、心血管病、COPD、糖尿病、肾病、关节炎等。"}, {"label": "可分析内容", "value": "热点主题、证据缺口、共现实体、暴露-疾病-结局链。"}, {"label": "可导出数据", "value": "实体、关系、研究列表、统计、JSON和CSV。"}]},
            {"tag": "研究工具", "title": "研究页服务检索、比较、假设生成、证据缺口和导出。", "statement": "页面保留高级检索、共现、路径、只读Cypher、导出和质量审计，减少与公众端、医务端无关的说明。", "meta": [{"label": "主题", "value": "热浪-心肾代谢、污染-呼吸/心血管、寒潮-血压、天气波动-疼痛。"}, {"label": "可用设计", "value": "DLNM、病例交叉、时间序列、症状日记、医保/门诊数据链接。"}, {"label": "输出", "value": "证据表、关系表、研究清单、热点和缺口。"}]},
        ],
        "research_path_rows": [
            {"研究任务": "形成研究问题", "页面输出": "近20年PubMed窗口、暴露类别、慢病类别、症状/结局和高频实体。", "可导出材料": "检索范围、实体表、主题统计和候选问题。"},
            {"研究任务": "比较证据强弱", "页面输出": "证据分诊层、研究就绪度、关系支持数量和低支持方向。", "可导出材料": "证据分诊表、研究就绪表、关系表和缺口清单。"},
            {"研究任务": "准备后续研究", "页面输出": "假设库、研究设计建议、共现分析、路径查询和质量审计结果。", "可导出材料": "假设表、研究列表、JSON/CSV和质量审计摘要。"},
        ],
        "intelligence_cards": [
            {"tag": "高频慢病信号", "title": "热浪把主题从症状解释推进到心肾代谢风险和卫生服务准备。", "statement": "图谱可连接热暴露、心血管病、肾病、糖尿病、脱水、住院和用药安全，适合公共卫生预警和服务韧性研究。", "meta": [{"label": "暴露变量", "value": "热浪、极端高温、温度变异。"}, {"label": "结局变量", "value": "住院、急诊、血压/血糖波动、肾脏压力、用药安全。"}, {"label": "推荐设计", "value": "时间分层病例交叉或DLNM。"}]},
            {"tag": "成熟暴露簇", "title": "空气污染和野火烟雾连接呼吸慢病与心血管事件。", "statement": "污染暴露、COPD、哮喘、心血管病、急性加重和住院构成清晰的可检索证据链。", "meta": [{"label": "暴露变量", "value": "PM2.5、PM10、臭氧、烟雾、复合高温。"}, {"label": "结局变量", "value": "COPD/哮喘急性加重、救援用药、门急诊和心血管事件。"}, {"label": "推荐设计", "value": "多污染物时间序列或病例交叉，加交互项。"}]},
            {"tag": "可行性样本", "title": "天气敏感性疼痛和关节炎是当前经过专家初评的可行性样本。", "statement": "这部分保留了近20年气候-关节炎抽取结果和双专家初步判读，可作为方法学可行性证据。", "meta": [{"label": "初评数据", "value": "1,249篇摘要抽取和50条关系双专家初评。"}, {"label": "关键不确定性", "value": "方向、滞后、疾病活动度和主观疼痛混杂。"}, {"label": "推荐设计", "value": "重复症状日记链接本地气象暴露。"}]},
        ],
        "hypothesis_rows": [
            {"假设": "热浪与心衰、慢性肾病和糖尿病相关医疗利用增加有关。", "人群": "医保、门急诊或住院记录中的慢病患者", "设计": "时间分层病例交叉或分布滞后非线性模型", "价值": "服务气候适应和慢病随访策略。"},
            {"假设": "空气污染和高温共同增加COPD/哮喘急性加重风险。", "人群": "呼吸慢病门急诊或药房数据", "设计": "多污染物时间序列或病例交叉，加交互项", "价值": "支持污染-气象复合预警。"},
            {"假设": "寒潮和温度变异与高血压控制不稳及心血管就诊相关。", "人群": "有连续血压或就诊记录的中老年慢病患者", "设计": "自我对照病例序列或DLNM", "价值": "把天气预警转化为随访窗口。"},
            {"假设": "天气波动比平均温度更能解释慢性疼痛或关节炎次日症状变化。", "人群": "有重复症状记录的慢性疼痛/关节炎队列", "设计": "症状日记联合本地气象暴露", "价值": "延续可行性样本，形成可检验的机制问题。"},
        ],
        "pipeline": [{"title": "界定问题", "body": "暴露、慢病类别、结局和人群"}, {"title": "检索证据", "body": "近20年PubMed范围和图谱关系"}, {"title": "分析缺口", "body": "热点、弱链接、慢病类别和症状结局"}, {"title": "导出结果", "body": "PMID、Cypher、统计和证据表"}],
        "workbench": [{"title": "研究结果整理", "body": "按暴露、疾病、结局、支持强度和文献来源整理可复核结果。"}, {"title": "证据缺口发现", "body": "发现低研究支持的气候因素、慢病类别和症状/结局。"}, {"title": "可复用研究输出", "body": "导出图谱统计、实体列表、关系列表和研究表，用于图表、补充材料和分析记录。"}],
        "sidebar": {"title": "科研工具", "body": "研究页只保留科研相关功能：检索、分析、导出、质量审计和假设生成。", "items": ["热点和证据缺口分析", "实体/路径/共现查询", "只读Cypher和JSON/CSV导出", "证据来源与质量审计"], "options": "查询设置", "max_results": "最大结果数", "include_studies": "包含文献详情", "export_format": "导出格式", "caption": "研究者版 v2.0"},
        "tabs": ["问答", "高级查询", "研究分析", "Cypher", "导出", "质量审计"],
        "qa": {"input": "请输入科研问题...", "spinner": "正在分析...", "details": "检索详情", "entities": "检索实体", "relations": "检索关系", "studies": "相关文献", "triage": "证据分诊模块", "boundary": "研究边界判断", "claim_ledger": "主张-证据账本", "study_list": "文献列表", "error": "错误："},
        "examples": [{"button": "总结慢病研究热点", "prompt": "基于2006-2026知识图谱和文献证据，总结气候敏感性常见慢病研究热点，并列出代表性证据、PMID和机制。"}, {"button": "发现低支持链接", "prompt": "识别低证据支持的气候因素、慢病类别、症状或机制，并提出3-5个可操作研究问题。"}, {"button": "比较慢病类别", "prompt": "比较心血管、呼吸、糖尿病、肾病和关节炎在气候敏感性方面的证据特点和公共卫生意义。"}, {"button": "导出证据表", "prompt": "请根据当前证据库整理一份可导出的研究证据表，包含暴露、疾病类别、结局、证据强度、PMID和可用研究设计。"}],
        "advanced": {"query_type": "查询类型", "types": {"实体检索": "entity", "路径查询": "path", "共现分析": "cooccurrence", "子图提取": "subgraph"}, "entity_name": "实体名称", "search": "检索", "source": "源实体", "target": "目标实体", "max_path": "最大路径长度", "find_path": "查找路径", "path": "路径 {i}（长度：{n}）", "relations": "关系：{items}", "min_studies": "最少共同研究数", "analyze": "分析", "cooccur": "与“{entity}”共现的实体：", "center": "中心实体", "depth": "子图深度", "extract": "提取子图", "extracted": "已提取 {nodes} 个节点和 {rels} 条关系。", "nodes": "节点", "relationships": "关系", "no_results": "未找到结果。", "no_path": "未找到路径。", "no_cooccur": "未找到共现实体。", "no_subgraph": "未找到子图。", "failed": "查询失败：", "analysis_failed": "分析失败：", "extract_failed": "提取失败："},
        "analysis": {"type": "分析类型", "types": {"热点分析": "hotspot", "证据缺口": "gaps", "关系分布": "relations"}, "hotspots": "研究热点", "climate": "气候因素 Top 10", "arthritis": "慢性病实体 Top 10", "symptoms": "症状/结局 Top 10", "gap_title": "证据缺口检测", "gap_info": "识别低研究支持方向，并生成潜在研究选题。", "entity_type": "实体类型", "detect": "检测缺口", "detected": "检测到 {n} 个低支持 {kind} 实体。", "suggestions": "研究建议：", "supporting": "{n} 篇支持研究", "no_gaps": "演示视图中未检测到低支持实体。", "relationship_title": "关系类型分布", "inspect_entity": "查看某一实体的关系分布", "query": "查询"},
        "cypher": {"info": "高级功能：执行只读Cypher语句。", "preset": "预设查询", "custom": "自定义", "presets": {"全部节点计数": "All node counts", "全部关系计数": "All relationship counts", "高连接实体": "Highly connected entities", "近期研究": "Recent studies"}, "input": "Cypher查询", "run": "运行", "example": "示例：MATCH (n:ChronicDisease) RETURN n.name LIMIT 10", "spinner": "正在运行查询...", "returned": "返回 {n} 行。", "download_json": "下载JSON", "download_csv": "下载CSV", "none": "无查询结果。", "failed": "查询失败："},
        "export": {"type": "导出类型", "types": {"图谱统计": "stats", "实体列表": "entities", "关系列表": "relationships", "研究列表": "studies"}, "button": "生成导出数据", "spinner": "正在生成...", "success": "导出数据已生成。", "download": "下载数据", "preview": "数据预览", "failed": "生成失败："},
        "governance": {"assertions": "证据断言", "assertions_pmid": "有PMID的断言", "missing_ids": "缺少ID的实体", "missing_pmids": "缺少PMID的边", "window": "发表窗口", "covered_years": "覆盖年份", "candidates": "PubMed候选记录", "gain": "候选增量", "year_coverage": "研究图谱年度覆盖", "scope_source": "来源：{source} | 窗口：{start} 至 {end} | 标签：{label}", "node_schema": "节点结构", "relationship_schema": "关系结构", "no_node": "暂无节点结构统计。", "no_rel": "暂无关系结构统计。", "rationale_cards": [{"title": "标准实体", "body": "每个实体包含entity_id和canonical_name，用于减少命名变体造成的重复。"}, {"title": "证据断言", "body": "每条抽取关系可生成EvidenceAssertion节点，并连接来源PMID以便审计。"}, {"title": "支持加权边", "body": "直接边保留support_count、pmids、evidence_tier和latest_evidence，用于排序和质量审计。"}], "tracked": "已追踪PMID", "last_status": "上次运行状态", "live_state": "实时状态", "enabled": "已启用", "not_initialized": "未初始化", "last_success": "上次成功更新：{value}", "failed": "KG治理信息加载失败："},
        "empty_bar": "暂无足够数据生成排序图。",
        "evidence_snapshot": COMMON_EVIDENCE["zh"],
    },
    "en": {
        "page_title": "Research Studio - Climate-Sensitive Chronic Disease Evidence Analysis",
        "language_label": "Page language",
        "hero": {"title": "Climate-Chronic Disease Research Studio", "subtitle": "A research-facing workbench using near-20-year literature evidence, hotspots, evidence gaps, hypothesis banks, and exportable data for climate-sensitive chronic disease topic development and analysis.", "eyebrow": "Research evidence retrieval and analysis workbench", "pills": ["Literature evidence", "Chronic disease expansion", "Quality audit", "Hypothesis bank", "Data export"]},
        "sections": {"value": ("Research Use Cases", "Supports question framing, evidence retrieval, hotspot/gap analysis, study design, and data export."), "research_path": ("Research Analysis Pathway", "Map interface outputs to topic development, evidence organization, data export, and follow-up study planning."), "intelligence": ("Research Evidence Intelligence", "Focuses on what researchers need: high-frequency themes, mechanism clusters, emerging exposures, hypotheses, and exportable evidence."), "hypotheses": ("Research Hypothesis Bank", "Converts evidence relationships into testable exposure, population, design, and public-health value statements."), "readiness": ("Research Readiness Stratification", "Separates expert-adjudicated feasibility cases, external-literature scaffolds, and hypothesis modules requiring disease-specific validation."), "triage": ("Evidence Triage Layer", "Turns exposure-disease-outcome chains into evidence grade, validation status, and next research design."), "qa": ("Research Q&A", "Ask a research question and preserve retrieval details for checking, comparison, and export."), "examples": ("Example Research Prompts", "Click one prompt to generate a research-oriented answer."), "advanced": ("Advanced Entity Query", "Search entities, paths, co-occurrence patterns, and centered subgraphs."), "analysis": ("Research Hotspots and Evidence Gaps", "Use graph statistics to identify high-frequency themes and low-support directions."), "cypher": ("Read-only Cypher Console", "Run safe read-only Cypher queries to inspect structure and extract research data."), "export": ("Data Export", "Generate downloadable outputs by statistics, entities, relationships, or studies."), "governance": ("Evidence-Base Quality Audit", "Inspect structure, provenance coverage, entity normalization, and relationship support."), "scope": ("Near-20-Year Literature Scope", "In this submission package, the default PubMed retrieval window spans publications from 2006-01-01 to 2026-05-24, with live updates constrained to the same publication window."), "schema": ("Graph Schema", "Inspect node types, relationship types, and support strength."), "rationale": ("Quality Logic", "The evidence base retains canonical entities, evidence assertions, and relationship-level support for ranking and checking."), "live": ("Update Status", "Inspect incremental PubMed retrieval, evidence append, and quality-audit status.")},
        "original_cards": [{"tag": "Research entry", "title": "Start research questions from exposure, disease category, symptom/outcome, and literature clues.", "statement": "Researchers can first inspect high-frequency themes and low-support links, then move to entity search, path query, co-occurrence analysis, and data export.", "meta": [{"label": "Search targets", "value": "Heat waves, air pollution, cold spells, cardiovascular disease, COPD, diabetes, kidney disease, arthritis."}, {"label": "Analytic content", "value": "Hotspots, evidence gaps, co-occurring entities, and exposure-disease-outcome chains."}, {"label": "Exportable data", "value": "Entities, relationships, study lists, statistics, JSON, and CSV."}]}, {"tag": "Research tools", "title": "The research page serves retrieval, comparison, hypothesis generation, evidence gaps, and export.", "statement": "The interface keeps advanced search, co-occurrence, paths, read-only Cypher, export, and quality audit while reducing content unrelated to researchers.", "meta": [{"label": "Topics", "value": "Heat-cardio-renal-metabolic risk, pollution-respiratory/cardiovascular risk, cold-blood pressure, weather-pain."}, {"label": "Usable designs", "value": "DLNM, case-crossover, time series, symptom diaries, claims/outpatient linkage."}, {"label": "Outputs", "value": "Evidence tables, relationship tables, study lists, hotspots, and gaps."}]}],
        "research_path_rows": [
            {"Research task": "Frame a research question", "Interface output": "Near-20-year PubMed window, exposure categories, disease categories, symptoms/outcomes, and high-frequency entities.", "Exportable material": "Search scope, entity table, theme statistics, and candidate questions."},
            {"Research task": "Compare evidence strength", "Interface output": "Evidence triage layer, research readiness, relationship support counts, and low-support directions.", "Exportable material": "Evidence triage table, readiness table, relationship table, and gap list."},
            {"Research task": "Plan follow-up study", "Interface output": "Hypothesis bank, design suggestions, co-occurrence analysis, path query, and quality-audit results.", "Exportable material": "Hypothesis table, study list, JSON/CSV, and quality-audit summary."},
        ],
        "intelligence_cards": [{"tag": "High-frequency chronic disease signal", "title": "Heat moves the topic from symptom explanation to cardio-renal-metabolic risk and service preparedness.", "statement": "The graph can connect heat exposure, cardiovascular disease, kidney disease, diabetes, dehydration, admissions, and medication safety, supporting warning and service-resilience studies.", "meta": [{"label": "Exposure variables", "value": "Heat wave, extreme heat, and temperature variability."}, {"label": "Outcome variables", "value": "Admission, emergency visit, blood pressure/glucose instability, renal stress, and medication safety."}, {"label": "Recommended design", "value": "Time-stratified case-crossover or distributed-lag non-linear model."}]}, {"tag": "Mature exposure cluster", "title": "Air pollution and wildfire smoke connect chronic respiratory disease with cardiovascular events.", "statement": "Pollution exposure, COPD, asthma, cardiovascular disease, exacerbation, and admission form a clear evidence chain for retrieval.", "meta": [{"label": "Exposure variables", "value": "PM2.5, PM10, ozone, smoke, and compound heat."}, {"label": "Outcome variables", "value": "COPD/asthma exacerbation, rescue medication, emergency visits, and cardiovascular events."}, {"label": "Recommended design", "value": "Multi-pollutant time series or case-crossover with interaction terms."}]}, {"tag": "Feasibility case", "title": "Weather-sensitive pain and arthritis are the current expert-adjudicated feasibility sample.", "statement": "This module retains the near-20-year climate-arthritis extraction outputs and preliminary dual-expert adjudication, serving as feasibility evidence for extending to other chronic diseases.", "meta": [{"label": "Adjudicated sample", "value": "1,249 abstract extractions and dual-expert review of 50 relationships."}, {"label": "Key uncertainty", "value": "Direction, lag, disease activity, and subjective pain confounding."}, {"label": "Recommended design", "value": "Repeated symptom diary linked with local meteorological exposure."}]}],
        "hypothesis_rows": [{"Hypothesis": "Heat waves are associated with increased health-service utilization among patients with heart failure, chronic kidney disease, and diabetes.", "Population": "Patients in claims, emergency, or inpatient data", "Design": "Time-stratified case-crossover or distributed-lag non-linear model", "Value": "Supports climate adaptation and chronic disease follow-up."}, {"Hypothesis": "Air pollution and high temperature jointly increase COPD/asthma exacerbation risk.", "Population": "Respiratory outpatient, emergency, or pharmacy data", "Design": "Multi-pollutant time series or case-crossover with interaction terms", "Value": "Supports combined pollution-weather warning systems."}, {"Hypothesis": "Cold spells and temperature variability are associated with unstable hypertension control and cardiovascular visits.", "Population": "Older chronic disease patients with blood pressure or visit records", "Design": "Self-controlled case series or DLNM", "Value": "Turns weather alerts into follow-up windows."}, {"Hypothesis": "Weather variability predicts next-day chronic pain or arthritis symptoms more strongly than mean temperature.", "Population": "Chronic pain or arthritis cohorts with repeated symptom records", "Design": "Symptom diary plus local meteorology linkage", "Value": "Extends the feasibility case into a testable mechanism question."}],
        "pipeline": [{"title": "Frame question", "body": "Exposure, chronic disease category, outcome, and population"}, {"title": "Retrieve evidence", "body": "Near-20-year PubMed scope and graph relationships"}, {"title": "Analyze gaps", "body": "Hotspots, weak links, disease categories, and symptom outcomes"}, {"title": "Export results", "body": "PMID, Cypher, statistics, and downloadable evidence tables"}],
        "workbench": [{"title": "Research result organization", "body": "Organize checkable results by exposure, disease, outcome, support strength, and literature source."}, {"title": "Evidence-gap discovery", "body": "Find under-studied climate factors, chronic disease categories, and symptoms/outcomes."}, {"title": "Reusable research outputs", "body": "Export graph statistics, entity lists, relationship lists, and study tables for figures, supplements, and analysis logs."}],
        "sidebar": {"title": "Research tools", "body": "The research page keeps only research-relevant functions: retrieval, analysis, export, quality audit, and hypothesis generation.", "items": ["Hotspot and evidence-gap analysis", "Entity/path/co-occurrence query", "Read-only Cypher and JSON/CSV export", "Evidence provenance and quality audit"], "options": "Query settings", "max_results": "Maximum results", "include_studies": "Include study details", "export_format": "Export format", "caption": "Researcher version v2.0"},
        "tabs": ["Q&A", "Advanced Query", "Research Analysis", "Cypher", "Export", "Quality Audit"],
        "qa": {"input": "Enter a research question...", "spinner": "Analyzing...", "details": "Retrieval details", "entities": "Retrieved entities", "relations": "Retrieved relationships", "studies": "Related studies", "triage": "Evidence triage modules", "boundary": "Research boundary assessment", "claim_ledger": "Claim-evidence ledger", "study_list": "Study list", "error": "Error: "},
        "examples": [{"button": "Summarize chronic disease hotspots", "prompt": "Based on the 2006-2026 knowledge graph and literature evidence, summarize hotspots in climate-sensitive common chronic disease research and list representative evidence, PMIDs, and mechanisms."}, {"button": "Find under-studied links", "prompt": "Identify low-evidence climate factors, chronic disease categories, symptoms, or mechanisms, and propose 3-5 actionable research questions."}, {"button": "Compare chronic disease categories", "prompt": "Compare cardiovascular, respiratory, diabetes, kidney disease, and arthritis evidence patterns in climate sensitivity and public-health relevance."}, {"button": "Export evidence table", "prompt": "Organize an exportable research evidence table with exposure, disease category, outcome, evidence strength, PMID, and usable study design."}],
        "advanced": {"query_type": "Query type", "types": {"Entity search": "entity", "Path query": "path", "Co-occurrence analysis": "cooccurrence", "Subgraph extraction": "subgraph"}, "entity_name": "Entity name", "search": "Search", "source": "Source entity", "target": "Target entity", "max_path": "Maximum path length", "find_path": "Find path", "path": "Path {i} (length: {n})", "relations": "Relations: {items}", "min_studies": "Minimum co-occurring studies", "analyze": "Analyze", "cooccur": "Entities co-occurring with '{entity}':", "center": "Center entity", "depth": "Subgraph depth", "extract": "Extract subgraph", "extracted": "Extracted {nodes} nodes and {rels} relationships.", "nodes": "Nodes", "relationships": "Relationships", "no_results": "No results found.", "no_path": "No path found.", "no_cooccur": "No co-occurring entities found.", "no_subgraph": "No subgraph found.", "failed": "Query failed: ", "analysis_failed": "Analysis failed: ", "extract_failed": "Extraction failed: "},
        "analysis": {"type": "Analysis type", "types": {"Hotspot analysis": "hotspot", "Evidence gaps": "gaps", "Relationship distribution": "relations"}, "hotspots": "Research hotspots", "climate": "Climate factors Top 10", "arthritis": "Chronic disease entities Top 10", "symptoms": "Symptoms/outcomes Top 10", "gap_title": "Evidence-gap detection", "gap_info": "Identify under-studied areas and generate potential research directions.", "entity_type": "Entity type", "detect": "Detect gaps", "detected": "Detected {n} low-support {kind} entities.", "suggestions": "Research suggestions:", "supporting": "{n} supporting studies", "no_gaps": "No low-support entities detected in this demo view.", "relationship_title": "Relationship-type distribution", "inspect_entity": "Inspect relationship distribution for one entity", "query": "Query"},
        "cypher": {"info": "Advanced feature: execute read-only Cypher statements.", "preset": "Preset query", "custom": "Custom", "presets": {"All node counts": "All node counts", "All relationship counts": "All relationship counts", "Highly connected entities": "Highly connected entities", "Recent studies": "Recent studies"}, "input": "Cypher query", "run": "Run", "example": "Example: MATCH (n:ChronicDisease) RETURN n.name LIMIT 10", "spinner": "Running query...", "returned": "Returned {n} rows.", "download_json": "Download JSON", "download_csv": "Download CSV", "none": "No query results.", "failed": "Query failed: "},
        "export": {"type": "Export type", "types": {"Graph statistics": "stats", "Entity list": "entities", "Relationship list": "relationships", "Study list": "studies"}, "button": "Generate export data", "spinner": "Generating...", "success": "Export data generated.", "download": "Download data", "preview": "Data preview", "failed": "Generation failed: "},
        "governance": {"assertions": "Evidence assertions", "assertions_pmid": "Assertions with PMID", "missing_ids": "Entities missing IDs", "missing_pmids": "Edges missing PMID", "window": "Publication window", "covered_years": "Covered years", "candidates": "PubMed candidates", "gain": "Candidate gain", "year_coverage": "Year coverage in the research graph", "scope_source": "Source: {source} | Window: {start} to {end} | Label: {label}", "node_schema": "Node schema", "relationship_schema": "Relationship schema", "no_node": "No node schema statistics available.", "no_rel": "No relationship schema statistics available.", "rationale_cards": [{"title": "Canonical entity", "body": "Each entity has an entity_id and canonical_name to reduce duplicates caused by naming variants."}, {"title": "Evidence assertion", "body": "Each extracted relationship can generate an EvidenceAssertion node linked to source PMIDs for auditability."}, {"title": "Support-weighted edge", "body": "Direct edges retain support_count, pmids, evidence_tier, and latest_evidence for ranking and quality audit."}], "tracked": "Tracked PMIDs", "last_status": "Last run status", "live_state": "Live state", "enabled": "Enabled", "not_initialized": "Not initialized", "last_success": "Last successful update: {value}", "failed": "KG governance information failed to load: "},
        "empty_bar": "Not enough data to render a ranked chart.",
        "evidence_snapshot": COMMON_EVIDENCE["en"],
    },
}


PAGE_TEXT = {
    "public": PUBLIC_TEXT,
    "medical": MEDICAL_TEXT,
    "research": RESEARCH_TEXT,
}


def get_text(page: str, lang: str) -> Dict:
    return PAGE_TEXT[page][lang]
