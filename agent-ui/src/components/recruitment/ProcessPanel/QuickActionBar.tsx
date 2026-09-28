'use client'

import type { QuickAction } from '@/types/recruitment'

type QuickActionBarProps = {
  actions: QuickAction[]
  onAction: (prompt: string) => void
}

export function QuickActionBar({ actions, onAction }: QuickActionBarProps) {
  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {actions.map((action) => (
        <button
          key={action.label}
          onClick={() => onAction(action.prompt)}
          className="rounded-full border border-border px-3 py-1 text-sm text-primary transition-colors hover:bg-accent"
        >
          {action.label}
        </button>
      ))}
    </div>
  )
}
