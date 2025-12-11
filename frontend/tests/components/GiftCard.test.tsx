/**
 * Component tests for GiftCard.
 */

import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

// GiftCard component will be created in implementation phase
// These tests should FAIL until implementation

describe('GiftCard', () => {
  const mockGift = {
    id: 'test-id-123',
    name: 'Leather Journal',
    brief_description: 'Hand-crafted leather journal for notes',
    relevance_score: 0.85,
    price_range: 'moderate' as const,
    categories: ['stationery', 'handmade'],
  };

  it('renders gift name', async () => {
    // Import dynamically to allow test to fail if component doesn't exist
    const { GiftCard } = await import('../../src/components/GiftCard');
    render(<GiftCard gift={mockGift} />);

    expect(screen.getByText('Leather Journal')).toBeInTheDocument();
  });

  it('renders brief description', async () => {
    const { GiftCard } = await import('../../src/components/GiftCard');
    render(<GiftCard gift={mockGift} />);

    expect(screen.getByText(/Hand-crafted leather journal/)).toBeInTheDocument();
  });

  it('renders price range', async () => {
    const { GiftCard } = await import('../../src/components/GiftCard');
    render(<GiftCard gift={mockGift} />);

    expect(screen.getByText(/\$25 - \$75/)).toBeInTheDocument();
  });

  it('renders categories', async () => {
    const { GiftCard } = await import('../../src/components/GiftCard');
    render(<GiftCard gift={mockGift} />);

    expect(screen.getByText(/stationery/)).toBeInTheDocument();
  });

  it('renders relevance score indicator', async () => {
    const { GiftCard } = await import('../../src/components/GiftCard');
    render(<GiftCard gift={mockGift} />);

    // Should show some form of relevance indicator (85% match, etc.)
    expect(screen.getByText(/85%|0\.85|match/i)).toBeInTheDocument();
  });
});
