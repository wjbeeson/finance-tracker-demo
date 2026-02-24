import { render, screen } from '@testing-library/react';
import { ThemeProvider } from './context/ThemeContext';
import App from './App';

test('renders Acme Expenses heading', () => {
  render(
    <ThemeProvider>
      <App />
    </ThemeProvider>
  );
  const headingElement = screen.getByRole('heading', { name: /Acme Expenses/i });
  expect(headingElement).toBeInTheDocument();
});
