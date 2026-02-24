import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Acme Expenses heading', () => {
  render(<App />);
  const headingElement = screen.getByRole('heading', { name: /Acme Expenses/i });
  expect(headingElement).toBeInTheDocument();
});
