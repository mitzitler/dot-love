import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const daphneApi = createApi({
  reducerPath: 'daphneApi',
  baseQuery: fetchBaseQuery({ baseUrl: 'https://api.mitzimatthew.love/daphne' }),
  tagTypes: ['Scoreboard'],
  endpoints: (builder) => ({
    // Get scoreboard - requires game parameter
    getScoreboard: builder.query({
      query: (game) => ({
        url: `/scoreboard?game=${game}`,
        method: 'GET',
      }),
      providesTags: (result, error, game) => [{ type: 'Scoreboard', id: game }],
    }),

    // Submit score - only invalidates if it was a high score
    submitScore: builder.mutation({
      query: ({ headers, scoreData }) => ({
        url: '/score',
        method: 'POST',
        body: scoreData,
        headers: headers,
      }),
      // Conditionally invalidate tags based on response and game
      invalidatesTags: (result, error, arg) => {
        // Only invalidate scoreboard if it was actually a high score
        return result?.isHighScore ? [{ type: 'Scoreboard', id: arg.scoreData.game }] : [];
      },
    }),
  }),
});

export const {
  useGetScoreboardQuery,
  useSubmitScoreMutation,
} = daphneApi;
