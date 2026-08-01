# Chat & Messaging — Critical Rules

## Chat Primitives
```tsx
// ✅ Correct composition
<MessageScroller>
  <Message key={msg.id} user={msg.user}>
    <Bubble>
      <BubbleContent>{msg.content}</BubbleContent>
      <BubbleTimestamp>{formatTime(msg.time)}</BubbleTimestamp>
    </Bubble>
  </Message>
  <MessageScrollerButton>Jump to latest</MessageScrollerButton>
</MessageScroller>

// ❌ Wrong - hand-rolled bubbles
<div className="overflow-y-auto">
  {messages.map(m => (
    <div key={m.id} className="flex gap-2">
      <div className="rounded-lg bg-primary p-3">{m.content}</div>
    </div>
  ))}
</div>
```

## Streaming
- `MessageScroller` owns scroll behavior (anchoring, follow, jump-to-latest)
- Don't write `useStickToBottom` or `ResizeObserver` hooks manually

## Attachments & System
```tsx
// ✅ Correct
<Message>
  <Attachment file={file} />
</Message>
<Marker>System note</Marker>
<Divider /> // or <Separator />

// ❌ Wrong
<Item variant="system">System note</Item>
<Separator className="border-t" />
```

## Never
- Hand-rolled bubble `div`s or raw scroll containers
- Custom streaming hooks
- `Item` cards for chat messages