/**
 * Type definitions for the gift recommendations widget.
 */

export type PriceRange = 'budget' | 'moderate' | 'premium' | 'luxury';

export interface GiftRecommendation {
  id: string;
  name: string;
  brief_description: string;
  relevance_score: number;
  price_range: PriceRange;
  categories: string[];
}

export interface QueryContext {
  total_searched: number;
  above_threshold: number;
  starred_boost_applied: boolean;
  fallback_used: boolean;
}

export interface RecommendationResponse {
  gifts: GiftRecommendation[];
  query_context: QueryContext;
}

export interface RecommendationRequest {
  recipient_description: string;
  past_gifts?: string[];
  starred_gift_ids?: string[];
  limit?: number;
}

export interface GiftDetailsData {
  id: string;
  name: string;
  brief_description: string;
  full_description: string;
  price_range: PriceRange;
  categories: string[];
  occasions: string[];
  recipient_types: string[];
  purchase_url: string | null;
  has_affiliate_commission: boolean;
}
