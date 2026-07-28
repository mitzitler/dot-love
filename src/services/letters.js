import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const lettersApi = createApi({
  reducerPath: 'lettersApi',
  baseQuery: fetchBaseQuery({ baseUrl: 'https://api.mitzimatthew.love/miatun' }),
  tagTypes: ['Letters'],
  endpoints: (builder) => ({
    // Get all letters
    getAllLetters: builder.query({
      query: (apiKey) => ({
        url: '/letter',
        method: 'GET',
        headers: { 'Internal-Api-Key': apiKey },
      }),
      providesTags: ['Letters'],
    }),

    // Re-gather delivered gifts from claims/items/users and upsert letters
    syncLetters: builder.mutation({
      query: (apiKey) => ({
        url: '/sync',
        method: 'POST',
        headers: { 'Internal-Api-Key': apiKey },
      }),
      invalidatesTags: ['Letters'],
    }),

    // Manually create a letter not tied to a registry claim
    createLetter: builder.mutation({
      query: ({ apiKey, letterData }) => ({
        url: '/letter',
        method: 'POST',
        body: letterData,
        headers: { 'Internal-Api-Key': apiKey },
      }),
      invalidatesTags: ['Letters'],
    }),

    // Edit a letter's body/status/contact fields
    updateLetter: builder.mutation({
      query: ({ apiKey, letterId, updates }) => ({
        url: '/letter',
        method: 'PATCH',
        body: { letter_id: letterId, ...updates },
        headers: { 'Internal-Api-Key': apiKey },
      }),
      invalidatesTags: ['Letters'],
    }),

    // Delete a letter
    deleteLetter: builder.mutation({
      query: ({ apiKey, letterId }) => ({
        url: '/letter',
        method: 'DELETE',
        body: { letter_id: letterId },
        headers: { 'Internal-Api-Key': apiKey },
      }),
      invalidatesTags: ['Letters'],
    }),

    // Split a two-person letter into two individual letters
    disjoinLetterPair: builder.mutation({
      query: ({ apiKey, letterId }) => ({
        url: '/disjoin',
        method: 'POST',
        body: { letter_id: letterId },
        headers: { 'Internal-Api-Key': apiKey },
      }),
      invalidatesTags: ['Letters'],
    }),
  }),
});

export const {
  useLazyGetAllLettersQuery,
  useSyncLettersMutation,
  useCreateLetterMutation,
  useUpdateLetterMutation,
  useDeleteLetterMutation,
  useDisjoinLetterPairMutation,
} = lettersApi;
