# 🛰️ TrendLab: Autonomous Intelligence Engine
> **A high-signal, zero-maintenance NLI pipeline for tracking technical breakthroughs across configurable domains with enterprise-grade safety gates.**

[![Live Dashboard](https://img.shields.io/badge/View-Live_Dashboard-FF4B4B?style=for-the-badge&logo=streamlit)](https://trendlab-intel.streamlit.app/)
[![LinkedIn](https://img.shields.io/badge/Connect-LinkedIn-0077B5?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/nishant-verma-88915998/)

## 📖 Overview
TrendLab is an automated intelligence asset designed to solve the "Noise-to-Signal" problem in rapidly evolving tech sectors. It scouts high-value domains (ArXiv, GitHub, Reddit), analyzes data via Natural Language Inference (NLI), and presents objective intelligence scores—all while maintaining a strict governance layer to ensure content professionality and corporate compliance.

---

## 🏗️ System Architecture
The pipeline is architected for **high availability and zero operational cost**, utilizing a version-controlled flat-file system for data persistence.

```mermaid
graph TD
    %% Global Styles
    classDef default fill:#f9f9fb,stroke:#2c3e50,stroke-width:1.5px,color:#2c3e50,font-family:Inter,Arial;
    classDef subgraphStyle fill:#ffffff,stroke:#bdc3c7,stroke-width:1px,stroke-dasharray: 5 5,color:#7f8c8d,font-size:13px;
    classDef highlight fill:#e8f0fe,stroke:#1a73e8,stroke-width:2px,color:#1a73e8,font-weight:bold;
    classDef storage fill:#f1f3f4,stroke:#5f6368,stroke-width:2px;

    %% --- TIER 1: INGESTION ---
    subgraph Ingestion ["1. INGESTION & SEARCH"]
        direction LR
        A[GitHub Action] --> B[Targeted Scout] --> C(Tavily Search API)
    end

    %% --- TIER 2: INTELLIGENCE ---
    subgraph Intel ["2. INTELLIGENCE & SAFETY"]
        direction LR
        D{Model Switcher} -- "NLI Logic" --> E[Inference Tier: Gemini Flash/Pro] --> F[Content Safety Filter]
    end

    %% --- TIER 3: DEPLOYMENT ---
    subgraph Deployment ["3. DEPLOYMENT"]
        direction LR
        G[(trends.csv)] --> H[Streamlit Dashboard]
    end

    %% Vertical Connections between tiers
    C --> D
    F --> G

    %% Apply Classes
    class Ingestion,Intel,Deployment subgraphStyle;
    class C,E highlight;
    class G storage;

    %% Flow Customization
    linkStyle default stroke:#34495e,stroke-width:1.5px;
```

### 🛠️ Key Technical Features

The engine includes a modular **Safety & Redaction Layer** to ensure all generated intelligence is professional and compliant:

* **Entity Masking:** Automatic redaction of specific corporate entities (e.g., Big Four firms) to maintain professional neutrality.
* **Linguistic "Cringe" Filter:** A custom mapping system that identifies and replaces AI-typical buzzwords (e.g., *delve*, *unleash*, *tapestry*) with precise, professional terminology.
* **Toxicity Guard:** Integrated keyword filtering based on standard open-source safety lists to prevent non-professional content ingestion.

To ensure 100% uptime within free-tier quotas, the system features a **Hierarchical Fallback Mechanism**. The **Model Switcher** logic detects rate limits (429) or unavailability and automatically shifts the inference load across a configured priority list:

1.  **Primary:** `gemini-3-flash-preview`
2.  **Secondary:** `gemini-2.5-flash` / `gemini-2.5-pro`
3.  **Legacy:** `gemini-pro-latest`

The system is entirely **domain-agnostic**. By modifying the `config.json`, the scout can pivot across diverse technical vectors:

* **AI & LLM Frontier:** Tracking agentic workflows and fine-tuning breakthroughs.
* **The AI Bubble (Infra):** Monitoring GPU compute costs and infrastructure valuation.
* **Cybersecurity:** Scanning for 0-day exploits, PoC releases, and threat actors.
* **Consumer Tech:** Tracking the evolution of wearables and handheld AI hardware.
* **FinTech & Web3:** Analyzing L2 scaling, stablecoins, and CBDC compliance.

---

### 👤 About the Author

I am a professional at a **Big Four professional services firm**, specializing in the intersection of **Software Engineering, AI Orchestration, and Technical Risk Management.**

**Let's Connect:** [![LinkedIn](https://img.shields.io/badge/Connect-LinkedIn-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/nishant-verma-88915998/)

> *This project is architected with a **"Security-First"** mindset, ensuring that AI-driven insights remain professional, accurate, and objective.*