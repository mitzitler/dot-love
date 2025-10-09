import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const daphneApi = createApi({
  reducerPath: 'daphneApi',
  baseQuery: fetchBaseQuery({ baseUrl: 'https://api.mitzimatthew.love/daphne' }),
  tagTypes: ['Scoreboard'],
  endpoints: (builder) => ({
    // Get scoreboard
    getScoreboard: builder.query({
      query: () => ({
        url: '/scoreboard',
        method: 'GET',
      }),
      providesTags: ['Scoreboard'],
    }),

    // Submit score - only invalidates if it was a high score
    submitScore: builder.mutation({
      query: ({ headers, scoreData }) => ({
        url: '/score',
        method: 'POST',
        body: scoreData,
        headers: headers,
      }),
      // Conditionally invalidate tags based on response
      invalidatesTags: (result, error, arg) => {
        // Only invalidate scoreboard if it was actually a high score
        return result?.isHighScore ? ['Scoreboard'] : [];
      },
    }),
  }),
});

export const {
  useGetScoreboardQuery,
  useSubmitScoreMutation,
} = daphneApi;
