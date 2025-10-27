import React, { useState } from 'react';
import { useGetScoreboardQuery, useGetDailyScoreboardQuery } from '../services/daphne';

function GameScoreboard({ game }) {
  const [view, setView] = useState('global'); // 'global' or 'daily'

  // Fetch global leaderboard with polling every 10 seconds
  const { data: globalScores, isLoading: globalLoading } = useGetScoreboardQuery(game, {
    pollingInterval: 10000, // Refetch every 10 seconds
  });

  // Fetch daily leaderboard with polling every 10 seconds
  const { data: dailyData, isLoading: dailyLoading } = useGetDailyScoreboardQuery({ game }, {
    pollingInterval: 10000, // Refetch every 10 seconds
  });

  const dailyScores = dailyData?.scores || [];
  const isLoading = view === 'global' ? globalLoading : dailyLoading;
  const topScores = view === 'global' ? globalScores : dailyScores;

  return (
    <div style={{
      width: '320px',
      maxWidth: '100%',
      padding: '15px',
      backgroundColor: '#1a1a1a',
      borderRadius: '10px',
      position: 'relative',
      zIndex: 10
    }}>
      {/* Toggle buttons */}
      <div style={{
        display: 'flex',
        gap: '10px',
        marginBottom: '15px',
        justifyContent: 'center'
      }}>
        <button
          onClick={() => setView('global')}
          style={{
            padding: '8px 16px',
            backgroundColor: view === 'global' ? '#ff6600' : '#333333',
            color: '#ffffff',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: view === 'global' ? 'bold' : 'normal',
            transition: 'all 0.2s'
          }}
        >
          All-Time
        </button>
        <button
          onClick={() => setView('daily')}
          style={{
            padding: '8px 16px',
            backgroundColor: view === 'daily' ? '#ff6600' : '#333333',
            color: '#ffffff',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: view === 'daily' ? 'bold' : 'normal',
            transition: 'all 0.2s'
          }}
        >
          Today
        </button>
      </div>

      <h2 style={{
        color: '#ffffff',
        marginTop: 0,
        marginBottom: '20px',
        fontSize: '24px',
        textAlign: 'center'
      }}>
        {view === 'global' ? 'All-Time Top 5' : "Today's Top 5"}
      </h2>

      {isLoading ? (
        <p style={{ color: '#aaaaaa', textAlign: 'center' }}>Loading...</p>
      ) : !topScores || topScores.length === 0 ? (
        <p style={{ color: '#aaaaaa', textAlign: 'center' }}>No scores yet!</p>
      ) : (
        <ol style={{
          color: '#ffffff',
          padding: '0 0 0 25px',
          margin: 0,
          listStylePosition: 'outside',
          listStyle: 'decimal'
        }}>
          {topScores.map((entry, index) => (
            <li key={index} style={{
              marginBottom: '15px',
              fontSize: '16px',
              paddingLeft: '5px',
              color: '#ffffff',
              display: 'list-item'
            }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '10px'
              }}>
                <span style={{
                  color: '#ffffff',
                  flexGrow: 1,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  fontSize: '16px'
                }}>
                  {entry.userName}
                </span>
                <span style={{
                  color: '#ff6600',
                  fontWeight: 'bold',
                  flexShrink: 0,
                  minWidth: '40px',
                  textAlign: 'right',
                  fontSize: '16px'
                }}>
                  {entry.score}
                </span>
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

export default GameScoreboard;
