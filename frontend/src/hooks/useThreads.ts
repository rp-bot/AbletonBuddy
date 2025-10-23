/**
 * React Query hooks for thread management
 */

import {useQuery, useMutation, useQueryClient} from '@tanstack/react-query';
import {fetchThreads, createThread, deleteThread} from '@/api/client';

/**
 * Hook to fetch all threads
 */
export function useThreads ()
{
    return useQuery({
        queryKey: ['threads'],
        queryFn: fetchThreads,
        // Remove constant polling - only refetch when needed
        staleTime: 1000 * 60 * 5, // 5 minutes
        refetchOnWindowFocus: false, // Don't refetch when window regains focus
    });
}

/**
 * Hook to create a new thread
 */
export function useCreateThread ()
{
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: createThread,
        onSuccess: () =>
        {
            // Invalidate threads query to refetch the list
            queryClient.invalidateQueries({queryKey: ['threads']});
        },
    });
}

/**
 * Hook to delete a thread
 */
export function useDeleteThread ()
{
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: deleteThread,
        onSuccess: () =>
        {
            // Invalidate threads query to refetch the list
            queryClient.invalidateQueries({queryKey: ['threads']});
        },
    });
}

