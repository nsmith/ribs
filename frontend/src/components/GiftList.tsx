/**
 * GiftList component displays a list of gift recommendations.
 */

import { GiftRecommendation, QueryContext } from '../types';
import { GiftCard } from './GiftCard';

interface GiftListProps {
  gifts: GiftRecommendation[];
  queryContext: QueryContext;
}

export function GiftList({ gifts, queryContext }: GiftListProps) {
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
        {queryContext.fallback_used ? (
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
          <GiftCard key={gift.id} gift={gift} />
        ))}
      </div>
    </div>
  );
}
