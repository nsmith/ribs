/**
 * Component tests for GiftList starred state management and refinement.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach } from 'vitest';

// Mock window.openai for refinement tests
const mockCallTool = vi.fn();

beforeEach(() => {
  vi.clearAllMocks();
  (window as any).openai = {
    callTool: mockCallTool,
  };
});

describe('GiftList Starred State Management', () => {
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

  it('renders star buttons for each gift', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    render(
      <GiftList
        gifts={mockGifts}
        queryContext={mockQueryContext}
        recipientDescription="My dad who loves building things"
      />
    );

    const starButtons = screen.getAllByRole('button', { name: /star/i });
    expect(starButtons).toHaveLength(3);
  });

  it('toggles star state when star button clicked', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    render(
      <GiftList
        gifts={mockGifts}
        queryContext={mockQueryContext}
        recipientDescription="My dad who loves building things"
      />
    );

    const starButtons = screen.getAllByRole('button', { name: /star/i });
    const firstStarButton = starButtons[0];

    // Initially not starred
    expect(firstStarButton).toHaveAttribute('aria-pressed', 'false');

    // Click to star
    fireEvent.click(firstStarButton);
    expect(firstStarButton).toHaveAttribute('aria-pressed', 'true');

    // Click again to unstar
    fireEvent.click(firstStarButton);
    expect(firstStarButton).toHaveAttribute('aria-pressed', 'false');
  });

  it('shows refine button when at least one gift is starred', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    render(
      <GiftList
        gifts={mockGifts}
        queryContext={mockQueryContext}
        recipientDescription="My dad who loves building things"
      />
    );

    // Initially no refine button
    expect(screen.queryByRole('button', { name: /refine/i })).not.toBeInTheDocument();

    // Star a gift
    const starButtons = screen.getAllByRole('button', { name: /star/i });
    fireEvent.click(starButtons[0]);

    // Refine button should appear
    expect(screen.getByRole('button', { name: /refine/i })).toBeInTheDocument();
  });

  it('hides refine button when all gifts are unstarred', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    render(
      <GiftList
        gifts={mockGifts}
        queryContext={mockQueryContext}
        recipientDescription="My dad who loves building things"
      />
    );

    const starButtons = screen.getAllByRole('button', { name: /star/i });

    // Star a gift
    fireEvent.click(starButtons[0]);
    expect(screen.getByRole('button', { name: /refine/i })).toBeInTheDocument();

    // Unstar it
    fireEvent.click(starButtons[0]);
    expect(screen.queryByRole('button', { name: /refine/i })).not.toBeInTheDocument();
  });

  it('can star multiple gifts', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    render(
      <GiftList
        gifts={mockGifts}
        queryContext={mockQueryContext}
        recipientDescription="My dad who loves building things"
      />
    );

    const starButtons = screen.getAllByRole('button', { name: /star/i });

    // Star first and third gift
    fireEvent.click(starButtons[0]);
    fireEvent.click(starButtons[2]);

    expect(starButtons[0]).toHaveAttribute('aria-pressed', 'true');
    expect(starButtons[1]).toHaveAttribute('aria-pressed', 'false');
    expect(starButtons[2]).toHaveAttribute('aria-pressed', 'true');
  });
});

describe('GiftList Refine Recommendations', () => {
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
  ];

  const mockQueryContext = {
    total_searched: 100,
    above_threshold: 15,
    starred_boost_applied: false,
    fallback_used: false,
  };

  it('calls window.openai.callTool with starred gift IDs when refine clicked', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    render(
      <GiftList
        gifts={mockGifts}
        queryContext={mockQueryContext}
        recipientDescription="My dad who loves building things"
      />
    );

    const starButtons = screen.getAllByRole('button', { name: /star/i });

    // Star first gift
    fireEvent.click(starButtons[0]);

    // Click refine
    const refineButton = screen.getByRole('button', { name: /refine/i });
    fireEvent.click(refineButton);

    expect(mockCallTool).toHaveBeenCalledWith('get_recommendations', {
      recipient_description: 'My dad who loves building things',
      starred_gift_ids: ['gift-1'],
    });
  });

  it('includes all starred gift IDs in refine call', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    render(
      <GiftList
        gifts={mockGifts}
        queryContext={mockQueryContext}
        recipientDescription="My dad who loves building things"
      />
    );

    const starButtons = screen.getAllByRole('button', { name: /star/i });

    // Star both gifts
    fireEvent.click(starButtons[0]);
    fireEvent.click(starButtons[1]);

    // Click refine
    const refineButton = screen.getByRole('button', { name: /refine/i });
    fireEvent.click(refineButton);

    expect(mockCallTool).toHaveBeenCalledWith('get_recommendations', {
      recipient_description: 'My dad who loves building things',
      starred_gift_ids: ['gift-1', 'gift-2'],
    });
  });

  it('shows starred count on refine button', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    render(
      <GiftList
        gifts={mockGifts}
        queryContext={mockQueryContext}
        recipientDescription="My dad who loves building things"
      />
    );

    const starButtons = screen.getAllByRole('button', { name: /star/i });

    // Star one gift
    fireEvent.click(starButtons[0]);
    expect(screen.getByRole('button', { name: /refine/i })).toHaveTextContent(/1/);

    // Star another
    fireEvent.click(starButtons[1]);
    expect(screen.getByRole('button', { name: /refine/i })).toHaveTextContent(/2/);
  });

  it('shows boost indicator when starred_boost_applied is true', async () => {
    const { GiftList } = await import('../../src/components/GiftList');
    const boostedContext = { ...mockQueryContext, starred_boost_applied: true };

    render(
      <GiftList
        gifts={mockGifts}
        queryContext={boostedContext}
        recipientDescription="My dad who loves building things"
      />
    );

    // Should indicate that results are refined
    expect(screen.getByText(/refined|based on|starred/i)).toBeInTheDocument();
  });
});
