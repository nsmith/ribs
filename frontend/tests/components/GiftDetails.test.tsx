/**
 * Component tests for GiftDetails expanded view.
 */

import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

describe('GiftDetails', () => {
  const mockGiftDetails = {
    id: 'gift-123',
    name: 'Leather Journal',
    brief_description: 'Hand-crafted leather journal',
    full_description:
      'A beautiful hand-crafted leather journal with 200 pages of acid-free paper. Perfect for writers, artists, or anyone who appreciates fine craftsmanship.',
    price_range: 'moderate' as const,
    categories: ['stationery', 'handmade'],
    occasions: ['birthday', 'graduation', 'christmas'],
    recipient_types: ['writers', 'professionals', 'students'],
    purchase_url: 'https://example.com/leather-journal',
    has_affiliate_commission: true,
  };

  it('renders gift name as heading', async () => {
    const { GiftDetails } = await import('../../src/components/GiftDetails');
    render(<GiftDetails details={mockGiftDetails} />);

    expect(screen.getByRole('heading', { name: 'Leather Journal' })).toBeInTheDocument();
  });

  it('renders full description', async () => {
    const { GiftDetails } = await import('../../src/components/GiftDetails');
    render(<GiftDetails details={mockGiftDetails} />);

    expect(screen.getByText(/200 pages of acid-free paper/)).toBeInTheDocument();
  });

  it('renders price range', async () => {
    const { GiftDetails } = await import('../../src/components/GiftDetails');
    render(<GiftDetails details={mockGiftDetails} />);

    expect(screen.getByText(/\$25 - \$75/)).toBeInTheDocument();
  });

  it('renders categories as tags', async () => {
    const { GiftDetails } = await import('../../src/components/GiftDetails');
    render(<GiftDetails details={mockGiftDetails} />);

    expect(screen.getByText('stationery')).toBeInTheDocument();
    expect(screen.getByText('handmade')).toBeInTheDocument();
  });

  it('renders occasions when provided', async () => {
    const { GiftDetails } = await import('../../src/components/GiftDetails');
    render(<GiftDetails details={mockGiftDetails} />);

    expect(screen.getByText(/birthday/i)).toBeInTheDocument();
    expect(screen.getByText(/graduation/i)).toBeInTheDocument();
  });

  it('renders recipient types when provided', async () => {
    const { GiftDetails } = await import('../../src/components/GiftDetails');
    render(<GiftDetails details={mockGiftDetails} />);

    // Check for the section header
    expect(screen.getByText('Perfect for')).toBeInTheDocument();
    // Check for items in the list (using getAllByRole to find list items)
    const recipientsList = screen.getByText('Perfect for').closest('div');
    expect(recipientsList).toHaveTextContent('writers');
    expect(recipientsList).toHaveTextContent('professionals');
  });

  it('renders purchase link when URL provided', async () => {
    const { GiftDetails } = await import('../../src/components/GiftDetails');
    render(<GiftDetails details={mockGiftDetails} />);

    const link = screen.getByRole('link', { name: /buy|purchase|shop/i });
    expect(link).toHaveAttribute('href', 'https://example.com/leather-journal');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('shows affiliate disclosure when has_affiliate_commission is true', async () => {
    const { GiftDetails } = await import('../../src/components/GiftDetails');
    render(<GiftDetails details={mockGiftDetails} />);

    expect(screen.getByText(/affiliate/i)).toBeInTheDocument();
  });

  it('does not show affiliate disclosure when has_affiliate_commission is false', async () => {
    const { GiftDetails } = await import('../../src/components/GiftDetails');
    const detailsWithoutAffiliate = {
      ...mockGiftDetails,
      has_affiliate_commission: false,
    };

    render(<GiftDetails details={detailsWithoutAffiliate} />);

    expect(screen.queryByText(/affiliate/i)).not.toBeInTheDocument();
  });

  it('does not render purchase link when URL is null', async () => {
    const { GiftDetails } = await import('../../src/components/GiftDetails');
    const detailsWithoutUrl = {
      ...mockGiftDetails,
      purchase_url: null,
    };

    render(<GiftDetails details={detailsWithoutUrl} />);

    expect(screen.queryByRole('link', { name: /buy|purchase|shop/i })).not.toBeInTheDocument();
  });

  it('does not render occasions section when empty', async () => {
    const { GiftDetails } = await import('../../src/components/GiftDetails');
    const detailsWithoutOccasions = {
      ...mockGiftDetails,
      occasions: [],
    };

    render(<GiftDetails details={detailsWithoutOccasions} />);

    expect(screen.queryByText(/occasions/i)).not.toBeInTheDocument();
  });

  it('does not render recipient types section when empty', async () => {
    const { GiftDetails } = await import('../../src/components/GiftDetails');
    const detailsWithoutRecipients = {
      ...mockGiftDetails,
      recipient_types: [],
    };

    render(<GiftDetails details={detailsWithoutRecipients} />);

    // Should not have a "Perfect for" section header (exact match)
    expect(screen.queryByText('Perfect for')).not.toBeInTheDocument();
  });
});
