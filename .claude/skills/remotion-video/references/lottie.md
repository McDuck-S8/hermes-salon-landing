# Lottie Animations Reference

Reference: https://www.remotion.dev/docs/lottie

## Install
```bash
npx remotion add @remotion/lottie
```

## Basic Usage
```tsx
import { Lottie } from "@remotion/lottie";

const animationData = await fetch("/animation.json").then(r => r.json());

<Lottie
  animationData={animationData}
  style={{ width: 500, height: 500 }}
/>
```

## With Delay/Continue Render
```tsx
import { delayRender, continueRender } from "remotion";

const LottieWrapper = () => {
  const handleRef = useRef(null);

  useEffect(() => {
    if (!handleRef.current) return;
    delayRender(handleRef.current);
    handleRef.current.addEventListener("load", () => {
      continueRender(handleRef.current);
    });
  }, []);

  return (
    <Lottie
      ref={handleRef}
      animationData={animationData}
      renderer="svg"
    />
  );
};
```

## Props
| Prop | Type | Description |
|------|------|-------------|
| `animationData` | `object` | Parsed Lottie JSON |
| `style` | `CSSProperties` | Container size |
| `renderer` | `"svg" \| "canvas" \| "html"` | Default: "svg" |
| `loop` | `boolean` | Default: true |
| `speed` | `number` | Default: 1 |

## Getting Lottie Files
- [LottieFiles.com](https://lottiefiles.com) - free animations
- Export from After Effects with Bodymovin plugin
- Create in Haiku Animator, Spirit

## Best Practices
- Use `delayRender`/`continueRender` for async loading
- Prefer SVG renderer for crisp scaling
- Keep file size < 500KB for web
- Test with `npx remotion still` first