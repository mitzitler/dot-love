import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const daphneApi = createApi({
  reducerPath: 'daphneApi',
  baseQuery: fetchBaseQuery({ baseUrl: 'https://api.mitzimatthew.love/daphne' }),
  tagTypes: ['Scoreboard', 'DailyScoreboard'],
  endpoints: (builder) => ({
    // Get global scoreboard (all-time high scores)
    getScoreboard: builder.query({
      query: (game) => ({
        url: `/scoreboard?game=${game}`,
        method: 'GET',
      }),
      providesTags: (result, error, game) => [{ type: 'Scoreboard', id: game }],
    }),

    // Get daily scoreboard for a specific date
    getDailyScoreboard: builder.query({
      query: ({ game, date }) => ({
        url: `/scoreboard/daily?game=${game}${date ? `&date=${date}` : ''}`,
        method: 'GET',
      }),
      providesTags: (result, error, { game, date }) => [
        { type: 'DailyScoreboard', id: `${game}-${date || 'today'}` }
      ],
    }),

    // Submit score - invalidates both global and daily scoreboards
    submitScore: builder.mutation({
      query: ({ headers, scoreData }) => ({
        url: '/score',
        method: 'POST',
        body: scoreData,
        headers: headers,
      }),
      invalidatesTags: (result, error, arg) => {
        const tags = [];
        // Always invalidate daily scoreboard when a score is submitted
        tags.push({ type: 'DailyScoreboard', id: `${arg.scoreData.game}-today` });
        // Only invalidate global scoreboard if it was a high score
        if (result?.isHighScore) {
          tags.push({ type: 'Scoreboard', id: arg.scoreData.game });
        }
        return tags;
      },
    }),
  }),
});

export const {
  useGetScoreboardQuery,
  useGetDailyScoreboardQuery,
  useSubmitScoreMutation,
} = daphneApi;
