// examples/nuqs-example.tsx
// nuqs — type-safe URL state для React
// Установка: npm install nuqs

import { useQueryState, parseAsString, parseAsInteger, parseAsBoolean } from 'nuqs'

// === ФИЛЬТРЫ ДЛЯ E-COMMERCE ===
export function ProductFilters() {
  // Каждый параметр автоматически синхронизируется с URL
  const [search, setSearch] = useQueryState('q', parseAsString.withDefault(''))
  const [category, setCategory] = useQueryState('cat', parseAsString.withDefault('all'))
  const [minPrice, setMinPrice] = useQueryState('min', parseAsInteger.withDefault(0))
  const [maxPrice, setMaxPrice] = useQueryState('max', parseAsInteger.withDefault(10000))
  const [inStock, setInStock] = useQueryState('stock', parseAsBoolean.withDefault(false))

  // URL автоматически меняется: ?q=nike&cat=shoes&min=1000&stock=true

  return (
    <div>
      <input
        placeholder="Поиск..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />
      
      <select value={category} onChange={e => setCategory(e.target.value)}>
        <option value="all">Все категории</option>
        <option value="shoes">Обувь</option>
        <option value="clothes">Одежда</option>
      </select>

      <input
        type="number"
        placeholder="Мин. цена"
        value={minPrice}
        onChange={e => setMinPrice(Number(e.target.value))}
      />

      <label>
        <input
          type="checkbox"
          checked={inStock}
          onChange={e => setInStock(e.target.checked)}
        />
        В наличии
      </label>
    </div>
  )
}

// === ПАГИНАЦИЯ ===
export function Pagination() {
  const [page, setPage] = useQueryState('page', parseAsInteger.withDefault(1))
  // URL: ?page=2

  return (
    <div>
      <button onClick={() => setPage(p => Math.max(1, p - 1))}>← Назад</button>
      <span>Страница {page}</span>
      <button onClick={() => setPage(p => p + 1)}>Вперёд →</button>
    </div>
  )
}

// === СОРТИРОВКА ===
export function SortSelect() {
  const [sort, setSort] = useQueryState('sort', parseAsString.withDefault('popular'))
  // URL: ?sort=price_asc

  return (
    <select value={sort} onChange={e => setSort(e.target.value)}>
      <option value="popular">По популярности</option>
      <option value="price_asc">Цена ↑</option>
      <option value="price_desc">Цена ↓</option>
      <option value="newest">Новинки</option>
    </select>
  )
}

// === НЕСКОЛЬКО ПАРАМЕТРОВ ОДНОВРЕМЕННО ===
import { useQueryStates } from 'nuqs'

export function MultiFilter() {
  const [filters, setFilters] = useQueryStates({
    q: parseAsString.withDefault(''),
    cat: parseAsString.withDefault('all'),
    page: parseAsInteger.withDefault(1),
  })

  // Установить несколько параметров за раз
  const resetFilters = () => setFilters({ q: '', cat: 'all', page: 1 })

  return (
    <div>
      <input value={filters.q} onChange={e => setFilters({ q: e.target.value, page: 1 })} />
      <button onClick={resetFilters}>Сбросить фильтры</button>
    </div>
  )
}
