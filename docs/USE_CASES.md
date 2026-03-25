# 🎯 Use Cases: EpidBot-OpenMAIC Integration

> **Real-world scenarios and user stories**

---

## 👥 Primary Users

| User Type | Description | Key Needs |
|-----------|-------------|-----------|
| **Health Agents** | Field workers in endemic areas | Practical training, quick updates |
| **Epidemiologists** | Public health surveillance professionals | Deep analysis, advanced techniques |
| **Students** | Public health, medicine, nursing students | Learning foundations, case studies |
| **Health Managers** | Municipal/state health department leaders | Policy training, decision support |
| **Researchers** | Academic researchers | Methods training, data analysis |

---

## 📚 Use Case Categories

### Category 1: Training & Education

---

## UC-001: Dengue Surveillance Training for Field Agents

### Overview
Train field health agents on dengue surveillance protocols using real-time data from their municipality.

### Actors
- **Primary:** Municipal health agent (Agente de Saúde)
- **Secondary:** AI Teacher, AI Classmates
- **System:** EpidBot-OpenMAIC Platform

### Preconditions
- Agent has basic smartphone/computer access
- Municipality has recent dengue cases reported in SINAN

### Main Flow

```
1. Health coordinator accesses platform
2. Inputs: "Create training for dengue surveillance in [Municipality]"
3. System fetches:
   - Last 30 days of dengue cases from SINAN
   - Current vector control data
   - Weather patterns affecting transmission
4. AI analyzes data and generates:
   - 8 slides with local statistics
   - 5 quiz questions based on current situation
   - 1 interactive simulation of outbreak response
5. System creates classroom with:
   - AI Teacher: Epidemiologist persona
   - 3 AI Classmates: Other health agents
6. Field agents receive invitation link
7. Agents complete 45-minute interactive training
8. System generates completion certificates
```

### Alternative Flows

**A1: No recent cases**
- System uses historical data from similar municipalities
- Includes "what if" scenario preparation

**A2: Poor internet connectivity**
- System generates downloadable PPTX
- Offline version with static data

### Postconditions
- Agents trained on current local situation
- Completion recorded in HR system
- Knowledge gaps identified

### Business Value
- **Time saved:** 4 hours (vs traditional training prep)
- **Relevance:** 100% current local data
- **Scale:** Unlimited simultaneous trainees

---

## UC-002: University Course Module on Arbovirus Epidemiology

### Overview
Professor creates a comprehensive 2-week course module on arbovirus epidemiology using multi-country data.

### Actors
- **Primary:** Public health professor
- **Secondary:** Students (30-50), AI Teaching Assistant
- **System:** EpidBot-OpenMAIC Platform

### Preconditions
- Professor has syllabus outline
- Course LMS integration available

### Main Flow

```
1. Professor requests: "Generate arbovirus module for Week 3-4"
2. System fetches comparative data:
   - Brazil: Dengue trends (SINAN)
   - Colombia: Chikungunya patterns (INS)
   - Argentina: Zika historical data
   - PAHO: Regional overview
3. AI generates comprehensive module:
   
   Week 3 Content:
   ├── Lecture 1: Dengue in Brazil (slides + video)
   ├── Lecture 2: Chikungunya in Colombia
   ├── Case Study: Cross-border transmission
   └── Quiz 1: Comparative analysis
   
   Week 4 Content:
   ├── Lecture 3: Zika lessons learned
   ├── Simulation: Multi-country outbreak
   ├── Group Project: Prevention strategies
   └── Quiz 2: Final assessment
4. System creates virtual classroom with:
   - AI Professor: Expert epidemiologist
   - AI TA: Answers student questions 24/7
   - AI Classmates: 5 virtual students for discussions
5. Content exported to Moodle/Canvas
6. Students engage with interactive content
7. Professor monitors analytics dashboard
```

### Key Features
- **Interactive simulations:** Students manage virtual outbreak
- **Real data:** Actual case numbers from 3 countries
- **Group work:** AI-facilitated group discussions
- **Auto-grading:** Immediate quiz feedback

### Business Value
- **Prep time:** Reduced from 20 hours to 30 minutes
- **Engagement:** +60% vs traditional lectures
- **Consistency:** Same quality across semesters

---

### Category 2: Emergency Response

---

## UC-003: Emergency Zika Outbreak Response Workshop

### Overview
Rapid training for health teams during active Zika outbreak emergency.

### Actors
- **Primary:** Emergency response team (10-15 people)
- **Secondary:** State health secretary
- **System:** EpidBot-OpenMAIC Platform

### Preconditions
- Outbreak declared within last 7 days
- Team needs immediate protocol updates

### Main Flow

```
1. Health secretary declares emergency training need
2. System auto-generates emergency workshop:
   - Data: Last 7 days of outbreak progression
   - Analysis: Current Rt value, attack rates
   - Comparison: Similar past outbreaks
   
3. 2-hour intensive workshop created:
   
   Hour 1: Situation Assessment
   ├── Live dashboard of current cases
   ├── AI presents transmission patterns
   ├── Team discusses intervention options
   └── AI simulates each option's impact
   
   Hour 2: Response Planning
   ├── Breakout sessions with AI facilitator
   ├── Resource allocation simulation
   ├── Timeline planning with milestones
   └── Commitment to action items
   
4. System tracks:
   - Decisions made during simulation
   - Knowledge assessment scores
   - Action items committed
   
5. Post-workshop:
   - Report to health secretary
   - Action item tracking
   - Follow-up training scheduled
```

### Special Features
- **Time pressure:** Simulated countdowns
- **Real decisions:** Team choices affect simulation
- **Immediate application:** Protocols for current outbreak
- **Documentation:** Auto-generated after-action report

### Business Value
- **Speed:** Training ready in 15 minutes
- **Relevance:** Current outbreak data
- **Coordination:** Aligns multi-disciplinary team
- **Accountability:** Tracks commitments

---

### Category 3: Continuous Learning

---

## UC-004: Weekly Epidemiological Update

### Overview
Automated weekly briefing for epidemiologists on disease trends.

### Actors
- **Primary:** Surveillance team epidemiologists
- **System:** EpidBot-OpenMAIC Platform (automated)

### Preconditions
- Weekly data feed configured
- Team subscribed to updates

### Main Flow

```
1. Every Monday 6:00 AM, system auto-generates:
   
   Weekly Epidemiological Update
   ├── Executive Summary (AI-generated)
   ├── Disease-by-disease breakdown:
   │   ├── Dengue: Cases, trend, alert level
   │   ├── Chikungunya: Same
   │   └── Influenza: Same
   ├── Geographic hotspots map
   ├── Comparison to previous weeks
   ├── Weather correlation analysis
   └── Predictive models (next 2 weeks)
   
2. 15-minute interactive presentation created
3. System emails link to surveillance team
4. Epidemiologists review on-demand
5. AI available for Q&A about data
6. System logs questions for pattern analysis
```

### Business Value
- **Consistency:** Never miss a weekly update
- **Efficiency:** 15-min vs 2-hour manual prep
- **Insight:** AI pattern recognition

---

### Category 4: Research & Analysis

---

## UC-005: Research Methods Training

### Overview
Train researchers on epidemiological analysis methods using real datasets.

### Actors
- **Primary:** Graduate students, researchers
- **Secondary:** Research advisor
- **System:** EpidBot-OpenMAIC Platform

### Main Flow

```
1. Advisor requests: "R0 estimation methods training"
2. System creates workshop:
   
   Module: Estimating R0 for Dengue
   ├── Theory: Mathematical foundations
   ├── Methods: 3 different approaches
   ├── Hands-on: Real dataset from Brazil
   ├── Exercise: Calculate R0 for multiple cities
   ├── Discussion: Limitations and assumptions
   └── Assessment: Interpret results
   
3. Students work with actual SINAN data
4. AI guides through calculation steps
5. Peer discussion facilitated by AI classmates
6. Results compared across student groups
```

### Business Value
- **Real data:** Learn with actual surveillance data
- **Safe environment:** Practice without real consequences
- **Reproducibility:** Documented analysis steps

---

## 🌍 Regional Adaptations

### Brazil
- **Data source:** SINAN, InfoDengue
- **Focus diseases:** Dengue, Zika, Chikungunya, COVID-19
- **Languages:** Portuguese
- **Use cases:** Sistema Único de Saúde (SUS) training

### Colombia
- **Data source:** SIVIGILA (INS)
- **Focus diseases:** Malaria, Dengue, Leishmaniasis
- **Languages:** Spanish
- **Use cases:** territorial health training

### Global/WHO
- **Data source:** WHO, HealthMap, ProMED
- **Focus diseases:** Pandemic preparedness
- **Languages:** English, French
- **Use cases:** International health regulations

---

## 📊 Success Metrics by Use Case

| Use Case | Primary Metric | Target |
|----------|---------------|--------|
| UC-001: Field Training | Completion rate | >90% |
| UC-002: University Course | Student satisfaction | >4.5/5 |
| UC-003: Emergency Workshop | Response time | <15 min to deploy |
| UC-004: Weekly Update | Open rate | >80% |
| UC-005: Research Training | Knowledge gain | +40% pre/post |

---

## 🎭 User Personas

### Persona 1: Maria, Health Agent
- **Age:** 35
- **Location:** Recife, PE
- **Tech level:** Basic smartphone
- **Needs:** Quick updates, practical guidance
- **Pain points:** Hard to access training, outdated materials

### Persona 2: Dr. Silva, Epidemiologist
- **Age:** 45
- **Location:** Brasília, DF
- **Tech level:** Advanced
- **Needs:** Deep analysis, advanced methods
- **Pain points:** Data scattered, manual report prep

### Persona 3: Prof. Ana, University
- **Age:** 38
- **Location:** São Paulo, SP
- **Tech level:** Intermediate
- **Needs:** Engaging content, current examples
- **Pain points:** Outdated case studies, low engagement

---

## 🔮 Future Use Cases

### UC-006: International Collaboration
Cross-border outbreak simulation with teams from multiple countries.

### UC-007: Policy Maker Briefing
Executive summaries for health secretaries with decision support.

### UC-008: Community Health Worker
Basic training for community agents in rural areas (low bandwidth).

### UC-009: Outbreak Investigation Training
Simulation of field investigation protocols.

### UC-010: Vaccination Campaign Planning
Training for immunization teams using coverage data.

---

*Document Version: 1.0*  
*Last Updated: March 2025*
