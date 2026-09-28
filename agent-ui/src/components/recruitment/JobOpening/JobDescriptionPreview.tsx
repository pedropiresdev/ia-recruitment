'use client'

import { useState } from 'react'

type JobDescriptionPreviewProps = {
  openingId: string
  jobPostingId: string
  draft: string
  onConfirm: (finalText: string) => void
}

export function JobDescriptionPreview({
  openingId,
  jobPostingId,
  draft,
  onConfirm
}: JobDescriptionPreviewProps) {
  const [text, setText] = useState(draft)
  const [editing, setEditing] = useState(false)

  return (
    <div className="space-y-3 rounded-xl border border-border bg-background-secondary p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-primary">
          Rascunho da Job Description
        </h3>
        <button
          onClick={() => setEditing((v) => !v)}
          className="text-xs text-muted transition-colors hover:text-primary"
        >
          {editing ? 'Visualizar' : 'Editar'}
        </button>
      </div>

      <div className="flex gap-4 text-xs text-muted">
        <span>
          Abertura: <span className="font-mono text-primary">{openingId}</span>
        </span>
        <span>
          Vaga ATS:{' '}
          <span className="font-mono text-primary">{jobPostingId}</span>
        </span>
      </div>

      {editing ? (
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="min-h-48 w-full resize-y rounded-lg border border-border bg-background p-3 text-sm text-primary focus:outline-none focus:ring-1 focus:ring-brand"
        />
      ) : (
        <div className="max-h-64 overflow-y-auto whitespace-pre-wrap rounded-lg bg-background p-3 text-sm text-primary">
          {text}
        </div>
      )}

      <button
        onClick={() => onConfirm(text)}
        className="w-full rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-brand/90"
      >
        Confirmar e publicar vaga
      </button>
    </div>
  )
}
