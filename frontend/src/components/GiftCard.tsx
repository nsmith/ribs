/**
 * GiftCard component displays a single gift recommendation.
 */

import { PriceRange, GiftRecommendation } from '../types';

interface GiftCardProps {
  gift: GiftRecommendation;
}

const PRICE_RANGE_DISPLAY: Record<PriceRange, string> = {
  budget: 'Under $25',
  moderate: '$25 - $75',
  premium: '$75 - $200',
  luxury: 'Over $200',
};

export function GiftCard({ gift }: GiftCardProps) {
  const matchPercent = Math.round(gift.relevance_score * 100);

  return (
    <article className="gift-card">
      <header className="gift-card-header">
        <h3 className="gift-card-name">{gift.name}</h3>
        <span className="gift-card-match">{matchPercent}% match</span>
      </header>

      <p className="gift-card-description">{gift.brief_description}</p>

      <div className="gift-card-meta">
        <span className="gift-card-price">
          {PRICE_RANGE_DISPLAY[gift.price_range]}
        </span>
        <div className="gift-card-categories">
          {gift.categories.map((category) => (
            <span key={category} className="gift-card-category">
              {category}
            </span>
          ))}
        </div>
      </div>
    </article>
  );
}
