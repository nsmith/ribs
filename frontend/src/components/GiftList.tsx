/**
 * GiftList component displays a list of gift recommendations.
 */

import { useState } from 'react';
import { GiftRecommendation, QueryContext } from '../types';
import { GiftCard } from './GiftCard';

interface GiftListProps {
  gifts: GiftRecommendation[];
  queryContext: QueryContext;
  recipientDescription?: string;
}

export function GiftList({ gifts, queryContext, recipientDescription }: GiftListProps) {
  const [starredIds, setStarredIds] = useState<Set<string>>(new Set());

  const handleStar = (giftId: string) => {
    setStarredIds((prev) => {
      const next = new Set(prev);
      if (next.has(giftId)) {
        next.delete(giftId);
      } else {
        next.add(giftId);
      }
      return next;
    });
  };

  const handleRefine = () => {
    if (starredIds.size > 0 && recipientDescription && window.openai?.callTool) {
      window.openai.callTool('get_recommendations', {
        recipient_description: recipientDescription,
        starred_gift_ids: Array.from(starredIds),
      });
    }
  };

  if (gifts.length === 0) {
    return (
      <div className="gift-list-empty">
        <p>No recommendations found. Try a different description.</p>
      </div>
    );
  }

  return (
    <div className="gift-list">
      <div className="gift-list-context">
        {queryContext.starred_boost_applied ? (
          <p className="gift-list-refined">
            Results refined based on your starred selections.
          </p>
        ) : queryContext.fallback_used ? (
          <p className="gift-list-fallback">
            Showing popular gift suggestions based on general trends.
          </p>
        ) : (
          <p className="gift-list-stats">
            Found {queryContext.above_threshold} matches from {queryContext.total_searched} gifts searched.
          </p>
        )}
      </div>

      <div className="gift-list-items">
        {gifts.map((gift) => (
          <GiftCard
            key={gift.id}
            gift={gift}
            onStar={handleStar}
            isStarred={starredIds.has(gift.id)}
          />
        ))}
      </div>

      {starredIds.size > 0 && (
        <div className="gift-list-actions">
          <button
            type="button"
            className="gift-list-refine-button"
            onClick={handleRefine}
            aria-label={`Refine recommendations based on ${starredIds.size} starred gift${starredIds.size > 1 ? 's' : ''}`}
          >
            Refine Recommendations ({starredIds.size})
          </button>
        </div>
      )}
    </div>
  );
}
