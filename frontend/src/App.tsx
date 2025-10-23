/**
 * Main App component with React Query provider
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppLayout } from "./components/Layout/AppLayout";

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppLayout />
    </QueryClientProvider>
  );
}

export default App;
