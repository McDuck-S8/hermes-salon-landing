# =============================================================================
# KEY STRENGTH ASSESSMENT — Оценка силы самого ключа (гипотезы)
# =============================================================================

@dataclass
class KeyStrength:
    """Оценка силы ключа (гипотезы) — НЕ аспектов, а самого ключа."""
    key_name: str
    viability: float          # Жизнеспособность: спрос, барьер, маржа
    cohesion: float           # Связанность: насколько аспекты блокируют друг друга
    growth_potential: float   # Потенциал роста: потолок дохода
    key_strength: float       # Итоговая оценка
    
    # Детализация для отладки/объяснения
    viability_details: Dict[str, float] = field(default_factory=dict)
    cohesion_details: Dict[str, Any] = field(default_factory=dict)
    growth_details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "key_name": self.key_name,
            "viability": round(self.viability, 3),
            "cohesion": round(self.cohesion, 3),
            "growth_potential": round(self.growth_potential, 3),
            "key_strength": round(self.key_strength, 3),
            "viability_details": self.viability_details,
            "cohesion_details": self.cohesion_details,
            "growth_details": self.growth_details,
        }


class KeyStrengthEstimator:
    """
    Оценщик силы ключа.
    
    Ключ — это гипотеза, а не сумма аспектов. Оцениваем:
    1. Viability — жизнеспособность ключа (рыночный спрос, барьер входа, маржа)
    2. Cohesion — связанность аспектов (насколько красные блокируют зелёные)
    3. Growth Potential — потолок масштабирования
    
    Key Strength = Viability×0.4 + Cohesion×0.3 + Growth×0.3
    """
    
    # Доменные профили для оценки viability
    DOMAIN_VIABILITY: Dict[str, Dict[str, float]] = {
        "arbitrage": {
            "market_demand": 0.75,    # Рынок арбитража активен
            "entry_barrier": 0.55,    # Средний барьер (прокси, аккаунты, бюджет)
            "margin_potential": 0.70, # Хорошая маржа при успехе
        },
        "ai-ofm": {
            "market_demand": 0.85,    # Рынок взрывной
            "entry_barrier": 0.30,    # Низкий барьер (инструменты доступны)
            "margin_potential": 0.80, # Очень высокая маржа
        },
        "craft": {
            "market_demand": 0.65,    # Нишевый рынок
            "entry_barrier": 0.60,    # Производство требует ресурсов
            "margin_potential": 0.55, # Умеренная маржа
        },
        "default": {
            "market_demand": 0.50,
            "entry_barrier": 0.50,
            "margin_potential": 0.50,
        }
    }
    
    # Оценки потенциала роста по типам ключей (в $/мес максимум)
    KEY_TYPE_GROWTH_CEILING: Dict[str, float] = {
        "pwa betting": 10000,
        "youtube shorts": 5000,
        "tiktok": 8000,
        "cpa content lock": 3000,
        "telegram mini app": 15000,
        "native ads": 12000,
        "push traffic": 8000,
        "email marketing": 5000,
        "seo": 3000,
        "default": 2000,
    }
    
    def __init__(self, domain: str = "arbitrage"):
        self.domain = domain
        self.viability_profile = self.DOMAIN_VIABILITY.get(domain, self.DOMAIN_VIABILITY["default"])
    
    def estimate(self, 
                 key_name: str, 
                 sectors: List[Sector],
                 intersections: List[Intersection] = None) -> KeyStrength:
        """Оценить силу ключа."""
        
        # 1. Viability — жизнеспособность ключа
        viability = self._estimate_viability(key_name)
        
        # 2. Cohesion — связанность аспектов
        cohesion = self._estimate_cohesion(key_name, sectors, intersections)
        
        # 3. Growth Potential — потенциал роста
        growth = self._estimate_growth(key_name)
        
        # Итоговая сила ключа
        key_strength = (viability * 0.4) + (cohesion * 0.3) + (growth * 0.3)
        
        return KeyStrength(
            key_name=key_name,
            viability=viability,
            cohesion=cohesion,
            growth_potential=growth,
            key_strength=key_strength,
            viability_details=self._viability_details,
            cohesion_details=self._cohesion_details,
            growth_details=self._growth_details,
        )
    
    def _estimate_viability(self, key_name: str) -> float:
        """Жизнеспособность: спрос × 0.4 + (1 - барьер) × 0.3 + маржа × 0.3"""
        kl = key_name.lower()
        
        # Базовые значения из профиля домена
        demand = self.viability_profile["market_demand"]
        barrier = self.viability_profile["entry_barrier"]
        margin = self.viability_profile["margin_potential"]
        
        # Корректировки по ключу
        if "pwa" in kl or "progressive web" in kl:
            demand = max(demand, 0.7)
            barrier = min(barrier, 0.6)  # PWA = ниже барьер (нет аппстора)
        if "youtube shorts" in kl or "shorts" in kl:
            demand = max(demand, 0.8)
            barrier = min(barrier, 0.4)  # Shorts = бесплатный трафик
        if "tiktok" in kl:
            demand = max(demand, 0.85)
            barrier = min(barrier, 0.45)
        if "cpa" in kl or "content lock" in kl:
            demand = max(demand, 0.75)
            margin = max(margin, 0.75)
        if "telegram mini app" in kl or "mini app" in kl:
            demand = max(demand, 0.8)
            barrier = min(barrier, 0.5)
            margin = max(margin, 0.8)
        if "india" in kl or "индия" in kl:
            demand = max(demand, 0.8)  # Индия = огромный рынок
            barrier = max(barrier, 0.6)  # Но локальные сложности
        if "betting" in kl or "беттинг" in kl or "gambling" in kl:
            demand = max(demand, 0.85)
            margin = max(margin, 0.85)
            barrier = max(barrier, 0.7)  # Высокие риски блокировок
        
        self._viability_details = {
            "market_demand": demand,
            "entry_barrier": barrier,
            "margin_potential": margin,
            "formula": f"{demand:.2f}×0.4 + {1-barrier:.2f}×0.3 + {margin:.2f}×0.3",
        }
        
        return demand * 0.4 + (1 - barrier) * 0.3 + margin * 0.3
    
    def _estimate_cohesion(self, key_name: str, sectors: List[Sector], 
                           intersections: List[Intersection] = None) -> float:
        """
        Связанность: 1 - (красные аспекты блокирующие зелёные / всего аспектов)
        
        Аспект "блокирует" если он красный И есть зелёный аспект, с которым он в конфликте
        """
        # Считаем красные аспекты
        red_sectors = [s for s in sectors if s.status == "🔴"]
        total_sectors = len(sectors)
        
        if total_sectors == 0:
            self._cohesion_details = {"note": "no sectors"}
            return 0.5
        
        # Если есть intersections, считаем конфликты
        blocking_red = 0
        if intersections:
            green_ids = {s.id for s in sectors if s.status == "🟢"}
            red_ids = {s.id for s in sectors if s.status == "🔴"}
            
            for inter in intersections:
                if inter.intersection_type == "conflict":
                    # Проверяем: зелёный + красный
                    inter_ids = set(inter.circle_ids)
                    if inter_ids & green_ids and inter_ids & red_ids:
                        blocking_red += len(inter_ids & red_ids)
        
        # Если intersections нет, считаем просто долю красных
        if blocking_red == 0:
            blocking_red = len(red_sectors)
        
        cohesion = max(0.0, 1.0 - (blocking_red / total_sectors))
        
        self._cohesion_details = {
            "total_sectors": total_sectors,
            "red_sectors": [s.name for s in red_sectors],
            "blocking_red_count": blocking_red,
            "green_sectors": [s.name for s in sectors if s.status == "🟢"],
            "formula": f"1 - {blocking_red}/{total_sectors} = {cohesion:.2f}",
        }
        
        return cohesion
    
    def _estimate_growth(self, key_name: str) -> float:
        """
        Потенциал роста: логарифм потолка дохода, нормированный к 10k
        """
        kl = key_name.lower()
        
        # Ищем максимальный потолок среди известных типов
        max_ceiling = self.KEY_TYPE_GROWTH_CEILING["default"]
        for ktype, ceiling in self.KEY_TYPE_GROWTH_CEILING.items():
            if ktype in kl:
                max_ceiling = max(max_ceiling, ceiling)
        
        # Корректировки
        if "scale" in kl or "масштаб" in kl:
            max_ceiling *= 2
        if "auto" in kl or "авто" in kl:
            max_ceiling *= 1.5
        
        # Нормируем: log10(ceiling) / log10(10000) = log10(ceiling) / 4
        import math
        growth = min(1.0, math.log10(max(max_ceiling, 100)) / 4.0)
        
        self._growth_details = {
            "max_ceiling_usd": max_ceiling,
            "log10_ceiling": math.log10(max_ceiling),
            "normalized": growth,
            "formula": f"log10({max_ceiling}) / 4 = {growth:.2f}",
        }
        
        return growth
    
    def compare_keys(self, keys: List[str], sectors_map: Dict[str, List[Sector]],
                     intersections_map: Dict[str, List[Intersection]] = None) -> List[KeyStrength]:
        """Сравнить несколько ключей и вернуть отсортированный по силе список."""
        results = []
        for key_name in keys:
            sectors = sectors_map.get(key_name, [])
            intersections = intersections_map.get(key_name, []) if intersections_map else None
            ks = self.estimate(key_name, sectors, intersections)
            results.append(ks)
        
        results.sort(key=lambda x: x.key_strength, reverse=True)
        return results