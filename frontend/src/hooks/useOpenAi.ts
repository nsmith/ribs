/**
 * Hook for integrating with OpenAI Apps SDK window.openai globals.
 *
 * Provides typed access to the skybridge runtime APIs for ChatGPT widget integration.
 */

import { useCallback, useEffect, useState } from 'react';

/**
 * Gift data structure from tool output.
 */
export interface GiftData {
  id: string;
  name: string;
  brief_description: string;
  relevance_score: number;
  price_range: 'budget' | 'moderate' | 'premium' | 'luxury';
  categories: string[];
}

/**
 * Extended gift data from _meta.
 */
export interface GiftMetaData extends GiftData {
  full_description: string;
  occasions?: string[];
  purchasing_guidance?: string;
}

/**
 * Query context from tool output.
 */
export interface QueryContext {
  total_searched: number;
  above_threshold: number;
  starred_boost_applied: boolean;
  fallback_used: boolean;
}

/**
 * Structured content from get_recommendations tool.
 */
export interface RecommendationOutput {
  gifts: GiftData[];
  query_context: QueryContext;
  error?: string;
}

/**
 * Full tool output including _meta.
 */
export interface ToolOutput {
  structuredContent: RecommendationOutput;
  content: string;
  _meta?: {
    gifts?: GiftMetaData[];
    'openai/outputTemplate'?: string;
  };
}

/**
 * Widget state persisted across renders.
 */
export interface WidgetState {
  starredGiftIds: string[];
  recipientDescription?: string;
}

/**
 * OpenAI globals type definition.
 */
interface OpenAIGlobals {
  toolOutput?: ToolOutput;
  widgetState?: WidgetState;
  setWidgetState?: (state: WidgetState) => void;
  callTool?: (name: string, args: Record<string, unknown>) => Promise<unknown>;
  sendFollowUpMessage?: (message: string) => void;
  theme?: 'light' | 'dark';
  displayMode?: string;
  locale?: string;
}

declare global {
  interface Window {
    openai?: OpenAIGlobals;
  }
}

/**
 * Hook return type.
 */
interface UseOpenAiReturn {
  toolOutput: ToolOutput | null;
  widgetState: WidgetState;
  setWidgetState: (state: WidgetState) => void;
  callTool: (name: string, args: Record<string, unknown>) => Promise<unknown>;
  sendFollowUpMessage: (message: string) => void;
  theme: 'light' | 'dark';
  isReady: boolean;
}

/**
 * Default widget state.
 */
const DEFAULT_WIDGET_STATE: WidgetState = {
  starredGiftIds: [],
};

/**
 * Hook for accessing OpenAI Apps SDK globals.
 *
 * Provides typed access to tool output, widget state, and API methods.
 */
export function useOpenAi(): UseOpenAiReturn {
  const [isReady, setIsReady] = useState(false);
  const [toolOutput, setToolOutput] = useState<ToolOutput | null>(null);
  const [widgetState, setWidgetStateLocal] = useState<WidgetState>(DEFAULT_WIDGET_STATE);

  // Initialize from window.openai
  useEffect(() => {
    const checkReady = () => {
      if (window.openai) {
        setIsReady(true);

        // Load initial tool output
        if (window.openai.toolOutput) {
          setToolOutput(window.openai.toolOutput);
        }

        // Load initial widget state
        if (window.openai.widgetState) {
          setWidgetStateLocal(window.openai.widgetState);
        }
      }
    };

    // Check immediately
    checkReady();

    // Also check after a short delay (skybridge may inject later)
    const timeout = setTimeout(checkReady, 100);

    return () => clearTimeout(timeout);
  }, []);

  // Sync widget state with skybridge
  const setWidgetState = useCallback((state: WidgetState) => {
    setWidgetStateLocal(state);
    window.openai?.setWidgetState?.(state);
  }, []);

  // Call MCP tool
  const callTool = useCallback(
    async (name: string, args: Record<string, unknown>): Promise<unknown> => {
      if (!window.openai?.callTool) {
        console.warn('window.openai.callTool not available');
        return null;
      }
      return window.openai.callTool(name, args);
    },
    []
  );

  // Send follow-up message
  const sendFollowUpMessage = useCallback((message: string) => {
    window.openai?.sendFollowUpMessage?.(message);
  }, []);

  // Get theme
  const theme = window.openai?.theme ?? 'light';

  return {
    toolOutput,
    widgetState,
    setWidgetState,
    callTool,
    sendFollowUpMessage,
    theme,
    isReady,
  };
}
