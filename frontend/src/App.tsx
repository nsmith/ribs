/**
 * Main widget entry point for Gift Recommendations.
 *
 * Integrates with OpenAI Apps SDK skybridge runtime.
 */

import { useOpenAi } from './hooks/useOpenAi';
import { GiftList } from './components/GiftList';
import { GiftRecommendation, QueryContext } from './types';

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
  if (toolOutput.structuredContent?.error) {
    return (
      <div className={`app ${theme}`}>
        <p className="error">{toolOutput.content}</p>
      </div>
    );
  }

  // Extract data from tool output
  const gifts: GiftRecommendation[] = toolOutput.structuredContent?.gifts || [];
  const queryContext: QueryContext = toolOutput.structuredContent?.query_context || {
    total_searched: 0,
    above_threshold: 0,
    starred_boost_applied: false,
    fallback_used: false,
  };

  // Render gift list
  return (
    <div className={`app ${theme}`}>
      <GiftList gifts={gifts} queryContext={queryContext} />
    </div>
  );
}

export default App;
