"""
实体关系Schema定义
定义知识图谱中的实体类型和关系类型
"""

# 实体类型定义
ENTITY_TYPES = {
    "ChronicDisease": {
        "name": "常见慢性病",
        "description": "气候敏感性常见慢性病和多病共存类别",
        "examples": [
            "Cardiovascular Disease (心血管病)",
            "Hypertension (高血压)",
            "Chronic Obstructive Pulmonary Disease (慢阻肺)",
            "Asthma (哮喘)",
            "Diabetes (糖尿病)",
            "Chronic Kidney Disease (慢性肾病)",
            "Chronic Mental Health Conditions (慢性心理健康问题)",
            "Osteoarthritis (骨关节炎)"
        ]
    },
    "ArthritisType": {
        "name": "关节炎类型",
        "description": "关节炎pilot模块中的疾病类型",
        "examples": [
            "Osteoarthritis (骨关节炎)",
            "Rheumatoid Arthritis (类风湿关节炎)",
            "Gouty Arthritis (痛风性关节炎)",
            "Psoriatic Arthritis (银屑病关节炎)",
            "Inflammatory Arthritis (炎症性关节炎)"
        ]
    },
    "ClimateFactor": {
        "name": "气候因素",
        "description": "可能影响常见慢性病风险、症状或医疗服务利用的气候和气象因素",
        "examples": [
            "Temperature (温度)",
            "Humidity (湿度)",
            "Barometric Pressure (气压)",
            "Atmospheric Pressure (大气压)",
            "Precipitation (降水)",
            "Wind Speed (风速)",
            "Season (季节)",
            "Weather Pattern (天气模式)",
            "Cold Exposure (寒冷暴露)",
            "Heat Wave (热浪)",
            "Extreme Heat (极端高温)",
            "Air Pollution (空气污染)",
            "Wildfire Smoke (野火烟雾)",
            "Flooding (洪水)",
            "Climate Change (气候变化)"
        ]
    },
    "Symptom": {
        "name": "症状或结局",
        "description": "慢性病相关症状、急性加重、医疗服务利用或功能结局",
        "examples": [
            "Pain (疼痛)",
            "Joint Pain (关节疼痛)",
            "Dyspnea (呼吸困难)",
            "Exacerbation (急性加重)",
            "Hospital Admission (住院)",
            "Blood Pressure Instability (血压波动)",
            "Glycemic Instability (血糖波动)",
            "Renal Stress (肾脏负荷)",
            "Swelling (肿胀)",
            "Stiffness (僵硬)",
            "Morning Stiffness (晨僵)",
            "Inflammation (炎症)",
            "Limited Mobility (活动受限)",
            "Joint Dysfunction (关节功能障碍)"
        ]
    },
    "Mechanism": {
        "name": "生理机制",
        "description": "气候和环境暴露影响慢性病风险或症状的生理、行为或服务机制",
        "examples": [
            "Inflammatory Response (炎症反应)",
            "Cartilage Degradation (软骨退化)",
            "Immune Response (免疫应答)",
            "Synovial Changes (滑膜变化)",
            "Joint Pressure Changes (关节内压力变化)",
            "Nerve Sensitivity (神经敏感性)",
            "Blood Circulation (血液循环)",
            "Cytokine Release (细胞因子释放)",
            "Dehydration (脱水)",
            "Medication Safety (用药安全)",
            "Care Access Disruption (医疗可及性中断)"
        ]
    },
    "Population": {
        "name": "研究人群",
        "description": "研究涉及的人群特征",
        "examples": [
            "Elderly (老年人)",
            "Adults (成年人)",
            "Women (女性)",
            "Men (男性)",
            "Patients (患者)",
            "Specific Age Group (特定年龄组)"
        ]
    },
    "StudyType": {
        "name": "研究类型",
        "description": "研究方法学类型",
        "examples": [
            "Cohort Study (队列研究)",
            "Case-Control Study (病例对照研究)",
            "Cross-Sectional Study (横断面研究)",
            "Randomized Controlled Trial (随机对照试验)",
            "Systematic Review (系统综述)",
            "Meta-Analysis (荟萃分析)"
        ]
    }
}

# 关系类型定义
RELATION_TYPES = {
    "AFFECTS": {
        "name": "影响",
        "description": "气候因素对慢性病、症状或结局的影响",
        "examples": [
            "(Temperature, AFFECTS, Osteoarthritis)",
            "(Heat Wave, AFFECTS, Cardiovascular Disease)",
            "(Humidity, AFFECTS, Joint Pain)"
        ],
        "properties": ["direction", "strength", "evidence_level"]
    },
    "CAUSES": {
        "name": "导致",
        "description": "因果关系",
        "examples": [
            "(Cold Exposure, CAUSES, Joint Stiffness)",
            "(High Humidity, CAUSES, Pain Increase)"
        ],
        "properties": ["confidence", "mechanism"]
    },
    "EXACERBATES": {
        "name": "加重",
        "description": "使症状或疾病恶化",
        "examples": [
            "(Air Pollution, EXACERBATES, COPD)",
            "(High Barometric Pressure, EXACERBATES, Joint Pain)"
        ],
        "properties": ["severity_increase", "frequency"]
    },
    "ALLEVIATES": {
        "name": "缓解",
        "description": "减轻症状或改善病情",
        "examples": [
            "(Warm Temperature, ALLEVIATES, Morning Stiffness)",
            "(Dry Weather, ALLEVIATES, Joint Swelling)"
        ],
        "properties": ["relief_degree", "duration"]
    },
    "CORRELATES_WITH": {
        "name": "相关",
        "description": "统计相关性",
        "examples": [
            "(Humidity, CORRELATES_WITH, Pain Severity)",
            "(Temperature Change, CORRELATES_WITH, Symptom Flare)"
        ],
        "properties": ["correlation_coefficient", "p_value", "sample_size"]
    },
    "HAS_SYMPTOM": {
        "name": "具有症状",
        "description": "疾病与其症状的关系",
        "examples": [
            "(COPD, HAS_SYMPTOM, Dyspnea)",
            "(Rheumatoid Arthritis, HAS_SYMPTOM, Joint Pain)",
            "(Osteoarthritis, HAS_SYMPTOM, Stiffness)"
        ],
        "properties": ["frequency", "severity"]
    },
    "INVOLVES_MECHANISM": {
        "name": "涉及机制",
        "description": "疾病或影响涉及的生理机制",
        "examples": [
            "(Temperature Change, INVOLVES_MECHANISM, Inflammatory Response)",
            "(Osteoarthritis, INVOLVES_MECHANISM, Cartilage Degradation)"
        ],
        "properties": ["mechanism_type", "evidence"]
    },
    "STUDIED_IN": {
        "name": "研究于",
        "description": "实体在某篇研究中被提及",
        "examples": [
            "(Temperature Effect, STUDIED_IN, PMID:12345678)",
            "(Humidity Impact, STUDIED_IN, Study_2023)"
        ],
        "properties": ["pmid", "year", "journal", "study_type"]
    },
    "AFFECTS_POPULATION": {
        "name": "影响人群",
        "description": "关系或疾病对特定人群的影响",
        "examples": [
            "(Cold Weather Impact, AFFECTS_POPULATION, Elderly)",
            "(Osteoarthritis, AFFECTS_POPULATION, Women)"
        ],
        "properties": ["prevalence", "severity"]
    },
    "MEDIATES": {
        "name": "介导",
        "description": "中介机制",
        "examples": [
            "(Barometric Pressure, MEDIATES, Joint Pressure Changes)",
            "(Temperature, MEDIATES, Blood Circulation)"
        ],
        "properties": ["mediation_strength"]
    }
}

# 实体属性定义
ENTITY_PROPERTIES = {
    "name": "实体名称",
    "type": "实体类型",
    "description": "详细描述",
    "source_pmid": "来源文献PMID",
    "mention_count": "提及次数",
    "confidence": "置信度"
}

# 关系属性定义
RELATION_PROPERTIES = {
    "source": "关系来源",
    "evidence": "证据描述",
    "confidence": "置信度",
    "pmid": "来源PMID",
    "study_type": "研究类型",
    "sample_size": "样本量",
    "p_value": "P值",
    "effect_size": "效应量"
}


def get_entity_type_prompt():
    """生成实体类型的Prompt描述"""
    prompt = "Extract the following entity types from the text:\n\n"
    for entity_type, info in ENTITY_TYPES.items():
        prompt += f"{entity_type}: {info['description']}\n"
        prompt += f"  Examples: {', '.join(info['examples'][:3])}\n\n"
    return prompt


def get_relation_type_prompt():
    """生成关系类型的Prompt描述"""
    prompt = "Identify the following relationship types:\n\n"
    for relation_type, info in RELATION_TYPES.items():
        prompt += f"{relation_type}: {info['description']}\n"
        if info['examples']:
            prompt += f"  Example: {info['examples'][0]}\n\n"
    return prompt


def validate_entity_type(entity_type: str) -> bool:
    """验证实体类型是否有效"""
    return entity_type in ENTITY_TYPES


def validate_relation_type(relation_type: str) -> bool:
    """验证关系类型是否有效"""
    return relation_type in RELATION_TYPES
