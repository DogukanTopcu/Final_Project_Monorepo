"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { SSEEvent } from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const MAX_RETRIES = 3;

interface UseSSEOptions {
  experimentId: string;
  enabled?: boolean;
}

interface UseSSEReturn {
  events: SSEEvent[];
  lastEvent: SSEEvent | null;
  isConnected: boolean;
  isReconnecting: boolean;
  error: string | null;
}

export function useSSE({ experimentId, enabled = true }: UseSSEOptions): UseSSEReturn {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const retriesRef = useRef(0);
  const sourceRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (!enabled || !experimentId) return;

    const url = `${BASE_URL}/api/experiments/${experimentId}/stream`;
    const source = new EventSource(url);
    sourceRef.current = source;

    source.onopen = () => {
      setIsConnected(true);
      setIsReconnecting(false);
      setError(null);
      retriesRef.current = 0;
    };

    source.onmessage = (event) => {
      try {
        const data: SSEEvent = JSON.parse(event.data);
        setEvents((prev) => [...prev, data]);
        setLastEvent(data);

        if (data.type === "complete" || data.type === "error") {
          source.close();
          setIsConnected(false);
        }
      } catch {
        // skip malformed events
      }
    };

    source.onerror = () => {
      source.close();
      setIsConnected(false);

      if (retriesRef.current < MAX_RETRIES) {
        setIsReconnecting(true);
        const delay = Math.min(1000 * 2 ** retriesRef.current, 10000);
        retriesRef.current += 1;
        setTimeout(connect, delay);
      } else {
        setIsReconnecting(false);
        setError("Connection lost. Max retries reached.");
      }
    };
  }, [experimentId, enabled]);

  useEffect(() => {
    connect();
    return () => {
      sourceRef.current?.close();
    };
  }, [connect]);

  return { events, lastEvent, isConnected, isReconnecting, error };
}
