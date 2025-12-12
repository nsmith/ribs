/**
 * Global type declarations for OpenAI Skybridge integration.
 */

interface OpenAIBridge {
  callTool: (toolName: string, args: Record<string, unknown>) => void;
}

declare global {
  interface Window {
    openai?: OpenAIBridge;
  }
}

export {};
