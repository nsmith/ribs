/**
 * Component tests for GiftCard star toggle functionality.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

describe('GiftCard Star Toggle', () => {
  const mockGift = {
    id: 'test-id-123',
    name: 'Leather Journal',
    brief_description: 'Hand-crafted leather journal for notes',
    relevance_score: 0.85,
    price_range: 'moderate' as const,
    categories: ['stationery', 'handmade'],
  };

  it('renders star button', async () => {
    const { GiftCard } = await import('../../src/components/GiftCard');
    render(<GiftCard gift={mockGift} onStar={() => {}} isStarred={false} />);

    const starButton = screen.getByRole('button', { name: /star/i });
    expect(starButton).toBeInTheDocument();
  });

  it('calls onStar callback when star clicked', async () => {
    const { GiftCard } = await import('../../src/components/GiftCard');
    const onStar = vi.fn();

    render(<GiftCard gift={mockGift} onStar={onStar} isStarred={false} />);

    const starButton = screen.getByRole('button', { name: /star/i });
    fireEvent.click(starButton);

    expect(onStar).toHaveBeenCalledWith('test-id-123');
  });

  it('shows filled star when isStarred is true', async () => {
    const { GiftCard } = await import('../../src/components/GiftCard');
    render(<GiftCard gift={mockGift} onStar={() => {}} isStarred={true} />);

    const starButton = screen.getByRole('button', { name: /star/i });
    expect(starButton).toHaveAttribute('aria-pressed', 'true');
  });

  it('shows empty star when isStarred is false', async () => {
    const { GiftCard } = await import('../../src/components/GiftCard');
    render(<GiftCard gift={mockGift} onStar={() => {}} isStarred={false} />);

    const starButton = screen.getByRole('button', { name: /star/i });
    expect(starButton).toHaveAttribute('aria-pressed', 'false');
  });
});
