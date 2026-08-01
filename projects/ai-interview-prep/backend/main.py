import os
import json
import re
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
import httpx
from PyPDF2 import PdfReader
from docx import Document
import io

# Инициализация приложения
app = FastAPI(
    title="AI Interview Prep API",
    description="Backend для AI-подготовки к собеседованиям: парсинг резюме, парсинг HH.ru, мэтчинг с GPT-4o",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (в проде — Redis/Postgres)
resumes_db: Dict[str, dict] = {}
vacancies_db: Dict[str, dict] = {}
matches_db: Dict[str, dict] = {}

# ─── Models ──────────────────────────────────────────────────────────────
class ParsedResume(BaseModel):
    resume_id: str
    full_text: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: List[str] = []
    experience_years: float = 0
    experience: List[dict] = []
    education: List[dict] = []
    raw_sections: Dict[str, str] = {}

class HHVacancy(BaseModel):
    vacancy_id: str
    url: str
    name: str
    company: str
    salary: Optional[str] = None
    experience: Optional[str] = None
    employment: Optional[str] = None
    schedule: Optional[str] = None
    description: str
    key_skills: List[str] = []
    professional_roles: List[str] = []
    published_at: Optional[str] = None

class MatchRequest(BaseModel):
    resume_id: str
    vacancy_id: str

class MatchResult(BaseModel):
    match_id: str
    resume_id: str
    vacancy_id: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    gaps: List[str]
    interview_questions: List[dict]
    preparation_plan: List[dict]
    created_at: str

# ─── Helpers: Text Extraction ────────────────────────────────────────────
def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text.append(t)
    return "\n".join(text)

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def extract_text_from_file(file: UploadFile) -> str:
    content = file.file.read()
    if file.filename.lower().endswith('.pdf'):
        return extract_text_from_pdf(content)
    elif file.filename.lower().endswith('.docx'):
        return extract_text_from_docx(content)
    elif file.filename.lower().endswith('.txt'):
        return content.decode('utf-8', errors='ignore')
    else:
        raise HTTPException(400, "Поддерживаются только PDF, DOCX, TXT")

# ─── Helpers: Resume Parsing ─────────────────────────────────────────────
SKILLS_KEYWORDS = [
    # Языки
    'python', 'javascript', 'typescript', 'java', 'c#', 'c++', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin',
    # Фреймворки
    'django', 'fastapi', 'flask', 'react', 'vue', 'angular', 'next.js', 'nuxt', 'spring', 'node.js', 'express',
    'nestjs', 'gin', 'echo', 'fiber', 'laravel', 'symfony', 'rails',
    # БД
    'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'clickhouse', 'sqlite', 'cassandra',
    # DevOps
    'docker', 'kubernetes', 'k8s', 'ci/cd', 'github actions', 'gitlab ci', 'jenkins', 'terraform', 'ansible',
    'aws', 'gcp', 'azure', 'yandex cloud', 'cloudflare',
    # ML/AI
    'machine learning', 'deep learning', 'pytorch', 'tensorflow', 'keras', 'scikit-learn', 'huggingface',
    'llm', 'rag', 'langchain', 'llama', 'gpt', 'bert', 'transformers', 'nlp', 'computer vision',
    # Data
    'pandas', 'numpy', 'sql', 'spark', 'kafka', 'airflow', 'dbt', 'tableau', 'power bi', 'superset',
    # Прочее
    'git', 'linux', 'bash', 'rest', 'graphql', 'grpc', 'microservices', 'design patterns', 'clean architecture',
    'tdd', 'unit testing', 'pytest', 'jest', 'cypress', 'playwright',
]

def parse_resume(text: str) -> ParsedResume:
    resume_id = str(uuid.uuid4())[:8]
    
    # Нормализация
    text_lower = text.lower()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Контакты
    email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    phone = re.search(r'(\+7|8)[\s\(]?\d{3}[\s\)]?\d{3}[\s-]?\d{2}[\s-]?\d{2}', text)
    
    # Навыки — ищем ключевые слова
    found_skills = []
    for skill in SKILLS_KEYWORDS:
        if skill in text_lower:
            found_skills.append(skill)
    
    # Опыт работы — грубая эвристика
    exp_years = 0
    exp_matches = re.findall(r'(\d{1,2})\s*(?:лет|год|года|years?)', text_lower)
    if exp_matches:
        exp_years = max([int(m) for m in exp_matches])
    
    # Разделы
    sections = {}
    current_section = 'header'
    current_content = []
    section_keywords = {
        'experience': ['опыт', 'работа', 'employment', 'work experience', 'карьера'],
        'education': ['образование', 'education', 'учеба', 'университет', 'курсы'],
        'skills': ['навыки', 'skills', 'технологии', 'стек', 'инструменты'],
        'projects': ['проекты', 'projects', 'пет-проекты', 'pet projects'],
    }
    
    for line in lines:
        line_lower = line.lower()
        # Определяем секцию
        for sec, keywords in section_keywords.items():
            if any(kw in line_lower for kw in keywords) and len(line) < 50:
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = sec
                current_content = []
                break
        else:
            current_content.append(line)
    
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    # Имя — первая непустая строка, похожая на ФИО
    name = None
    for line in lines[:10]:
        if re.match(r'^[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+$', line) or \
           re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', line):
            name = line
            break
    
    return ParsedResume(
        resume_id=resume_id,
        full_text=text[:50000],  # ограничиваем
        name=name,
        email=email.group(0) if email else None,
        phone=phone.group(0) if phone else None,
        skills=list(set(found_skills))[:30],
        experience_years=exp_years,
        raw_sections=sections,
    )

# ─── Helpers: HH.ru Parsing ──────────────────────────────────────────────
async def fetch_hh_vacancy(url: str) -> HHVacancy:
    """Парсит вакансию с HH.ru по URL или ID"""
    # Извлекаем ID из URL
    vacancy_id_match = re.search(r'vacancy/(\d+)', url)
    if not vacancy_id_match:
        vacancy_id_match = re.search(r'/(\d+)\?', url)
    if not vacancy_id_match:
        vacancy_id_match = re.search(r'(\d{6,})', url)
    
    if not vacancy_id_match:
        raise HTTPException(400, "Не удалось извлечь ID вакансии из URL. Пример: https://hh.ru/vacancy/12345678")
    
    vacancy_id = vacancy_id_match.group(1)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Публичный API HH (без токена даёт базовую инфу)
        resp = await client.get(f"https://api.hh.ru/vacancies/{vacancy_id}")
        if resp.status_code == 404:
            raise HTTPException(404, "Вакансия не найдена на HH.ru")
        if resp.status_code != 200:
            raise HTTPException(502, f"HH API error: {resp.status_code}")
        
        data = resp.json()
        
        # Парсим зарплату
        salary_str = None
        if data.get('salary'):
            s = data['salary']
            parts = []
            if s.get('from'): parts.append(f"от {s['from']:,}")
            if s.get('to'): parts.append(f"до {s['to']:,}")
            if s.get('currency'): parts.append(s['currency'])
            salary_str = ' '.join(parts)
        
        # Описание — чистим HTML
        desc = data.get('description', '')
        desc = re.sub(r'<[^>]+>', '', desc)
        desc = re.sub(r'\s+', ' ', desc).strip()
        
        return HHVacancy(
            vacancy_id=vacancy_id,
            url=url,
            name=data.get('name', ''),
            company=data.get('employer', {}).get('name', ''),
            salary=salary_str,
            experience=data.get('experience', {}).get('name'),
            employment=data.get('employment', {}).get('name'),
            schedule=data.get('schedule', {}).get('name'),
            description=desc[:10000],
            key_skills=[s['name'] for s in data.get('key_skills', [])],
            professional_roles=[r['name'] for r in data.get('professional_roles', [])],
            published_at=data.get('published_at'),
        )

# ─── Helpers: Matching Logic ─────────────────────────────────────────────
async def match_with_llm(resume: ParsedResume, vacancy: HHVacancy) -> MatchResult:
    """Мэтчинг через GPT-4o (или любой OpenAI-совместимый API)"""
    
    # Подготовка промпта
    prompt = f"""Ты — эксперт по найму в IT. Сравни резюме кандидата с вакансией и верни строгий JSON.

РЕЗЮМЕ:
Имя: {resume.name or 'Не указано'}
Опыт: {resume.experience_years} лет
Навыки: {', '.join(resume.skills[:25])}
Опыт работы (кратко): {resume.raw_sections.get('experience', '')[:2000]}
Проекты: {resume.raw_sections.get('projects', '')[:1000]}

ВАКАНСИЯ:
Название: {vacancy.name}
Компания: {vacancy.company}
Опыт: {vacancy.experience or 'не указан'}
Зарплата: {vacancy.salary or 'не указана'}
Ключевые навыки: {', '.join(vacancy.key_skills[:20])}
Проф. роли: {', '.join(vacancy.professional_roles)}
Описание: {vacancy.description[:3000]}

Верни ТОЛЬКО JSON с полями:
{{
  "match_score": число 0-100,
  "matched_skills": ["skill1", "skill2", ...],  // что есть и в резюме, и в вакансии
  "missing_skills": ["skill1", "skill2", ...],  // что требуется в вакансии, но нет в резюме
  "strengths": ["сильная сторона 1", "сильная сторона 2", ...],  // 3-5 пунктов
  "gaps": ["пробел 1", "пробел 2", ...],  // 3-5 пунктов, критичные
  "interview_questions": [
    {{"topic": "тема", "question": "вопрос", "hint": "что искать в ответе", "difficulty": "junior|middle"}},
    ...
  ],  // 5-7 вопросов по пробелам + сильным сторонам
  "preparation_plan": [
    {{"day": 1, "focus": "тема дня", "tasks": ["задача 1", "задача 2"], "resources": ["ссылка/название ресурса"]}},
    ...
  ]  // 7 дней
}}

Критично: match_score должен честно отражать соответствие. Джуниор с 1 годом опыта на сеньорскую — 20-30%. Полный стек — 80-95%.
"""

    try:
        import openai
        client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        
        response = await client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": "Ты эксперт по техническому найму. Отвечаешь только валидным JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return MatchResult(
            match_id=str(uuid.uuid4())[:8],
            resume_id=resume.resume_id,
            vacancy_id=vacancy.vacancy_id,
            match_score=result.get("match_score", 0),
            matched_skills=result.get("matched_skills", []),
            missing_skills=result.get("missing_skills", []),
            strengths=result.get("strengths", []),
            gaps=result.get("gaps", []),
            interview_questions=result.get("interview_questions", []),
            preparation_plan=result.get("preparation_plan", []),
            created_at=datetime.now().isoformat(),
        )
    except Exception as e:
        # Fallback: простой эвристический мэтчинг без LLM
        return fallback_match(resume, vacancy)

def fallback_match(resume: ParsedResume, vacancy: HHVacancy) -> MatchResult:
    """Простой мэтчинг без LLM — для демо/оффлайна"""
    resume_skills = set(s.lower() for s in resume.skills)
    vacancy_skills = set(s.lower() for s in vacancy.key_skills)
    
    matched = resume_skills & vacancy_skills
    missing = vacancy_skills - resume_skills
    
    # Скор
    if vacancy_skills:
        skill_score = len(matched) / len(vacancy_skills) * 100
    else:
        skill_score = 50
    
    # Опыт
    exp_required = 0
    if vacancy.experience:
        exp_map = {'Нет опыта': 0, 'От 1 года до 3 лет': 2, 'От 3 до 6 лет': 4, 'Более 6 лет': 7}
        exp_required = exp_map.get(vacancy.experience, 3)
    
    exp_score = min(resume.experience_years / max(exp_required, 1) * 100, 100) if exp_required > 0 else 50
    
    match_score = int(skill_score * 0.7 + exp_score * 0.3)
    
    return MatchResult(
        match_id=str(uuid.uuid4())[:8],
        resume_id=resume.resume_id,
        vacancy_id=vacancy.vacancy_id,
        match_score=match_score,
        matched_skills=list(matched)[:10],
        missing_skills=list(missing)[:10],
        strengths=[f"Знает {', '.join(list(matched)[:3])}"] if matched else ["Базовая мотивация"],
        gaps=[f"Нет опыта с {', '.join(list(missing)[:3])}"] if missing else ["Опыт соответствует требованиям"],
        interview_questions=[
            {"topic": "Tech Stack", "question": f"Расскажи про опыт с {', '.join(list(matched)[:2])}", "hint": "Ищи конкретные проекты", "difficulty": "junior"},
            {"topic": "Gaps", "question": f"Как бы ты закрыл пробел в {', '.join(list(missing)[:2])}?", "hint": "Ожидаем план обучения", "difficulty": "junior"},
        ],
        preparation_plan=[
            {"day": 1, "focus": "Анализ вакансии", "tasks": ["Изучить стек компании", "Подготовить кейсы по-matched скиллам"], "resources": ["HH.ru компания", "GitHub компании"]},
            {"day": 2, "focus": "Заполнение пробелов", "tasks": [f"Прочитать доки по {', '.join(list(missing)[:3])}"], "resources": ["Официальная документация", "YouTube туториалы"]},
            {"day": 3, "focus": "Практика", "tasks": ["Решить 3 задачи на LeetCode Easy", "Написать микросервис на стек вакансии"], "resources": ["LeetCode", "GitHub шаблоны"]},
            {"day": 4, "focus": "Системный дизайн", "tasks": ["Разобрать архитектуру типового проекта на стеке"], "resources": ["System Design Primer", "Артикулы на Хабре"]},
            {"day": 5, "focus": "Soft Skills", "tasks": ["Подготовить STAR-истории по 3 проектам"], "resources": ["STAR метод", "Примеры ответов"]},
            {"day": 6, "focus": "Мок-собеседование", "tasks": ["Пройти собеседование с другом/ментором", "Записать ответы на диктофон"], "resources": ["Pramp", "Interviewing.io"]},
            {"day": 7, "focus": "Финал", "tasks": ["Повторить слабые места", "Подготовить вопросы к работодателю", "Отдохнуть перед собеседованием"], "resources": []},
        ],
        created_at=datetime.now().isoformat(),
    )

# ─── API Endpoints ───────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-interview-prep", "version": "1.0.0"}

@app.post("/api/resume/upload", response_model=ParsedResume)
async def upload_resume(file: UploadFile = File(...)):
    """Загрузка и парсинг резюме (PDF/DOCX/TXT)"""
    text = extract_text_from_file(file)
    if not text.strip():
        raise HTTPException(400, "Файл пустой или текст не извлечён")
    
    parsed = parse_resume(text)
    resumes_db[parsed.resume_id] = parsed.model_dump()
    
    return parsed

@app.post("/api/resume/text", response_model=ParsedResume)
async def upload_resume_text(text: str = Form(...)):
    """Парсинг резюме из текста (для копипаста)"""
    if not text.strip():
        raise HTTPException(400, "Текст пустой")
    
    parsed = parse_resume(text)
    resumes_db[parsed.resume_id] = parsed.model_dump()
    
    return parsed

@app.get("/api/resume/{resume_id}", response_model=ParsedResume)
async def get_resume(resume_id: str):
    if resume_id not in resumes_db:
        raise HTTPException(404, "Резюме не найдено")
    return resumes_db[resume_id]

@app.post("/api/vacancy/fetch", response_model=HHVacancy)
async def fetch_vacancy(url: str = Form(...)):
    """Парсинг вакансии с HH.ru по URL"""
    vacancy = await fetch_hh_vacancy(url)
    vacancies_db[vacancy.vacancy_id] = vacancy.model_dump()
    return vacancy

@app.post("/api/vacancy/text", response_model=HHVacancy)
async def create_vacancy_text(
    name: str = Form(...),
    company: str = Form(""),
    description: str = Form(...),
    key_skills: str = Form(""),
    experience: str = Form(""),
    salary: str = Form(""),
):
    """Создание вакансии вручную (без HH)"""
    vacancy_id = str(uuid.uuid4())[:8]
    skills = [s.strip() for s in key_skills.split(',') if s.strip()]
    
    vacancy = HHVacancy(
        vacancy_id=vacancy_id,
        url=f"manual://{vacancy_id}",
        name=name,
        company=company,
        salary=salary or None,
        experience=experience or None,
        description=description,
        key_skills=skills,
    )
    vacancies_db[vacancy_id] = vacancy.model_dump()
    return vacancy

@app.get("/api/vacancy/{vacancy_id}", response_model=HHVacancy)
async def get_vacancy(vacancy_id: str):
    if vacancy_id not in vacancies_db:
        raise HTTPException(404, "Вакансия не найдена")
    return vacancies_db[vacancy_id]

@app.post("/api/match", response_model=MatchResult)
async def match_resume_vacancy(request: MatchRequest):
    """Мэтчинг резюме с вакансией"""
    if request.resume_id not in resumes_db:
        raise HTTPException(404, "Резюме не найдено")
    if request.vacancy_id not in vacancies_db:
        raise HTTPException(404, "Вакансия не найдена")
    
    resume = ParsedResume(**resumes_db[request.resume_id])
    vacancy = HHVacancy(**vacancies_db[request.vacancy_id])
    
    result = await match_with_llm(resume, vacancy)
    matches_db[result.match_id] = result.model_dump()
    
    return result

@app.get("/api/match/{match_id}", response_model=MatchResult)
async def get_match(match_id: str):
    if match_id not in matches_db:
        raise HTTPException(404, "Результат мэтчинга не найден")
    return matches_db[match_id]

# ─── Run ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)