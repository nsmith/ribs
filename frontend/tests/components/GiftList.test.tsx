/**
 * Component tests for GiftList.
 */

import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

// GiftList component will be created in implementation phase
// These tests should FAIL until implementation

describe('GiftList', () => {
  const mockGifts = [
    {
      id: 'gift-1',
      name: 'Leather Journal',
      brief_description: 'Hand-crafted leather journal',
      relevance_score: 0.9,
      price_range: 'moderate' as const,
      categories: ['stationery'],
    },
    {
      id: 'gift-2',
      name: 'Woodworking Kit',
      brief_description: 'Beginner woodworking tools',
      relevance_score: 0.85,
      price_range: 'premium' as const,
      categories: ['tools'],
    },
    {
      id: 'gift-3',
      name: 'Vinyl Record Player',
      brief_description: 'Retro-style turntable',
      relevance_score: 0.8,
      price_range: 'premium' as const,
      categories: ['electronics'],
    },
  ];

  const mockQueryContext = {
    total_searched: 100,
    above_threshold: 15,
    starred_boost_applied: false,
    fallback_used: false,
  };

  it('renders list of gift cards', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    render(<GiftList gifts={mockGifts} queryContext={mockQueryContext} />);

    expect(screen.getByText('Leather Journal')).toBeInTheDocument();
    expect(screen.getByText('Woodworking Kit')).toBeInTheDocument();
    expect(screen.getByText('Vinyl Record Player')).toBeInTheDocument();
  });

  it('renders correct number of gifts', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    render(<GiftList gifts={mockGifts} queryContext={mockQueryContext} />);

    // Check all three gifts are rendered
    const giftCards = screen.getAllByRole('article');
    expect(giftCards).toHaveLength(3);
  });

  it('renders empty state when no gifts', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    render(<GiftList gifts={[]} queryContext={mockQueryContext} />);

    expect(screen.getByText(/no recommendations/i)).toBeInTheDocument();
  });

  it('renders query context info', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    render(<GiftList gifts={mockGifts} queryContext={mockQueryContext} />);

    // Should show some context about the search
    expect(screen.getByText(/100|searched|found/i)).toBeInTheDocument();
  });

  it('renders fallback message when fallback used', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    const fallbackContext = { ...mockQueryContext, fallback_used: true };

    render(<GiftList gifts={mockGifts} queryContext={fallbackContext} />);

    expect(screen.getByText(/popular|general|suggestions/i)).toBeInTheDocument();
  });
});
