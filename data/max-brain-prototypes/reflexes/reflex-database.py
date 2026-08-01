#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REFLEX DATABASE — ChromaDB для хранения рефлексов

Интеграция с Nocturnal Cognition
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️ ChromaDB не установлен. Рефлексы будут сохранены в JSON.")

BRAIN_DIR = Path("D:/MAX-BRAIN")
CHROMA_DIR = BRAIN_DIR / "memory" / "chroma" / "reflexes"
JSON_FILE = BRAIN_DIR / "memory" / "reflexes.json"


class ReflexDatabase:
    """База данных рефлексов на ChromaDB"""
    
    def __init__(self):
        self.collection = None
        self.reflexes = []
        
        if CHROMA_AVAILABLE:
            try:
                # Инициализация ChromaDB
                CHROMA_DIR.mkdir(parents=True, exist_ok=True)
                
                client = chromadb.PersistentClient(
                    path=str(CHROMA_DIR),
                    settings=Settings(anonymized_telemetry=False)
                )
                
                self.collection = client.get_or_create_collection(
                    name="reflexes",
                    metadata={"description": "AI reflexes learned from historical data"}
                )
                print(f"✅ ChromaDB подключён: {CHROMA_DIR}")
                
                # Загрузить существующие рефлексы
                self._load_from_chroma()
                
            except Exception as e:
                print(f"⚠️ ChromaDB ошибка: {e}. Используем JSON.")
                self._load_from_json()
        else:
            self._load_from_json()
    
    def _load_from_chroma(self):
        """Загрузить рефлексы из ChromaDB"""
        try:
            if self.collection.count() > 0:
                all_data = self.collection.get()
                self.reflexes = all_data['metadatas']
                print(f"   📚 Загружено {len(self.reflexes)} рефлексов из ChromaDB")
        except Exception as e:
            print(f"   ⚠️ Ошибка загрузки из ChromaDB: {e}")
    
    def _load_from_json(self):
        """Загрузить рефлексы из JSON"""
        if JSON_FILE.exists():
            try:
                with open(JSON_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.reflexes = data.get('reflexes', [])
                print(f"   📚 Загружено {len(self.reflexes)} рефлексов из JSON")
            except:
                pass
    
    def _save_to_json(self):
        """Сохранить рефлексы в JSON"""
        try:
            JSON_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "updated_at": datetime.now().isoformat(),
                    "reflexes": self.reflexes
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"   ⚠️ Ошибка сохранения JSON: {e}")
    
    def add_candidate(self, candidate):
        """Добавить кандидата в рефлексы"""
        try:
            # Создать embedding из текста
            trigger_text = candidate.get('trigger_text', '')
            embedding = self._create_simple_embedding(trigger_text)
            
            # Упростить метадату для ChromaDB (только str, int, float, bool)
            simple_metadata = {
                'id': candidate['id'],
                'trigger_text': trigger_text,
                'trigger_type': candidate.get('trigger_type', 'unknown'),
                'action_type': candidate.get('action', {}).get('type', 'unknown'),
                'action_message': candidate.get('action', {}).get('message', '')[:200],
                'weight': float(candidate.get('weight', 0.5)),
                'source': candidate.get('source', 'historical'),
                'created_at': candidate.get('created_at', '')[:19],
                'success_count': int(candidate.get('success_count', 0)),
                'fail_count': int(candidate.get('fail_count', 0))
            }
            
            if self.collection:
                self.collection.add(
                    ids=[candidate['id']],
                    embeddings=[embedding],
                    metadatas=[simple_metadata]
                )
                print(f"   ✅ Добавлен рефлекс: {candidate['id']}")
            else:
                self.reflexes.append(candidate)
                self._save_to_json()
                print(f"   ✅ Добавлен рефлекс (JSON): {candidate['id']}")
            
        except Exception as e:
            print(f"   ❌ Ошибка добавления рефлекса: {e}")
    
    def search(self, text, threshold=0.5, max_results=5):
        """Поиск сработавшего рефлекса"""
        try:
            text_lower = text.lower()
            text_words = set(text_lower.split())
            
            # Сначала ищем в JSON (надёжнее)
            matched = []
            for reflex in self.reflexes:
                if reflex.get('weight', 0) < threshold:
                    continue
                    
                trigger = reflex.get('trigger_text', '').lower()
                action = reflex.get('action', {}).get('message', '').lower()
                rtype = reflex.get('trigger_type', '').lower()
                
                # Считаем совпадения
                score = 0
                
                # Прямое вхождение слов запроса в trigger
                for word in text_words:
                    if len(word) > 2 and word in trigger:
                        score += 2
                    if len(word) > 2 and word in action:
                        score += 1
                    if len(word) > 2 and word in rtype:
                        score += 1
                
                # Прямое вхождение trigger в запрос
                if trigger in text_lower:
                    score += 5
                
                # Вхождение слов trigger в запрос
                trigger_words = set(trigger.split())
                for word in trigger_words:
                    if len(word) > 2 and word in text_lower:
                        score += 2
                
                if score > 0:
                    matched.append({
                        **reflex,
                        'search_score': score,
                        'distance': 1.0 / (1.0 + score)  # Псевдо-distance
                    })
            
            # Сортировка по score
            matched.sort(key=lambda x: (-x['search_score'], x['weight']))
            return matched[:max_results]
                
        except Exception as e:
            print(f"   ⚠️ Ошибка поиска: {e}")
            return []
    
    def update_weight(self, reflex_id, success=True):
        """Обновить вес рефлекса"""
        try:
            # Найти рефлекс
            reflex = None
            reflex_idx = -1
            
            for i, r in enumerate(self.reflexes):
                if r.get('id') == reflex_id:
                    reflex = r
                    reflex_idx = i
                    break
            
            if not reflex:
                # Поиск в ChromaDB
                if self.collection:
                    result = self.collection.get(ids=[reflex_id])
                    if result and result['metadatas']:
                        reflex = result['metadatas'][0]
            
            if not reflex:
                print(f"   ⚠️ Рефлекс {reflex_id} не найден")
                return False
            
            # Обновить вес
            if success:
                reflex['weight'] = min(1.0, reflex['weight'] + 0.1)
                reflex['success_count'] = reflex.get('success_count', 0) + 1
                print(f"   ✅ Рефлекс {reflex_id}: вес={reflex['weight']:.2f} (+0.1)")
            else:
                reflex['weight'] = max(0.0, reflex['weight'] - 0.1)
                reflex['fail_count'] = reflex.get('fail_count', 0) + 1
                print(f"   ❌ Рефлекс {reflex_id}: вес={reflex['weight']:.2f} (-0.1)")
            
            # Удалить если вес слишком низкий
            if reflex['weight'] < 0.3:
                if self.collection:
                    self.collection.delete(ids=[reflex_id])
                if reflex_idx >= 0:
                    self.reflexes.pop(reflex_idx)
                print(f"   🗑️ Рефлекс {reflex_id} удален (вес < 0.3)")
            else:
                # Сохранить обновлённый
                if self.collection:
                    self.collection.update(
                        ids=[reflex_id],
                        metadatas=[reflex]
                    )
                if reflex_idx >= 0:
                    self.reflexes[reflex_idx] = reflex
                self._save_to_json()
            
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка обновления веса: {e}")
            return False
    
    def _create_simple_embedding(self, text, dim=768):
        """Создать простой embedding (TF-IDF стиль)"""
        # Простая хэш-функция для детерминированного embedding
        embedding = [0.0] * dim
        words = text.lower().split()
        
        for i, word in enumerate(words):
            hash_val = hash(word) % 10000
            idx = (hash_val + i) % dim
            embedding[idx] += 1.0
        
        # Нормализация
        norm = sum(x*x for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x/norm for x in embedding]
        
        return embedding
    
    def get_stats(self):
        """Получить статистику"""
        total = len(self.reflexes)
        if self.collection:
            total = self.collection.count()
        
        by_type = {}
        by_weight = {"high": 0, "medium": 0, "low": 0}
        
        for reflex in self.reflexes:
            t = reflex.get('trigger_type', 'unknown')
            by_type[t] = by_type.get(t, 0) + 1
            
            w = reflex.get('weight', 0)
            if w > 0.7:
                by_weight["high"] += 1
            elif w > 0.4:
                by_weight["medium"] += 1
            else:
                by_weight["low"] += 1
        
        return {
            "total": total,
            "by_type": by_type,
            "by_weight": by_weight
        }
    
    def list_reflexes(self):
        """Вывести список рефлексов"""
        print("\n📋 РЕФЛЕКСЫ:")
        for reflex in self.reflexes[:20]:  # Первые 20
            trigger = reflex.get('trigger_text', 'Unknown')[:40]
            weight = reflex.get('weight', 0)
            success = reflex.get('success_count', 0)
            fail = reflex.get('fail_count', 0)
            print(f"   [{weight:.2f}] {trigger}... (+{success}/-{fail})")
        
        if len(self.reflexes) > 20:
            print(f"   ... и ещё {len(self.reflexes) - 20}")


def main():
    """Тест Reflex Database"""
    print("=" * 70)
    print("REFLEX DATABASE TEST")
    print("=" * 70)
    
    db = ReflexDatabase()
    
    # Загрузить кандидатов из файла
    candidates_file = BRAIN_DIR / "reflex-candidates.json"
    if candidates_file.exists():
        with open(candidates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            candidates = data.get('candidates', [])
        
        print(f"\n📚 Загрузка {len(candidates)} кандидатов...")
        for candidate in candidates:
            db.add_candidate(candidate)
        
        # Статистика
        stats = db.get_stats()
        print(f"\n📊 СТАТИСТИКА:")
        print(f"   Всего: {stats['total']}")
        print(f"   По типам: {stats['by_type']}")
        print(f"   По весу: {stats['by_weight']}")
        
        # Список
        db.list_reflexes()
        
        # Тест поиска
        print("\n🔍 ТЕСТ ПОИСКА:")
        results = db.search("ошибка error failed", threshold=0.3)
        print(f"   Найдено: {len(results)}")
        for r in results[:3]:
            print(f"   - {r.get('trigger_text', '')[:40]} (weight={r.get('weight', 0):.2f})")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
