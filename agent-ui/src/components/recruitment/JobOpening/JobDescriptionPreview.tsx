"use client";

import { useState } from "react";

type JobDescriptionPreviewProps = {
  openingId: string;
  jobPostingId: string;
  draft: string;
  onConfirm: (finalText: string) => void;
};

export function JobDescriptionPreview({
  openingId,
  jobPostingId,
  draft,
  onConfirm,
}: JobDescriptionPreviewProps) {
  const [text, setText] = useState(draft);
  const [editing, setEditing] = useState(false);

  return (
    <div className="rounded-xl border border-border bg-background-secondary p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-primary text-sm">
          Rascunho da Job Description
        </h3>
        <button
          onClick={() => setEditing((v) => !v)}
          className="text-xs text-muted hover:text-primary transition-colors"
        >
          {editing ? "Visualizar" : "Editar"}
        </button>
      </div>

      <div className="flex gap-4 text-xs text-muted">
        <span>
          Abertura: <span className="text-primary font-mono">{openingId}</span>
        </span>
        <span>
          Vaga ATS: <span className="text-primary font-mono">{jobPostingId}</span>
        </span>
      </div>

      {editing ? (
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="w-full min-h-48 rounded-lg border border-border bg-background p-3 text-sm text-primary resize-y focus:outline-none focus:ring-1 focus:ring-brand"
        />
      ) : (
        <div className="rounded-lg bg-background p-3 text-sm text-primary whitespace-pre-wrap max-h-64 overflow-y-auto">
          {text}
        </div>
      )}

      <button
        onClick={() => onConfirm(text)}
        className="w-full rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand/90 transition-colors"
      >
        Confirmar e publicar vaga
      </button>
    </div>
  );
}
