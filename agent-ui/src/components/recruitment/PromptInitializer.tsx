"use client";

import { useEffect } from "react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { useStore } from "@/store";

/**
 * Lê o query param `?prompt=` da URL (enviado pelo painel de processos),
 * injeta o texto no textarea do chat e limpa o param da URL.
 */
export function PromptInitializer() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const { chatInputRef } = useStore();

  useEffect(() => {
    const prompt = searchParams.get("prompt");
    if (!prompt || !chatInputRef?.current) return;

    // Injeta o valor no textarea controlado pelo React
    const nativeSetter = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype,
      "value"
    )?.set;
    nativeSetter?.call(chatInputRef.current, prompt);
    chatInputRef.current.dispatchEvent(new Event("input", { bubbles: true }));
    chatInputRef.current.focus();

    // Remove o param da URL sem adicionar ao histórico
    const params = new URLSearchParams(searchParams.toString());
    params.delete("prompt");
    const newUrl = params.size > 0 ? `${pathname}?${params}` : pathname;
    router.replace(newUrl);
  }, [searchParams, chatInputRef, pathname, router]);

  return null;
}
