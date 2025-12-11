/**
 * Main widget entry point for Gift Recommendations.
 *
 * Integrates with OpenAI Apps SDK skybridge runtime.
 */

import { useOpenAi } from './hooks/useOpenAi';

function App() {
  const { toolOutput, isReady, theme } = useOpenAi();

  // Show loading state while waiting for skybridge
  if (!isReady) {
    return (
      <div className={`app ${theme}`}>
        <p>Loading...</p>
      </div>
    );
  }

  // Show message if no tool output yet
  if (!toolOutput) {
    return (
      <div className={`app ${theme}`}>
        <p>Waiting for gift recommendations...</p>
      </div>
    );
  }

  // Handle error state
  if (toolOutput.structuredContent.error) {
    return (
      <div className={`app ${theme}`}>
        <p className="error">{toolOutput.content}</p>
      </div>
    );
  }

  // Render gift list (placeholder - will be implemented in US1)
  return (
    <div className={`app ${theme}`}>
      <p>Gift recommendations loaded: {toolOutput.structuredContent.gifts.length} items</p>
      {/* GiftList component will be added in User Story 1 */}
    </div>
  );
}

export default App;
