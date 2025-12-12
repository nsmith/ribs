/**
 * GiftCard component displays a single gift recommendation.
 */

import { PriceRange, GiftRecommendation } from '../types';

interface GiftCardProps {
  gift: GiftRecommendation;
  onStar?: (giftId: string) => void;
  isStarred?: boolean;
}

const PRICE_RANGE_DISPLAY: Record<PriceRange, string> = {
  budget: 'Under $25',
  moderate: '$25 - $75',
  premium: '$75 - $200',
  luxury: 'Over $200',
};

export function GiftCard({ gift, onStar, isStarred = false }: GiftCardProps) {
  const matchPercent = Math.round(gift.relevance_score * 100);

  const handleStarClick = () => {
    if (onStar) {
      onStar(gift.id);
    }
  };

  return (
    <article className="gift-card">
      <header className="gift-card-header">
        <h3 className="gift-card-name">{gift.name}</h3>
        <div className="gift-card-header-actions">
          <span className="gift-card-match">{matchPercent}% match</span>
          {onStar && (
            <button
              type="button"
              className={`gift-card-star ${isStarred ? 'starred' : ''}`}
              onClick={handleStarClick}
              aria-pressed={isStarred}
              aria-label={isStarred ? 'Unstar gift' : 'Star gift'}
            >
              {isStarred ? '\u2605' : '\u2606'}
            </button>
          )}
        </div>
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
