/**
 * React Query hooks for message management
 */

import {useQuery, useQueryClient} from '@tanstack/react-query';
import {fetchThread} from '@/api/client';

/**
 * Hook to fetch messages for a specific thread
 */
export function useMessages (threadId: string | null)
{
    return useQuery({
        queryKey: ['thread', threadId],
        queryFn: () => (threadId ? fetchThread(threadId) : null),
        enabled: !!threadId, // Only fetch if threadId is provided
        refetchOnWindowFocus: false, // Don't refetch when window regains focus
    });
}

/**
 * Hook to get query client for manual cache updates
 */
export function useInvalidateMessages ()
{
    const queryClient = useQueryClient();

    return (threadId: string) =>
    {
        queryClient.invalidateQueries({queryKey: ['thread', threadId]});
    };
}

