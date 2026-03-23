import { useCallback, useState } from "react";
import { AGENTOS_URL } from "@/lib/config";

export function useAgentStream(agentId: string) {
  const [response, setResponse] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = useCallback(
    async (message: string, sessionId: string) => {
      setIsStreaming(true);
      setResponse("");
      setError(null);

      try {
        const res = await fetch(`${AGENTOS_URL}/v1/agents/${agentId}/runs`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message, session_id: sessionId, stream: true }),
        });

        if (!res.ok) {
          throw new Error(`Erro na requisição: ${res.status} ${res.statusText}`);
        }

        const reader = res.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error("Resposta sem corpo para streaming.");
        }

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          setResponse((prev) => prev + decoder.decode(value));
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : "Erro desconhecido";
        setError(message);
      } finally {
        setIsStreaming(false);
      }
    },
    [agentId]
  );

  return { response, isStreaming, error, send };
}
