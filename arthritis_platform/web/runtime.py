"""
Runtime bootstrap helpers for the Streamlit applications.

The apps can run in two modes:
- live mode, backed by Neo4j and DeepSeek;
- local evidence-base mode, backed by deterministic in-memory services.
"""

from __future__ import annotations

import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from arthritis_platform.config import DEEPSEEK_CONFIG, NEO4J_CONFIG, get_missing_platform_settings
from arthritis_platform.services import (
    DemoGraphQueryService,
    DemoLLMService,
    GraphQueryService,
    get_llm_service_class,
    RAGEngine,
)


@dataclass(frozen=True)
class PlatformRuntime:
    rag: RAGEngine
    graph: object
    mode_label: str
    mode_detail: str
    is_demo: bool


def _demo_runtime(reason: str) -> PlatformRuntime:
    graph = DemoGraphQueryService()
    llm = DemoLLMService()
    return PlatformRuntime(
        rag=RAGEngine(graph, llm),
        graph=graph,
        mode_label="Local evidence-base mode",
        mode_detail=reason,
        is_demo=True,
    )


def create_runtime() -> PlatformRuntime:
    """Create the best available runtime without blocking the UI."""
    if os.getenv("PLATFORM_DEMO_MODE", "").strip() == "1":
        return _demo_runtime("Local evidence-base mode was requested through PLATFORM_DEMO_MODE=1.")

    missing = get_missing_platform_settings()
    if missing:
        return _demo_runtime(
            "Live credentials are incomplete, so the app is using the embedded evidence-base dataset."
        )

    llm_service_cls = get_llm_service_class()
    if GraphQueryService is None or llm_service_cls is None:
        return _demo_runtime(
            "Live Python dependencies are not installed, so the app is using the embedded evidence-base dataset."
        )

    try:
        graph = GraphQueryService(**NEO4J_CONFIG)
        # Lightweight connection check. If Neo4j is not reachable, fall back
        # before the user reaches an empty or broken screen.
        graph.get_statistics()
        llm = llm_service_cls(
            api_key=DEEPSEEK_CONFIG["api_key"],
            base_url=DEEPSEEK_CONFIG["base_url"],
            model_name=DEEPSEEK_CONFIG["model_name"],
        )
        return PlatformRuntime(
            rag=RAGEngine(graph, llm),
            graph=graph,
            mode_label="Live Graph-RAG mode",
            mode_detail="Connected to Neo4j and external LLM services.",
            is_demo=False,
        )
    except Exception as exc:
        return _demo_runtime(f"Live services were unavailable: {exc}")


def get_platform_metrics(graph: object) -> List[Dict[str, str]]:
    """Return compact metrics for the top dashboard strip."""
    try:
        stats = graph.get_statistics()
        node_total = sum(int(row.get("count", 0)) for row in stats.get("nodes", []))
        relation_total = sum(int(row.get("count", 0)) for row in stats.get("relations", []))
        climate_count = next(
            (int(row.get("count", 0)) for row in stats.get("nodes", []) if row.get("type") == "ClimateFactor"),
            0,
        )
        chronic_count = next(
            (int(row.get("count", 0)) for row in stats.get("nodes", []) if row.get("type") == "ChronicDisease"),
            0,
        )
        arthritis_count = next(
            (int(row.get("count", 0)) for row in stats.get("nodes", []) if row.get("type") == "ArthritisType"),
            0,
        )
        chronic_count += arthritis_count
    except Exception:
        node_total = relation_total = climate_count = chronic_count = 0
    try:
        coverage = graph.get_temporal_coverage()
        start_year = coverage.get("start_year") or 2006
        end_year = coverage.get("end_year") or "current"
        coverage_value = f"{start_year}-{end_year}"
        coverage_detail = coverage.get("window_label", "near-20-year literature window")
    except Exception:
        coverage_value = "2006-current"
        coverage_detail = "near-20-year literature window"
    try:
        triage_count = len(graph.get_evidence_triage())
    except Exception:
        triage_count = 0

    return [
        {"label": "Evidence nodes", "value": f"{node_total:,}", "detail": "graph concepts"},
        {"label": "Relationships", "value": f"{relation_total:,}", "detail": "traceable links"},
        {"label": "Climate factors", "value": f"{climate_count:,}", "detail": "weather exposures"},
        {"label": "Chronic disease entities", "value": f"{chronic_count:,}", "detail": "common conditions"},
        {"label": "Triage modules", "value": f"{triage_count:,}", "detail": "bounded evidence layers"},
        {"label": "KG time span", "value": coverage_value, "detail": coverage_detail},
        {"label": "Expert validation", "value": "88%", "detail": "graph-usable sample"},
    ]


def get_evidence_snapshot() -> List[Dict[str, str]]:
    """Static evidence snapshot used across interfaces."""
    return [
        {
            "Domain": "Temperature, heat, and chronic disease burden",
            "Signal": "Frequently retrieved",
            "Traceability": "Entity, relation, PMID",
            "Caution": "Association, not individualized prediction",
        },
        {
            "Domain": "Air pollution and respiratory/cardiovascular events",
            "Signal": "Moderate literature density",
            "Traceability": "Entity co-occurrence",
            "Caution": "Exposure windows and endpoints vary",
        },
        {
            "Domain": "Weather variability and chronic pain",
            "Signal": "Emerging gap",
            "Traceability": "Low-count graph nodes",
            "Caution": "Needs targeted epidemiologic study",
        },
    ]


def get_evidence_intelligence_cards() -> List[Dict[str, object]]:
    """Return high-value evidence translations for the first screen."""
    return [
        {
            "tag": "High-frequency signal",
            "title": "Heat, pollution, cold, and weather variability connect climate exposure with common chronic disease burden.",
            "statement": (
                "The graph can connect heat waves, air pollution, cold exposure, cardiovascular disease, respiratory "
                "disease, diabetes, kidney disease, chronic pain, arthritis, and multimorbidity. Its value is not "
                "diagnosis, but evidence-aware risk communication."
            ),
            "meta": [
                {"label": "Public value", "value": "Track symptoms, exposure, hydration, activity, medication context, and warning signs."},
                {"label": "Clinical value", "value": "Frame climate exposure as a contextual risk modifier while preserving standard assessment."},
                {"label": "Research value", "value": "Test lagged and non-linear climate effects using claims, visits, monitoring, or symptom data."},
            ],
        },
        {
            "tag": "Mechanism cluster",
            "title": "The arthritis corpus is a preliminary expert-adjudicated feasibility case, not proof of clinical validity.",
            "statement": (
                "Weather-sensitive pain and arthritis provide the current extraction and dual-expert adjudication "
                "results; the same schema now extends to broader chronic disease categories."
            ),
            "meta": [
                {"label": "Public value", "value": "Explain weather-sensitive symptoms without turning them into diagnosis."},
                {"label": "Clinical value", "value": "Use symptom diaries while still assessing disease activity and comorbidity."},
                {"label": "Research value", "value": "Use the feasibility case as an adjudication pattern for other disease modules."},
            ],
        },
        {
            "tag": "Emerging exposure",
            "title": "Extreme heat, air pollution, and climate change move the topic from symptoms to public health services.",
            "statement": (
                "The expanded KG makes room for heat waves, air pollution, climate change, and functional limitation, "
                "which lets the project speak to adaptation, vulnerable groups, and health-system preparedness."
            ),
            "meta": [
                {"label": "Public value", "value": "Connect heat, dehydration, outdoor activity, medication safety, and care-seeking during extreme weather."},
                {"label": "Clinical value", "value": "Prepare seasonal counseling for older adults and patients with multimorbidity or mobility limits."},
                {"label": "Research value", "value": "Link environmental exposure data with outpatient visits, pain flares, and rehabilitation interruption."},
            ],
        },
        {
            "tag": "Service angle",
            "title": "The strongest platform value is chronic disease evidence translation across roles.",
            "statement": (
                "The platform's practical value is a living, traceable evidence base that turns scattered literature into "
                "public explanations, clinician-ready briefs, and reproducible research leads."
            ),
            "meta": [
                {"label": "Novelty", "value": "Near-20-year PubMed scope plus Graph-RAG and role-specific interfaces."},
                {"label": "Trust", "value": "PMID traces, read-only Cypher, quality audit, and expert validation table."},
                {"label": "Use case", "value": "A digital public-health bridge between evidence retrieval and communication."},
            ],
        },
    ]


def get_clinical_translation_matrix() -> List[Dict[str, str]]:
    """Return a compact clinical/public health translation matrix."""
    return [
        {
            "Scenario": "Patient reports pain before rain or cold weather",
            "KG interpretation": "Weather may modify symptoms in susceptible patients; it does not confirm disease activity by itself.",
            "Clinical action": "Check inflammation, function, medication adherence, activity, sleep, and red flags.",
            "Boundary": "Avoid diagnosing or escalating treatment from weather sensitivity alone.",
        },
        {
            "Scenario": "Older adult with osteoarthritis during a cold spell",
            "KG interpretation": "Cold exposure and temperature variability are plausible symptom modifiers for pain and stiffness.",
            "Clinical action": "Discuss warmth, safe movement, fall prevention, analgesic safety, and timely review if function declines.",
            "Boundary": "Individual response varies; comorbidities and medication risks matter.",
        },
        {
            "Scenario": "Inflammatory arthritis patient reports seasonal flares",
            "KG interpretation": "Seasonal patterns may coexist with immune activity, infection, stress, or care access changes.",
            "Clinical action": "Use symptom diary plus standard disease activity assessment and laboratory or imaging context when needed.",
            "Boundary": "Do not replace treat-to-target assessment with meteorological explanations.",
        },
        {
            "Scenario": "Heat wave limits mobility or rehabilitation",
            "KG interpretation": "Extreme weather can affect function, hydration, activity, and health service needs.",
            "Clinical action": "Plan safer exercise timing, hydration guidance, heat-risk counseling, and follow-up for vulnerable patients.",
            "Boundary": "Evidence is emerging; treat as public-health risk management rather than causal proof.",
        },
    ]


def get_research_hypothesis_bank() -> List[Dict[str, str]]:
    """Return research leads surfaced by the expanded KG story."""
    return [
        {
            "Hypothesis": "Short-term temperature variability predicts next-day joint pain intensity more strongly than mean temperature.",
            "Population": "Osteoarthritis or mixed arthritis cohorts with repeated symptom records",
            "Design": "Distributed-lag non-linear model with local meteorology and within-person controls",
            "Why it matters": "Converts a common patient observation into a testable exposure-response question.",
        },
        {
            "Hypothesis": "Humidity-pressure combinations are associated with stiffness duration among inflammatory arthritis patients.",
            "Population": "Rheumatoid arthritis or psoriatic arthritis clinic cohorts",
            "Design": "Prospective symptom diary plus weather station or gridded exposure linkage",
            "Why it matters": "Targets a heterogeneous but clinically recognizable symptom cluster.",
        },
        {
            "Hypothesis": "Extreme heat episodes reduce rehabilitation adherence and increase functional limitation in older adults with arthritis.",
            "Population": "Older adults with osteoarthritis or multimorbidity",
            "Design": "Interrupted time-series or case-crossover study using heat alerts and rehabilitation attendance",
            "Why it matters": "Moves the topic into climate adaptation and health-service planning.",
        },
        {
            "Hypothesis": "Air pollution and temperature jointly modify arthritis-related outpatient visits or pain medication use.",
            "Population": "Claims, outpatient, or pharmacy datasets with environmental linkage",
            "Design": "Time-stratified case-crossover with interaction terms and sensitivity analyses",
            "Why it matters": "Connects musculoskeletal health to broader environmental public-health surveillance.",
        },
        {
            "Hypothesis": "Role-specific Graph-RAG outputs improve perceived usefulness and evidence comprehension versus generic literature search.",
            "Population": "Public users, clinicians, and graduate researchers",
            "Design": "Small usability validation with task completion, trust, and comprehension endpoints",
            "Why it matters": "Provides a direct digital-health evaluation pathway for the submitted software.",
        },
    ]


def get_public_practical_cards() -> List[Dict[str, object]]:
    """Return public-facing practical guidance cards."""
    return [
        {
            "tag": "日常解释",
            "title": "天气可能影响疼痛感受，但不能单独说明病情加重。",
            "statement": "系统把温度、湿度、气压、疼痛、僵硬和关节炎类型放在同一证据网络中，帮助用户理解“相关”和“诊断”的区别。",
            "meta": [
                {"label": "适合询问", "value": "下雨、降温、潮湿、热浪时疼痛或僵硬为什么会波动。"},
                {"label": "能得到", "value": "通俗解释、日常观察建议、就医边界。"},
                {"label": "不能替代", "value": "医生诊断、用药调整、疾病活动度判断。"},
            ],
        },
        {
            "tag": "行动边界",
            "title": "把症状记录下来，比只说“天气一变就疼”更有用。",
            "statement": "建议记录疼痛部位、持续时间、天气变化、活动量、睡眠、用药和伴随症状，为就诊沟通提供线索。",
            "meta": [
                {"label": "记录重点", "value": "疼痛评分、晨僵时间、肿胀、发热、活动受限。"},
                {"label": "就医提示", "value": "持续肿胀、明显发热、红肿热痛、无法负重或症状快速加重。"},
                {"label": "就医沟通", "value": "把科普问答变成可带去就诊的健康记录。"},
            ],
        },
    ]


def get_public_self_check_guide() -> List[Dict[str, str]]:
    """Return a public-facing self-check and care-boundary guide."""
    return [
        {
            "使用场景": "天气变化后关节疼痛加重",
            "可以先做": "记录疼痛、保暖或避暑、保持温和活动、观察是否与睡眠和活动量有关。",
            "建议询问医生": "疼痛持续不缓解、影响走路或工作、反复需要止痛药。",
            "需要警惕": "关节明显红肿热痛、发热、外伤后疼痛、突然不能负重。",
        },
        {
            "使用场景": "晨僵或关节僵硬变明显",
            "可以先做": "记录晨僵持续时间、受累关节、天气和活动情况。",
            "建议询问医生": "晨僵超过30-60分钟、伴肿胀或多个关节受累。",
            "需要警惕": "怀疑炎症性关节炎或原有病情突然变化。",
        },
        {
            "使用场景": "热浪或高温期间活动减少",
            "可以先做": "避开高温时段运动、补水、选择室内低冲击活动。",
            "建议询问医生": "合并心血管病、肾病、长期用药或行动明显受限。",
            "需要警惕": "头晕、脱水、胸闷、跌倒风险增加。",
        },
    ]


def get_medical_workflow_cards() -> List[Dict[str, object]]:
    """Return clinical workflow cards for medical users."""
    return [
        {
            "tag": "门诊沟通",
            "title": "把天气敏感性解释为症状修饰因素，而不是诊断依据。",
            "statement": "医务人员可以用系统快速生成机制线索、证据边界和患者可理解的话术，同时继续按标准流程评估炎症、功能和危险信号。",
            "meta": [
                {"label": "适合场景", "value": "患者反复提到降温、潮湿、气压变化与疼痛波动。"},
                {"label": "输出内容", "value": "机制解释、PMID线索、沟通话术、红旗症状。"},
                {"label": "临床边界", "value": "不替代查体、实验室、影像和疾病活动度评估。"},
            ],
        },
        {
            "tag": "科室支持",
            "title": "把分散文献变成可追溯的实体、关系和文献列表。",
            "statement": "医生可按气候因素、关节炎类型或症状检索关系网络，并查看相关文献线索，用于患者教育、随访模板或科室培训。",
            "meta": [
                {"label": "检索对象", "value": "temperature, humidity, barometric pressure, osteoarthritis, rheumatoid arthritis等。"},
                {"label": "证据线索", "value": "实体表、关系表、PMID、年份和标题。"},
                {"label": "临床用途", "value": "从问答延伸到可复核的文献证据。"},
            ],
        },
    ]


def get_research_original_research_cards() -> List[Dict[str, object]]:
    """Return research-facing cards for evidence analysis and hypothesis generation."""
    return [
        {
            "tag": "研究入口",
            "title": "从暴露、疾病、症状/结局和文献线索开始形成研究问题。",
            "statement": "研究者可先看高频主题与低支持链接，再进入实体检索、路径查询、共现分析和数据导出。",
            "meta": [
                {"label": "可检索对象", "value": "热浪、空气污染、寒潮、心血管病、COPD、糖尿病、肾病、关节炎等。"},
                {"label": "可分析内容", "value": "热点主题、证据缺口、共现实体、暴露-疾病-结局链。"},
                {"label": "可导出数据", "value": "实体、关系、研究列表、统计、JSON和CSV。"},
            ],
        },
        {
            "tag": "科研实用性",
            "title": "科研端要服务选题、假设生成、证据缺口和可导出结果。",
            "statement": "研究者页面保留高级检索、共现、路径、只读Cypher、数据导出和KG治理，不再混入公众或审稿人说明板。",
            "meta": [
                {"label": "选题", "value": "温度波动、湿度-气压组合、热浪、空气污染、功能受限。"},
                {"label": "方法", "value": "DLNM、病例交叉、前瞻性日记、门诊/康复数据链接。"},
                {"label": "输出", "value": "实体、关系、研究列表、统计结果和JSON/CSV。"},
            ],
        },
    ]


def get_live_update_status(state_file: str = "data/live_updates/live_update_state.json") -> Dict[str, object]:
    """Read the live-update state file for display in the research interface."""
    path = Path(state_file)
    if not path.exists():
        return {
            "enabled": False,
            "last_success_at": "Not initialized",
            "seen_pmids": 0,
            "last_run_status": "No runs yet",
            "last_manifest": "",
        }

    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "enabled": False,
            "last_success_at": "State file unreadable",
            "seen_pmids": 0,
            "last_run_status": "Error",
            "last_manifest": str(path),
        }

    runs = state.get("runs", [])
    last_run = runs[-1] if runs else {}
    return {
        "enabled": True,
        "last_success_at": state.get("last_success_at") or "No successful run",
        "seen_pmids": len(state.get("seen_pmids", [])),
        "last_run_status": last_run.get("status", "No runs yet"),
        "last_manifest": last_run.get("manifest_file", ""),
    }
