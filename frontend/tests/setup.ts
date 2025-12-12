import '@testing-library/jest-dom';

// Mock window.openai for testing
declare global {
  interface Window {
    openai?: {
      toolOutput?: unknown;
      widgetState?: unknown;
      setWidgetState?: (state: unknown) => void;
      callTool?: (name: string, args: unknown) => Promise<unknown>;
      sendFollowUpMessage?: (message: string) => void;
      theme?: 'light' | 'dark';
      displayMode?: string;
      locale?: string;
    };
  }
}

// Default mock implementation
window.openai = {
  toolOutput: null,
  widgetState: null,
  setWidgetState: () => {},
  callTool: async () => ({}),
  sendFollowUpMessage: () => {},
  theme: 'light',
  displayMode: 'default',
  locale: 'en-US',
};
