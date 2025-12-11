/**
 * GiftDetails component displays expanded gift information.
 */

import { GiftDetailsData, PriceRange } from '../types';

interface GiftDetailsProps {
  details: GiftDetailsData;
}

const PRICE_RANGE_DISPLAY: Record<PriceRange, string> = {
  budget: 'Under $25',
  moderate: '$25 - $75',
  premium: '$75 - $200',
  luxury: 'Over $200',
};

export function GiftDetails({ details }: GiftDetailsProps) {
  return (
    <article className="gift-details">
      <header className="gift-details-header">
        <h2 className="gift-details-name">{details.name}</h2>
        <span className="gift-details-price">
          {PRICE_RANGE_DISPLAY[details.price_range]}
        </span>
      </header>

      <p className="gift-details-description">{details.full_description}</p>

      <div className="gift-details-categories">
        {details.categories.map((category) => (
          <span key={category} className="gift-details-category">
            {category}
          </span>
        ))}
      </div>

      {details.occasions.length > 0 && (
        <div className="gift-details-occasions">
          <h3 className="gift-details-section-title">Great for occasions</h3>
          <ul className="gift-details-list">
            {details.occasions.map((occasion) => (
              <li key={occasion}>{occasion}</li>
            ))}
          </ul>
        </div>
      )}

      {details.recipient_types.length > 0 && (
        <div className="gift-details-recipients">
          <h3 className="gift-details-section-title">Perfect for</h3>
          <ul className="gift-details-list">
            {details.recipient_types.map((recipient) => (
              <li key={recipient}>{recipient}</li>
            ))}
          </ul>
        </div>
      )}

      {details.purchase_url && (
        <div className="gift-details-purchase">
          <a
            href={details.purchase_url}
            target="_blank"
            rel="noopener noreferrer"
            className="gift-details-buy-link"
          >
            Buy this gift
          </a>
          {details.has_affiliate_commission && (
            <p className="gift-details-affiliate-disclosure">
              This is an affiliate link. We may earn a commission on purchases.
            </p>
          )}
        </div>
      )}
    </article>
  );
}
