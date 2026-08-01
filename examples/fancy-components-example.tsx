// examples/fancy-components-example.tsx
// Fancy Components — React микроинтеракции
// GitHub: https://github.com/danielpetho/fancy
// Документация: https://www.fancycomponents.dev/docs/introduction

// === IMAGE TRAIL — след за курсором ===
// Установка: npm install @fancy-components/image-trail
import { ImageTrail } from '@fancy-components/image-trail'

export function HeroWithTrail() {
  return (
    <div className="relative h-screen">
      <ImageTrail
        images={[
          '/img1.jpg',
          '/img2.jpg',
          '/img3.jpg',
          '/img4.jpg',
        ]}
        interval={100} // задержка между появлениями
        fadeDuration={500} // время затухания
      />
      <h1>Наведи курсор</h1>
    </div>
  )
}

// === TEXT HIGHLIGHTER — подсветка текста при наведении ===
import { TextHighlighter } from '@fancy-components/text-highlighter'

export function AnimatedHeading() {
  return (
    <TextHighlighter
      text="Создавайте красивые интерфейсы с AI"
      highlightColor="#3b82f6"
      animationType="wave" // wave | fill | wipe
    />
  )
}

// === GRAVITY — физика текста ===
import { Gravity } from '@fancy-components/gravity'

export function PhysicsText() {
  return (
    <Gravity
      words={['React', 'TypeScript', 'Next.js', 'Tailwind', 'AI']}
      gravity={0.5} // сила гравитации
      bounce={0.7} // упругость
    />
  )
}

// === MARQUEE ALONG SVG PATH ===
import { MarqueePath } from '@fancy-components/marquee-along-svg-path'

export function AnimatedMarquee() {
  return (
    <MarqueePath
      path="M 0 100 Q 250 0 500 100 Q 750 200 1000 100"
      speed={2}
    >
      <span>🚀 АРБИТРАЖ • </span>
      <span>💰 МАРЖА • </span>
      <span>🤖 AI AGENTS • </span>
      <span>📈 СКАЛЬПИНГ • </span>
    </MarqueePath>
  )
}

// === CSS BOX — 3D трансформации ===
import { CSSBox } from '@fancy-components/css-box'

export function FlipCard() {
  return (
    <CSSBox
      rotateX={0}
      rotateY={180}
      perspective={1000}
      transition="transform 0.6s"
    >
      <div className="front">Лицевая сторона</div>
      <div className="back">Обратная сторона</div>
    </CSSBox>
  )
}

// === COMBINED — пример из ARBITRAGE_WORKSHOP ===
export function ArbitrageDashboard() {
  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      {/* Заголовок с анимацией */}
      <TextHighlighter
        text="Hermes Arbitrage Agent"
        highlightColor="#10b981"
        animationType="fill"
      />
      
      {/* Бегущая строка с метриками */}
      <MarqueePath path="M 0 50 Q 500 0 1000 50" speed={1.5}>
        <span>AMR: 95.6% ✅ • </span>
        <span>Cost: $0.22 • </span>
        <span>Revenue: $5.00 • </span>
        <span>Status: GREEN 🟢 • </span>
      </MarqueePath>
      
      {/* Карточки с 3D эффектом */}
      <div className="grid grid-cols-3 gap-4 mt-8">
        {['Agent A', 'Agent B', 'Agent C'].map(name => (
          <CSSBox key={name} rotateX={5} rotateY={5} perspective={800}>
            <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
              <h3>{name}</h3>
              <p>AMR: {name === 'Agent A' ? '95.6%' : name === 'Agent B' ? '31%' : '72%'}</p>
            </div>
          </CSSBox>
        ))}
      </div>
    </div>
  )
}
