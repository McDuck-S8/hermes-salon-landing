#!/usr/bin/env python3
"""
AI Education Bot — Telegram bot with AI for testing student knowledge.
Based on real FL.ru order: "разработка чат-бота с использованием AI-агента 
для подготовки и тестирования знаний обучающихся"

This bot:
1. Presents study materials
2. Generates quiz questions using AI
3. Evaluates answers
4. Tracks progress
5. Provides personalized feedback
"""

import os
import json
import random
from datetime import datetime

# Simulated AI responses (replace with real OpenAI/Claude API in production)
class AIEducator:
    """AI-powered education engine."""
    
    def __init__(self, subject="Python programming"):
        self.subject = subject
        self.difficulty_levels = ["начинающий", "средний", "продвинутый"]
        self.question_types = ["multiple_choice", "open_ended", "code_review"]
    
    def generate_question(self, topic, difficulty="средний"):
        """Generate a quiz question on the given topic."""
        
        # In production: call OpenAI/Claude API
        # For demo: use template-based questions
        
        questions_db = {
            "python": {
                "начинающий": [
                    {
                        "question": "Что выведет код: print(type([]))?",
                        "options": ["<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'set'>"],
                        "correct": 0,
                        "explanation": "[] — это литерал списка (list)."
                    },
                    {
                        "question": "Какой оператор используется для возведения в степень?",
                        "options": ["^", "**", "pow()", "Все перечисленные"],
                        "correct": 1,
                        "explanation": "В Python оператор ** используется для возведения в степень."
                    },
                ],
                "средний": [
                    {
                        "question": "Что такое list comprehension?",
                        "options": [
                            "Способ создания списков в одну строку",
                            "Метод сортировки списков",
                            "Тип данных в Python",
                            "Функция для работы со списками"
                        ],
                        "correct": 0,
                        "explanation": "List comprehension — это компактный способ создания списков: [x for x in range(10)]"
                    },
                    {
                        "question": "Что выведет код: print(\'hello\' * 3)?",
                        "options": ["hellohellohello", "hello 3", "Ошибка", "hello*3"],
                        "correct": 0,
                        "explanation": "Оператор * повторяет строку указанное количество раз."
                    },
                ],
                "продвинутый": [
                    {
                        "question": "Что такое GIL в Python?",
                        "options": [
                            "Global Interpreter Lock — мьютекс, ограничивающий потоки",
                            "General Input Layer — слой ввода",
                            "Graphical Interface Library — библиотека GUI",
                            "Global Index List — глобальный список индексов"
                        ],
                        "correct": 0,
                        "explanation": "GIL (Global Interpreter Lock) — механизм, позволяющий только одному потоку выполнять Python-код одновременно."
                    },
                ],
            },
            "ai": {
                "начинающий": [
                    {
                        "question": "Что такое машинное обучение?",
                        "options": [
                            "Обучение компьютеров на данных без явного программирования",
                            "Программирование роботов",
                            "Создание веб-сайтов",
                            "Анализ данных в Excel"
                        ],
                        "correct": 0,
                        "explanation": "Машинное обучение — это метод анализа данных, который автоматизирует построение аналитических моделей."
                    },
                ],
                "средний": [
                    {
                        "question": "Что такое нейронная сеть?",
                        "options": [
                            "Компьютерная модель, вдохновлённая мозгом",
                            "Сеть компьютеров",
                            "Протокол передачи данных",
                            "Тип базы данных"
                        ],
                        "correct": 0,
                        "explanation": "Нейронная сеть — это математическая модель, имитирующая работу нейронов мозга."
                    },
                ],
            },
        }
        
        # Find questions for topic and difficulty
        topic_lower = topic.lower()
        for key in questions_db:
            if key in topic_lower:
                if difficulty in questions_db[key]:
                    return random.choice(questions_db[key][difficulty])
        
        # Default question
        return {
            "question": f"Расскажите кратко о теме: {topic}",
            "options": None,
            "correct": None,
            "explanation": "Открытый вопрос — требуется развёрнутый ответ."
        }
    
    def evaluate_answer(self, question_data, user_answer):
        """Evaluate user's answer and provide feedback."""
        
        if question_data.get("options"):
            # Multiple choice
            try:
                selected = int(user_answer) - 1
                if selected == question_data["correct"]:
                    return {
                        "correct": True,
                        "message": f"✅ Правильно! {question_data['explanation']}",
                        "score": 10
                    }
                else:
                    correct_text = question_data["options"][question_data["correct"]]
                    return {
                        "correct": False,
                        "message": f"❌ Неправильно. Правильный ответ: {correct_text}\n{question_data['explanation']}",
                        "score": 0
                    }
            except (ValueError, IndexError):
                return {
                    "correct": False,
                    "message": "Пожалуйста, выберите номер ответа (1-4)",
                    "score": 0
                }
        else:
            # Open-ended — in production: use AI to evaluate
            return {
                "correct": None,
                "message": "📝 Спасибо за ответ! В полной версии AI оценит ваш ответ детально.",
                "score": 5
            }
    
    def generate_study_plan(self, current_level, weak_topics):
        """Generate personalized study plan."""
        plan = {
            "level": current_level,
            "recommendations": [],
            "estimated_time": "2-3 часа",
            "topics": []
        }
        
        for topic in weak_topics:
            plan["topics"].append({
                "name": topic,
                "priority": "высокий" if topic in ["python", "ai"] else "средний",
                "resources": [f"Глава о {topic}", f"Практика: 5 упражнений"]
            })
        
        return plan


class StudentProgress:
    """Track student learning progress."""
    
    def __init__(self, student_id):
        self.student_id = student_id
        self.scores = []
        self.topics_studied = set()
        self.correct_answers = 0
        self.total_questions = 0
    
    def add_result(self, topic, score):
        """Add quiz result."""
        self.scores.append({"topic": topic, "score": score, "time": datetime.now().isoformat()})
        self.topics_studied.add(topic)
        self.total_questions += 1
        if score > 0:
            self.correct_answers += 1
    
    def get_stats(self):
        """Get learning statistics."""
        if not self.scores:
            return {"message": "Пока нет данных"}
        
        avg_score = sum(s["score"] for s in self.scores) / len(self.scores)
        accuracy = (self.correct_answers / self.total_questions * 100) if self.total_questions > 0 else 0
        
        return {
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "accuracy": f"{accuracy:.1f}%",
            "average_score": f"{avg_score:.1f}/10",
            "topics_studied": list(self.topics_studied),
            "level": self._determine_level(avg_score)
        }
    
    def _determine_level(self, avg_score):
        """Determine student level based on performance."""
        if avg_score >= 8:
            return "продвинутый"
        elif avg_score >= 5:
            return "средний"
        else:
            return "начинающий"


def main():
    """Main bot function — demonstrates the education system."""
    
    print("=" * 60)
    print("AI EDUCATION BOT — DEMO")
    print("Based on FL.ru order: AI-агент для тестирования знаний")
    print("=" * 60)
    
    # Initialize
    ai = AIEducator(subject="Python & AI")
    student = StudentProgress(student_id="demo_user")
    
    # Simulate learning session
    topics = ["python", "ai"]
    
    for topic in topics:
        print(f"\n📚 Тема: {topic.upper()}")
        print("-" * 40)
        
        for difficulty in ["начинающий", "средний"]:
            question = ai.generate_question(topic, difficulty)
            
            print(f"\n❓ Вопрос ({difficulty}):")
            print(f"   {question['question']}")
            
            if question.get("options"):
                for i, opt in enumerate(question["options"]):
                    print(f"   {i+1}. {opt}")
                
                # Simulate answer (random for demo)
                simulated_answer = str(random.randint(1, len(question["options"])))
                print(f"\n👤 Ответ: {simulated_answer}")
                
                result = ai.evaluate_answer(question, simulated_answer)
                print(f"   {result['message']}")
                student.add_result(topic, result["score"])
            else:
                print("   [Открытый вопрос — требуется развёрнутый ответ]")
                student.add_result(topic, 5)
    
    # Show statistics
    print("\n" + "=" * 60)
    print("📊 СТАТИСТИКА ОБУЧЕНИЯ")
    print("=" * 60)
    
    stats = student.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Generate study plan
    print("\n📋 ПЛАН ОБУЧЕНИЯ")
    print("-" * 40)
    
    plan = ai.generate_study_plan(stats.get("level", "начинающий"), topics)
    print(f"   Уровень: {plan['level']}")
    print(f"   Время: {plan['estimated_time']}")
    print(f"   Темы:")
    for topic in plan["topics"]:
        print(f"     - {topic['name']} (приоритет: {topic['priority']})")
    
    print("\n✅ Демо завершено!")
    print("\n" + "=" * 60)
    print("В ПРОДАКШН ВЕРСИИ:")
    print("- Реальный Telegram бот на aiogram")
    print("- OpenAI/Claude API для генерации вопросов")
    print("- AI-оценка открытых ответов")
    print("- База данных PostgreSQL для прогресса")
    print("- Веб-дашборд для преподавателей")
    print("=" * 60)


if __name__ == "__main__":
    main()
